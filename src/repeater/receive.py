
# pip modules


# python built ins
import logging
from queue import Queue
from threading import Thread
import sys, signal


# this app
from .library.Exceptions import *
from .library.Config import *

from .library.NetworkReceiver import NetworkReceiver
from .library.NetworkDaemon import NetworkDaemon
from .decoders.BLEDecoder import BLEDecoder



class Receive:
    
    def __init__(self):
        self.cfg = Config()
        
        # only vaguely reliable way for python to handle ctrl+c with threads
        signal.signal(signal.SIGINT, self.signal_handler)
 
        incoming = Queue()
        decoded = {}
        self.netreceive = NetworkReceiver(incoming, self.cfg.network, decoded)
        self.bledecoder = BLEDecoder(incoming, self.cfg, decoded)
        self.netdaemon  = NetworkDaemon(self.cfg)
    
        self.threads = [
            Thread(target = self.netreceive.start, daemon = True),
            Thread(target = self.bledecoder.start, daemon = True),
            Thread(target = self.netdaemon.start,  daemon = True)
        ]


    def signal_handler(self, signal, frame):
        self.cfg.logger.info(f"Terminating program.")
        
        # tell our classes to finish
        self.netreceive.stop()
        self.bledecoder.stop()
        self.netdaemon.stop()
        
        # and wait for them to do so
        while self.threads:
            for t in self.threads:
                t.join(0.1)
                if t.is_alive():
                    self.cfg.logger.debug(f"{t.name} not yet ready to stop.")
                else:
                    self.cfg.logger.debug(f"{t.name} finished.")
                    self.threads.remove(t)
        
        # TODO: different exit code by signal passed
        sys.exit(0)

    
    def start(self):
        self.cfg.logger.info(f"Starting threads.")
        for t in self.threads:
            t.start()
            
        # now wait til they've finished (which is forever, unless interrupted)
        for t in self.threads:
            t.join()
            




def entry():
    Receive().start()
