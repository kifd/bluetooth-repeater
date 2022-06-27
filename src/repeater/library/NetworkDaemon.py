
# pip modules
import websockets
import rpyc
from rpyc.lib.compat import TimeoutError as AsyncResultTimeout

# built-ins
import logging
import re
import os, signal
import asyncio

# this app
from .DataClass import *
from .Exceptions import *



class NetworkDaemon:
    """
    Simple daemon that acts as an interface between:
        a websocket connection from my plasmoid temperature widget and
        the rpyc server that's busy receiving the bluetooth data
        
    TODO: when this gets moved to a separate program, should this query the influx db instead?
    TODO: make the parser device agnostic - it currently is pretty much just for temperature devices
    """

    
    def __init__(self, cfg):
        self.logger = logging.getLogger(__name__)
        self.cfg = cfg
        
        # NOTE: if you have more decoders than just TBs, add them here too
        self.macs = list(set(k.lower() for k in self.cfg.thermobeacons.__dict__))
        

    async def parse(self, websocket, path):
        message = await websocket.recv()
        self.logger.debug(f"Received: {message!r}")

        mac = message.strip().upper()
        if mac == "LIST":
            
            # TODO: should it reply with the ones it currently has in memory instead of all the ones from the config?
            reply = ",".join(self.macs)
            
        
        elif re.match("[0-9A-F]{2}([-:]?)[0-9A-F]{2}(\\1[0-9A-F]{2}){4}$", mac):
            
            try:
                beacon = self.rpyc.root.question(mac)
                
            except (OSError, ConnectionError, EOFError, AsyncResultTimeout) as ex:
                self.logger.error(f"Could not reach the network endpoint while questioning: {ex}.")
                os.kill(os.getpid(), signal.SIGINT)
                
            except Exception as ex:
                self.logger.error(f"Generic Exception (parse): {str(ex)}")
                os.kill(os.getpid(), signal.SIGINT)
                
            else:
                if beacon is not None:
                    try:
                        if beacon.temperature != 0.0 and beacon.humidity != 0.0:
                            reply = f"{beacon.temperature},{beacon.humidity},{beacon.rssi},{beacon.battery_level},{beacon.counter}"
                        else:
                            reply = f"Error: Beacon not yet ready: {beacon}"
                            
                    except AttributeError as ex:
                        reply = f"Error: Wrong key for beacon: {beacon} ({str(ex)})"
                        
                else:
                    reply = f"Error: {message} is not broadcasting."
            
        else:
            reply = f"Error: {message} is not a valid MAC address."
            
        
        await websocket.send(reply)
        self.logger.debug(f"Sent: {reply!r}")
        



    # https://stackoverflow.com/questions/58123599/starting-websocket-server-in-different-thread-event-loop
    def start(self):
        try:
            self.logger.debug(f"Connecting to RPC server")
            self.rpyc = rpyc.connect(self.cfg.network.address, self.cfg.network.rpyc_port)
            
            self.logger.debug(f"Starting WebSocket listener")
            
            loop = asyncio.new_event_loop()
            server = websockets.serve(self.parse, "0.0.0.0", self.cfg.network.ws_daemon, loop=loop)
            loop.run_until_complete(server)
            loop.run_forever()
            
        except (OSError, ConnectionError, EOFError, AsyncResultTimeout) as ex:
            self.logger.error(f"Could not reach the network endpoint while connecting: {ex}.")
            os.kill(os.getpid(), signal.SIGINT)
            
        except Exception as ex:
            self.logger.error(f"Generic Exception (start): {str(ex)}")
            os.kill(os.getpid(), signal.SIGINT)
            
            
            
    def stop(self):
        raise Exception(f"Closing NetworkDaemon thread by forcing an exception isn't good practice.")
        
        
