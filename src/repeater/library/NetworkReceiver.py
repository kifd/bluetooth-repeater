
# pip modules
import rpyc
from rpyc.utils.server import ThreadedServer
import time

# built-ins
import logging
import asyncio, signal
import time
import queue as Queue

# this app
from .DataClass import *
from .Exceptions import *



class RPCService(rpyc.Service):
    
    # hash table of manufacturer_data : timestamp
    hashed = {}
    
    # stats
    count_by_mac = {}
    count_by_ip = {}
    duplicates = 0
    
    
    def __init__(self, incoming, decoded):
        self.logger = logging.getLogger(__name__)
        self.queue = incoming
        self.decoded = decoded # latest beacon by mac
        self.last_message = time.time()
        
        
    def on_connect(self, conn):
        self.logger.debug(f"Connection opened from {conn._channel.stream.sock.getpeername()}.")

    """
    def on_disconnect(self, conn):
        try:
            self.logger.debug(f"Connection closed from {conn._channel.stream.sock.getpeername()}.")
        except (EOFError) as ex:
            self.logger.debug(f"Connection closed prematurely: {ex}.")
    """


    def exposed_message(self, message):
        #self.logger.debug(f"Got message: {message}.")
        beacon = BluetoothData.from_json(message)
        
        if beacon:
            self.logger.debug(f"Converted JSON to: {beacon}.")
            
            if not beacon.hashed in self.hashed:
                self.queue.put(beacon)
                self.logger.debug(f"Queued beacon okay. Queue size now {self.queue.qsize()}.")
                self.hashed[beacon.hashed] = time.time()
                
                # increment some stat counters
                self.count_by_mac[beacon.mac_address] = self.count_by_mac[beacon.mac_address] + 1 if beacon.mac_address in self.count_by_mac else 1
                self.count_by_ip[beacon.ip_address] = self.count_by_ip[beacon.ip_address] + 1 if beacon.ip_address in self.count_by_ip else 1
                
            else:
                self.logger.debug(f"Duplicate beacon message. Queue size still {self.queue.qsize()}.")
                self.duplicates += 1
        else:
            self.logger.warn(f"Could not decoded message {message}.")
            
        
        # if it's been more than X seconds since we got a message, print some stats and clean the hash table
        now = time.time()
        if now > self.last_message + 300:
            self.last_message = now
            self.schedule()
        
        
    def exposed_question(self, mac):
        self.logger.debug(f"Was asked for the latest data of {mac}.")
        answer = self.decoded[mac] if mac in self.decoded else None
        return answer
        
        
        
    def schedule(self):
        self.logger.info(f"Total messages received from downstream by BLE mac: {self.count_by_mac}")
        self.logger.info(f"Total messages received from downstream by repeater: {self.count_by_ip}")
        
        # remove entries from the hash table that are older than 5 minutes
        self.hashed = {h: ts for h, ts in self.hashed.items() if ts > self.last_message - 300}
        self.logger.info(f"{self.duplicates} duplicated messages received. Hash table size is {len(self.hashed)}.")
        
        
        
class NetworkReceiver:

    def __init__(self, incoming, cfg, decoded : dict):
        self.logger = logging.getLogger(__name__)
        
        rpyc_logger = logging.getLogger('ipc.rpyc')
        rpyc_logger.setLevel(logging.WARNING)
        
        self.server = ThreadedServer(RPCService(incoming, decoded), port=cfg.rpyc_port, logger=rpyc_logger, protocol_config={
            'allow_public_attrs': True,
        })
        
        
        
    def start(self):
        self.logger.info(f"Starting the network receiver.")
        self.server.start()

    def stop(self):
        self.server.close()
        self.logger.info(f"Stopped the network receiver.")
        
    
    
    
        
