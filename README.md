# Bluetooth Repeater/Receiver

Listens for BLE beacon advertisements, and repeats them on a normal network connection to a receiving port.


## Description

I have a bunch of bluetooth [ThermoBeacons](https://www.amazon.co.uk/Brifit-Thermometer-Hygrometer-Temperature-Greenhouse/dp/B08DLHFKT3/) scattered around my house, but their broadcast range doesn't reach the server that will track the data. Fortunately, there are also a few always-on computers (mostly Pis) that are in range of one or more of these beacons, and can be used to forward the sensor readings on to the main server.

Additionally, as I'm currently using a laptop as the box that gathers all the readings into one place (and that gets turned off each night), each BLE repeater needed to be able to queue their messages when it's unable to reach the laptop.


## Getting Started

### Dependencies

* Have some BLE devices broadcasting data - currently, only those **ThermoBeacons** are definitely okay out-of-the-box (because that's all I've got to test with), so if you don't have them, you'll need to write your own decoder module.

* **Influx** to save the data - again, unless you write your own output module.

* Both the repeating and receiving computers involved were running Debian flavoured **Linux** with **Python 3.9** - other versions of Linux/BSD should be fine, but I've no idea about Windows or Mac compatibility.

* And let's be honest, as this is very much "alpha/it-works-for-me" code, you're going to need to know your way around Python to adapt it for your own uses.



### Installing

* (Make Debian based OSes, like Rasbian, able to install virtual environments):
    * `sudo apt install python3-venv`
    
* Change directory to wherever you want to install it, eg:
    * `cd ~/.local/bin`

* Download this project and cd into it:
    * `git clone https://github.com/kifd/bluetooth-repeater`
    * `cd bluetooth-repeater`
    
* Install the virtual environment and activate it:
    * `python3 -m venv .venv`
    * `source .venv/bin/activate`
    
* Install the project, along with its pip dependencies:
    * `pip install --editable .`
    
* On any computer that will forward the BLE advertisements onwards, copy the blerepeater@ systemd file and point it at the install directory:
    * `sudo cp tools/systemd/blerepeater@.service /etc/systemd/system`
    * `sudo sed -i "s|PATHTOBLEDIRECTORY|$PWD|g" /etc/systemd/system/blerepeater@.service`

* On the destination computer, setup the BLE receiver service instead:
    * `sudo cp tools/systemd/blereceiver@.service /etc/systemd/system`
    * `sudo sed -i "s|PATHTOBLEDIRECTORY|$PWD|g" /etc/systemd/system/blereceiver@.service`
    
    
    
    
### Configuration

* Copy the `conf/config.json.example` to `conf/config.json` and edit it to reflect your own environment.

* Change the logging level to adjust how much gets written to the systemd journal.

* For each device section (currently just ThermoBeacons), add the bluetooth devices you wish to listen to as a dictionary of "mac address" : "description" pairs.

* Change the network address (and port if wanted) to the target computer that will receive all the broadcasts and do something with them. If necessary, remember to open that port on its firewall.

* Set the network queue granularity, which comes into play when that target computer can't be reached and limits the amount of messages per MAC that will get stored in a queue (no more than one every X seconds).

* Change the Influx settings to wherever your own Influx DB server is located. Make sure your API token has write permission for the bucket you want to store the sensor readings in.

        
### Running

* Run once:
    * `sudo systemctl start blerepeater@YOURUSERNAME`
    
* Check the log:
    * `sudo journalctl -f -u blerepeater@YOURUSERNAME`

* Run on startup:
    * `sudo systemctl enable blerepeater@YOURUSERNAME`

* And do the same for the blereceiver on the target computer.
    



## Authors

* [Keith Drakard](https://drakard.com)


## Version History

* 0.1 - Initial Release

 

## Roadmap

* Split off the ble decoding/influx/plasmoid bits into separate repos, and have this one just focus on generic bluetooth -&gt; network.
* Then draw the rest of the owl, finish the code TODOs, and make it into a proper package.

    
## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).


## Acknowledgments

* [aioblescan](https://github.com/frawau/aioblescan) for the ThermoBeacon parsing
* [Bleak](https://github.com/hbldh/bleak) and [RPyC](https://github.com/tomerfiliba-org/rpyc) for the bluetooth and network libraries
* StackOverflow for saving me having to remember how to code

