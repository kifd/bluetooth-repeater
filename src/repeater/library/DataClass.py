# coding: utf-8

# generic dataclasses (BluetoothData and Beacon) and their helpers (json parsing for BluetoothData)


from __future__ import annotations

# pip modules
import humps

# built-ins
from dataclasses import dataclass, field
import dataclasses, json
import base64
from typing import Dict, Any
import hashlib


# this app
from .Exceptions import *


@dataclass
class BluetoothData:
    # timestamp (in ns) of when we got this BLE broadcast
    time: int               = field(default = 0)
    # what's our own IP address
    ip_address: str         = field(default = "000.000.000.000")
    # reported MAC of the BLE device
    mac_address: str        = field(default = "00:00:00:00:00:00")
    # RSSI should be an average(?or sep?) of all the devices reporting this mac_address?
    rssi: int               = field(default = -0)
    
    # data fields that Bleak comes back with
    local_name: str         = field(default = "")
    manufacturer_data: dict = field(default_factory = dict)
    service_data: dict      = field(default_factory = dict)
    service_uuids: list     = field(default_factory = list)
    
    # calculated by the from_json function called by NetworkReceiver as we hash on the bytes payload of manufacturer_data
    hashed: str             = field(default = "")
    

    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                setattr(self, key, value)


    @staticmethod
    def to_json(beacon : BluetoothData):
        return json.dumps(beacon, cls=BluetoothDataJSONEncoder)
    
    
    @staticmethod
    def from_json(json_encoded_string : str):
        try:
            dict_from_json = json.loads(json_encoded_string, cls=BluetoothDataJSONDecoder)
            
        except json.JSONDecodeError as ex:
            raise ConversionException(f"Message was not JSON: {str(ex)}")
        
        # python's json dumps automatically camelCases the json string, so use humps module to get it back to underscores
        underscored_dict = humps.decamelize(dict_from_json)
        
        output = None
        try:
            # hash the payload (NOTE: yes, I'm reencoding the payload that I've just decoded)
            underscored_dict["hashed"] = dict_hash(underscored_dict["manufacturer_data"])
            output = BluetoothData(**underscored_dict)
            
        except TypeError as ex:
            pass
        
        return output
        



# https://www.doc.ic.ac.uk/~nuric/coding/how-to-hash-a-dictionary-in-python.html
def dict_hash(dictionary: Dict[str, Any]) -> str:
    dhash = hashlib.md5()
    encoded = json.dumps(dictionary, sort_keys=True, cls=BluetoothDataJSONEncoder).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


        
class BluetoothDataJSONEncoder(json.JSONEncoder):
    def default(self, o):
        
        if dataclasses.is_dataclass(o):
            encoded = dataclasses.asdict(o)
        
        elif type(o) is bytes:
            encoded = base64.b64encode(o).decode("ascii")
        
        else:
            encoded = super().default(o)
        
        return encoded
    
    
        
class BluetoothDataJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, entire_dict):
        decoded = {}
        
        for key, value in entire_dict.items():
            # see https://bleak.readthedocs.io/en/latest/_modules/bleak/backends/scanner.html
            # these two are the only byte encoded ones that should be passed
            if key == "manufacturer_data" or key == "service_data":
                value = {
                    elem: base64.b64decode( value.get(elem) ) for elem in value
                }
            
            decoded[key] = value
            
        return decoded
    
    







from datetime import datetime
class Beacon():

    time: int               = field(default = 0)
    mac_address: str        = field(default = "00:00:00:00:00:00")
    rssi: int               = field(default = -0)
    repeated_by: str        = field(default = "000.000.000.000")
    
    okay: bool              = field(default = True)
    
    def __init__(self, mac_address):
        self.mac_address = mac_address
        
    def decode(self, data : BluetoothData):
        self.time = data.time
        self.rssi = data.rssi
        self.repeated_by = data.ip_address
        
    def __repr__(self):
        dt = datetime.fromtimestamp(self.time // 1000000000)
        return f"Beacon @ {self.mac_address}, repeated by {self.repeated_by} on {dt.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def is_okay(self):
        return self.okay
