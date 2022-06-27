# coding: utf-8

# pip modules
from bleak import BleakScanner, BleakError

# built-ins
import logging
import asyncio
import time
import os, signal

# this app
from .DataClass import *
from .Exceptions import *


    
class BluetoothScanner:

    running = False
    beacons = {}

    def __init__(self, xtcomm, cfg):
        # logger
        self.logger = logging.getLogger(__name__)
        # we use a Queue object to pass messages from this simple BT class to the network interface
        self.queue = xtcomm
        # config
        self.cfg = cfg
        # the library that does the work
        self.scanner = BleakScanner()
        self.scanner.register_detection_callback(self.detection_callback)
        
        # NOTE: if you have more decoders than just TBs, add them here too
        self.macs = list(set(k.lower() for k in self.cfg.thermobeacons.__dict__))
        
        
    def detection_callback(self, device, data):
        beacon = BluetoothData(**{
            "time": time.time_ns(),
            "mac_address": device.address,
            "rssi": device.rssi,
            "local_name": data.local_name,
            "manufacturer_data": data.manufacturer_data,
            "service_data": data.service_data,
            "service_uuids": data.service_uuids,
        })
        
        
        if self.okay_to_repeat(beacon.mac_address):
            
            # only send on messages when the advertisement has changed
            if not beacon.mac_address in self.beacons or self.beacons[beacon.mac_address].manufacturer_data != beacon.manufacturer_data:
                self.logger.debug(f"Beacon detected: {str(beacon)}")
                # internal stack to keep track of the manufacturer_data
                self.beacons[beacon.mac_address] = beacon
                # cross thread communication
                self.queue.put(beacon)
                self.logger.debug(f"Queued beacon. Queue size now {self.queue.qsize()}.")
            else:
                self.logger.debug(f"Beacon data for {beacon.mac_address} not changed, skipping.")
        
        else:
            self.logger.debug(f"Beacon {beacon.mac_address} not configured, ignoring.")

            
    async def run(self):
        try:
            await self.scanner.start()
            while self.running:
                await asyncio.sleep(1)
        except Exception as ex:
            self.logger.error(f"ERROR: {str(ex)}")
            os.kill(os.getpid(), signal.SIGINT)

        finally:
            try:
                self.logger.info(f"Stopping the scanner.")
                await self.scanner.stop()
            except Exception as ex:
                self.logger.error(f"ERROR: {str(ex)}")
                os.kill(os.getpid(), signal.SIGINT)
            

    def start(self):
        self.logger.info(f"Starting the scanner.")
        self.running = True
        asyncio.run(self.run(), debug=True)
        

    def stop(self):
        self.logger.debug(f"Got stop request.")
        self.running = False


    def okay_to_repeat(self, mac):
        return (mac.lower() in self.macs)
    
    
