# coding: utf-8

# pip modules

# python built ins
import logging
from queue import Queue
from threading import Thread
import sys, signal, time


# this app
from .library.Exceptions import *
from .library.Config import *

from .library.BluetoothScanner import BluetoothScanner
from .library.NetworkSender import NetworkSender



class Repeat:
    
    def __init__(self):
        self.cfg = Config()
        
        # only vaguely reliable way for python to handle ctrl+c with threads
        signal.signal(signal.SIGINT, self.signal_handler)
 
        xtcomm = Queue()
        self.netsend = NetworkSender(xtcomm, self.cfg.network)
        self.scanner = BluetoothScanner(xtcomm, self.cfg)
        self.threads = [
            Thread(target = self.netsend.start, daemon = True),
            Thread(target = self.scanner.start, daemon = True)
        ]


    def signal_handler(self, signal, frame):
        self.cfg.logger.info(f"Terminating program.")
        
        # tell our classes to finish
        self.netsend.stop()
        self.scanner.stop()
        
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
            

# TODO: replace with __main__ and update setup.cfg
def entry():
    Repeat().start()
