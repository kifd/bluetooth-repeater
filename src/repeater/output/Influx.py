# coding: utf-8

# pip modules
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


# built-ins
import logging
from urllib3 import Retry



class Influx:
    
    def __init__(self, cfg):
        self.logger = logging.getLogger(__name__)
        
        self.bucket = cfg.bucket
        
        self.client = influxdb_client.InfluxDBClient(
            url = cfg.url,
            org = cfg.org,
            token = cfg.api_token,
            retries = Retry(connect=5, read=0, redirect=0),
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)


    def save(self, beacon):
        
        if beacon.is_okay():
            
            self.logger.debug(f"Influx dealing with {beacon}.")
            
            # NOTE: may well be better as 2-4 separate measurements ?
            # eg name=temperature,tag=mac_address,fields=temperature
            
            # TODO: record the mac description here, else there wasn't any point having it
            
            pt = {
                "name"        : "thermobeacon",
                "time"        : int(beacon.time),
                "mac_address" : beacon.mac_address,
                "temperature" : float(beacon.temperature),
                "humidity"    : float(beacon.humidity),
                "rssi"        : int(beacon.rssi),
                "battery"     : float(beacon.battery_level),
            }
            
            p = influxdb_client.Point.from_dict(pt,
                write_precision=influxdb_client.WritePrecision.NS,
                record_measurement_key="name",
                record_time_key="time",
                record_tag_keys=["mac_address"],
                record_field_keys=["temperature", "humidity", "rssi", "battery_level"]
            )
            
            #print(vars(p))

            self.write_api.write(bucket=self.bucket, org=self.client.org, record=p)

        else:
            
            self.logger.debug(f"Influx skipping {beacon} because no temperature set.")
