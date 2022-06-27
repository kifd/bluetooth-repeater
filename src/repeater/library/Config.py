
# pip modules

# python built ins
import json
from types import SimpleNamespace as Namespace

import logging
#import logging.config

import os



class Config:
    """
Simple class to read a config file or provide defaults.
    """
    
    def __init__(self):
        
        config_file = os.path.join(os.path.dirname(__file__), "../../../conf", "config.json")
        
        with open(config_file) as cf:
            self.data = json.load(cf, object_hook=lambda d: Namespace(**d))
        
        """
        for name in self.data.__dict__:
            value = getattr(self.data, name)
            setattr(self, name, value)
        """
        
        
        if self.logging == "warn":
            self.log_level = 30
        elif self.logging == "debug":
            self.log_level = 10
        else:
            self.log_level = 20 # info
        
        # now set up the logging for the rest of the program
        self.logcfg()
        
        
        
    def __getattr__(self, name):
        if name in self.data.__dict__:
            return getattr(self.data, name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(f"Config has no attribute called '{name}'.")


    
    def logcfg(self):
        # TODO: use https://docs.python.org/3/howto/logging.html#configuring-logging
        logging.basicConfig(
            level = self.log_level,
            format = "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        )
        self.logger = logging.getLogger("repeater")
        
        # disable the asyncio "Executing took ... seconds" warning, because it gets rendered useless by sleeping() always triggering it
        logging.getLogger("asyncio").setLevel(logging.ERROR)
        
        # don't need to see all the hello/goodbye spam at loglevel info
        logging.getLogger("rpyc").setLevel(logging.WARNING)
