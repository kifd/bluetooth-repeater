
# pip modules
import rpyc
from rpyc.lib.compat import TimeoutError as AsyncResultTimeout
import schedule

# built-ins
import logging
import asyncio
import os, signal
import queue as Queue
import socket
import time
import errno


# this app
from .DataClass import *
from .Exceptions import *


    
class NetworkSender:

    running = False
    stack_by_mac = {}
    
    sent_okay = {}
   
    network_connected = False
    network_problems = 0
    
    

    def __init__(self, xtcomm, network):
        self.logger = logging.getLogger(__name__)
        self.queue = xtcomm
        self.network = network
        self.ip_address = self.get_ip()
        self.last_message = time.time()
        
    
    async def run(self):
        
        # queue sleep to stop killing the cpu waiting for events
        sleep_timer = 1
        
        schedule.every(10).minutes.do(self.stats)
        
        while self.running:
            
            schedule.run_pending()
            
            # sleep to stop killing the cpu waiting for events
            # NOTE: that sleeping for ages will stop the thread from being closed nicely
            await asyncio.sleep(sleep_timer)
            
            
            # move any new beacons off the shared queue onto separated, timed stacks
            try:
                beacon = self.queue.get(False)
                
            except Queue.Empty:
                was_quick = False
            
            else:
                beacon.ip_address = self.ip_address
                self.logger.debug(f"Received beacon message to send upstream: {beacon}.")
                
                if beacon.mac_address not in self.stack_by_mac:
                    self.stack_by_mac[beacon.mac_address] = TimedStack(self.network.granularity)
            
                # add the beacon to its own timestamped stack
                was_quick = self.stack_by_mac[beacon.mac_address].push(beacon)
                
                self.logger.debug(f"{beacon.mac_address} stack {self.stack_by_mac[beacon.mac_address]}.")
                

            # process the stacks of beacon messages
            stack_size = sum([ stack.size() for mac, stack in self.stack_by_mac.items() ])
            
            if stack_size:
                # we have something to send, so let's see if we can
                    
                # what is the status of the network?
                try:
                    conn = rpyc.connect(self.network.address, self.network.rpyc_port)
                            
                except (OSError, ConnectionError, EOFError, AsyncResultTimeout) as ex:
                    self.logger.debug(f"Could not reach the network endpoint while connecting: {ex}.")
                    self.network_connected = False
                    # increment our stat counter
                    self.network_problems += 1
                    
                except Exception as ex:
                    self.logger.error(f"Missing network exception still: {str(ex)}")
                    os.kill(os.getpid(), signal.SIGINT)
                
                else:
                    self.network_connected = True
                    
                    
                
                # if we have a network connection, send beacons upstream
                if self.network_connected:
                    
                    for mac, stack in self.stack_by_mac.items():
                        timestamp, b = stack.pop()
                        if b:
                                        
                            try:
                                conn.root.message(BluetoothData.to_json(b))
                                        
                            except (OSError, ConnectionError, EOFError, AsyncResultTimeout) as ex:
                                self.logger.debug(f"Could not reach the network endpoint while messaging: {ex}.")
                                self.network_connected = False
                                # increment our stat counter
                                self.network_problems += 1
                                # and always put the beacon back because we weren't meant to have a network problem here
                                stack.push(b)
                                break
                            
                            else:
                                self.logger.debug(f"Sent beacon {b.mac_address} upstream.")
                                # increment counter
                                self.sent_okay[b.mac_address] = self.sent_okay[b.mac_address] + 1 if b.mac_address in self.sent_okay else 1
                                self.logger.debug(f"{b.mac_address} stack now {self.stack_by_mac[b.mac_address].size()} big.")
                
                
                # if we do not have a connection, then should we have added that beacon to the stack?
                elif was_quick:
                    
                    timestamp, b = self.stack_by_mac[beacon.mac_address].pop()
                    self.logger.debug(f"Popped beacon {b.mac_address} because it was too quick.")
                    
                    
            
            if stack_size:
                if self.network_connected:
                    # speed up the processing if we have messages and a network connection
                    sleep_timer = 0.1
                else:
                    # slow the shared queue processing down, as our endpoint has gone away
                    sleep_timer = 2
            else:
                if self.network_connected:
                    # if we're out of events, slow down again
                    sleep_timer = 1
                else:
                    # out of events and no network, slow right down
                    sleep_timer = 10
                
                
        self.logger.info(f"Stopping the network queue.")
        
    
    
    def stats(self):
        self.logger.info(f"Total messages sent upstream: {self.sent_okay}")
        if self.network_problems > 0:
            self.logger.info(f"Total network interruptions: {self.network_problems}")
        self.logger.info(f"MAC queues: {self.stack_by_mac}")
        if self.queue.qsize() > 0:
            self.logger.info(f"Current queue size: {self.queue.qsize()}")
        
    
    def start(self):
        self.logger.info(f"Starting the network queue.")
        self.running = True
        asyncio.run(self.run(), debug=True)
        
        
    def stop(self):
        self.logger.debug(f"Got stop request.")
        self.running = False
        
    
    def get_ip(self):
        ip = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.255.255.255", 1))
            ip = s.getsockname()[0]
            s.close()
        except (OSError, ConnectionError, EOFError) as ex:
            self.logger.debug(f"Network not started: {ex}.")
            self.network_connected = False
            # increment our stat counter
            self.network_problems += 1
        return ip





class TimedStack:
    
    def __init__(self, granularity : int = 10):
        self.granularity = granularity
        self.elements = []
    
    def __repr__(self):
        if self.is_empty():
            return f"TimedStack() is empty."
        else:
            return f"TimedStack() has {self.size()} elements, latest is {self.peek()}."
    
    def push(self, element):
        if (self.is_empty()):
            was_quick = False
        else:
            was_quick = (self.peek()[0] > time.time() - self.granularity)
        
        self.elements.append((time.time(), element))
        return was_quick

    def peek(self):
        timestamp, output = self.elements[-1] if self.size() else (None, None)
        return (timestamp, output)
        
    def pop(self):
        timestamp, output = self.elements.pop() if self.size() else (None, None)
        return (timestamp, output)

    def size(self):
        return len(self.elements)
    
    def is_empty(self):
        return self.size() == 0
