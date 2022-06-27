# ThermoBeacon scanner cobbled together from:
# main skeleton = https://stackoverflow.com/questions/69657870/python-bleak-scan-for-advertisements-and-exit-event-loop
# data parsing = https://github.com/frawau/aioblescan/blob/master/aioblescan/plugins/thermobeacon.py
# and voltage = https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/ble_parser/thermoplus.py

# TODO: check out https://pypi.org/project/aioblescan/
# TODO: check out https://github.com/rnlgreen/thermobeacon

from __future__ import annotations


# built-ins
from dataclasses import dataclass, field

# this app
from ..library.DataClass import *



@dataclass
class ThermoBeacon(Beacon):

    temperature: float      = field(default = 0.0)
    humidity: float         = field(default = 0.0)
    battery_volts: int      = field(default = 0)
    battery_level: float    = field(default = 0.0)
    counter: int            = field(default = 0)
    
    max_temperature: float  = field(default = 0.0)
    min_temperature: float  = field(default = 0.0)
    max_temp_ts: int        = field(default = 0)
    min_temp_ts: int        = field(default = 0)


    def __init__(self, mac_address):
        super().__init__(mac_address)
        
        # the whole "okay" flag is because TB have two distinct advertisements, and we can't report a temperature from just the max/min one
        self.okay = False
        
        
    def __repr__(self):
        output = super().__repr__()
        if self.is_okay():
            output = f"{output} measured {self.temperature} degrees and {self.humidity} % humidity."
        return output
    
    
    """
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(name)
    """
    
        
    def decode(self, data : BluetoothData):
        super().decode(data)
        
        payload = data.manufacturer_data["16"]
    
        if len(payload) == 18:
            
            self.battery_volts = int.from_bytes(payload[8:10], "little")
            self.temperature = int.from_bytes(payload[10:12], "little", signed=True) / 16.0
            self.humidity = int.from_bytes(payload[12:14], "little", signed=True) / 16.0
            self.counter = int.from_bytes(payload[14:18], "little")
            
            # https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/ble_parser/thermoplus.py
            battery = 2500
            if self.battery_volts >= 3000:
                battery = 100
            elif self.battery_volts >= 2600:
                battery = 60 + (self.battery_volts - 2600) * 0.1
            elif self.battery_volts >= 2500:
                battery = 40 + (self.battery_volts - 2500) * 0.2
            elif self.battery_volts >= 2450:
                battery = 20 + (self.battery_volts - 2450) * 0.4
            else:
                battery = 0
            self.battery_level = round(battery, 2)
            
            # okay to use this beacon in the output stage (ie. save to influx)
            self.okay = True
            

        elif len(payload) == 20:
            
            self.max_temperature = int.from_bytes(payload[8:10], "little") / 16.0
            self.max_temp_ts = int.from_bytes(payload[10:14], "little")
            self.min_temperature = int.from_bytes(payload[14:16], "little") / 16.0
            self.min_temp_ts = int.from_bytes(payload[16:20], "little")
        
        
