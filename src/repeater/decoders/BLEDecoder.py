# pip modules

# built-ins
import logging
import asyncio
import os, signal
import queue as Queue

# this app
from ..library.DataClass import *
from ..library.Exceptions import *

from .ThermoBeacon import ThermoBeacon

from ..output.Influx import *




class BLEDecoder:

    running = False
    #decoded = {}

    def __init__(self, incoming, cfg, decoded : dict):
        self.logger = logging.getLogger(__name__)
        self.incoming = incoming
        self.cfg = cfg
        self.decoded = decoded
        
        self.output = Influx(cfg.influx)
        
        
        # NOTE: if you have more decoders than just TBs, add them here too
        self.mac_tbs = set(k.lower() for k in self.cfg.thermobeacons.__dict__)
        
        
        
        
    async def run(self):
       
        sleep_timer = 1
        
        while self.running:
            
            # sleep to avoid killing the cpu waiting for events
            await asyncio.sleep(sleep_timer)
            
            try:
                beacon = self.incoming.get(False)
                if beacon:
                    
                    # load the right type of class
                    if beacon.mac_address.lower() in self.mac_tbs:
                        self.logger.debug(f"Got thermobeacon BLE to decode: {beacon}.")
                        self.decoded[beacon.mac_address] = ThermoBeacon(beacon.mac_address)
                    
                    # all those classes implement a decode() function to do the work
                    self.decoded[beacon.mac_address].decode(beacon)
                    
                    # log what we got
                    self.logger.debug(self.decoded[beacon.mac_address])
                    
                    # and now do something with it (ie. save it to influx)
                    self.output.save(self.decoded[beacon.mac_address])
                    
                    # speed up the queue if we've managed to pass on the message okay
                    sleep_timer = 0.1
                    
            except Queue.Empty:
                # if we're out of events, slow down again
                sleep_timer = 1
            
                
        self.logger.info(f"Stopped the BLE decoder.")
        
        
    def start(self):
        self.logger.info(f"Starting the BLE decoder.")
        self.running = True
        asyncio.run(self.run(), debug=True)
        

    def stop(self):
        self.logger.debug(f"Got stop request.")
        self.running = False

