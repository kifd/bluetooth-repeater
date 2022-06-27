import QtQuick 2.15
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.0
import QtQml 2.15


import org.kde.plasma.plasmoid 2.0
import org.kde.kirigami 2.5 as Kirigami

import "../lib"


Kirigami.FormLayout {
    id: configNetworkPage;
    
    // ------------------------------------------------------------------------------------------------------------------------

    property alias cfg_daemonHost : daemonHost.text;
    property alias cfg_daemonPort : daemonPort.text;
    property alias cfg_pollInterval : pollInterval.value;
    property var cfg_macAddressesAvailable : plasmoid.configuration.macAddressesAvailable;
    property string cfg_macAddress : plasmoid.configuration.macAddress;
    property alias cfg_macFriendly : macFriendly.text;
    
    // ------------------------------------------------------------------------------------------------------------------------

    Item {
        Kirigami.FormData.label: i18n("Monitoring Daemon");
        Kirigami.FormData.isSection: true;
    }
    
    TextField {
        id: daemonHost;
        Kirigami.FormData.label: i18n("Address");
        text: plasmoid.configuration.daemonHost;
        //inputMask: "900.900.900.900";
        validator: RegularExpressionValidator { regularExpression: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/ }
        color: acceptableInput ? "white" : "red"
    }
    TextField {
        id: daemonPort;
        Kirigami.FormData.label: i18n("Port");
        text: plasmoid.configuration.daemonPort;
        //inputMask: "99990";
        validator: IntValidator { bottom: 1024; top: 65535; }
        color: acceptableInput ? "white" : "red"
    }
    SpinBox {
        id: pollInterval;
        Kirigami.FormData.label: i18n("Poll Interval (s)");
        valueFromText: function(text) {
            return parseInt(text);
        }
        from: 10;
        to: 3600;
    }

    
    // ------------------------------------------------------------------------------------------------------------------------

    
    Item {
        Kirigami.FormData.label: i18n("Beacon Shown");
        Kirigami.FormData.isSection: true;
    }
    
    
    RowLayout {
    
        Kirigami.FormData.label: i18n("Beacon MAC Address");
        
        BeaconSocket {
            id: macConnector;
            wsUrl: "ws://"+cfg_daemonHost+":"+cfg_daemonPort;
        
            onReceivedData: {
                cfg_macAddressesAvailable = dataReceived.split(",");
                
                if (cfg_macAddress != "") {
                    // always have the currently selected MAC, even if we couldn't find it on the broadcast
                    cfg_macAddressesAvailable.push(cfg_macAddress);
                    // but make sure we don't have it twice...
                    // https://stackoverflow.com/questions/1960473/get-all-unique-values-in-a-javascript-array-remove-duplicates#comment68618078_14438954
                    cfg_macAddressesAvailable = [...new Set(cfg_macAddressesAvailable)];
                    console.log("Made sure " + cfg_macAddress + " was on the address list.");
                    
                    macAddressListCB.model = cfg_macAddressesAvailable;
                    macAddressListCB.currentIndex = macAddressListCB.find(cfg_macAddress);
                    
                } else {
                    console.log("No existing MAC address.");
                    
                    macAddressListCB.model = cfg_macAddressesAvailable;
                    
                    macAddressListCB.currentIndex = 0;
                    cfg_macAddress = macAddressListCB.currentText;
                }
                
            }
        }
        
        
        ComboBox {
            id: macAddressListCB;
            
            onActivated: {
                cfg_macAddress = macAddressListCB.currentText;
                //plasmoid.configuration.macAddress = macAddressListCB.currentText;
            }
            
            Component.onCompleted: {
                if (cfg_macAddressesAvailable.length == 0) {
                    console.log("No existing MACs, so trying to get some now.")
                    macFetch.clicked();
                } else {
                    console.log("Loaded ("+cfg_macAddress+") with these addresses available: " + cfg_macAddressesAvailable)
                    macAddressListCB.model = cfg_macAddressesAvailable;
                    macAddressListCB.currentIndex = macAddressListCB.find(cfg_macAddress);
                }
            }
        }
        
        Button {
            id: macFetch;
            text: i18n("Refresh");
            onClicked: {
                console.log("Refreshing list of available beacon MAC addresses.")
                macConnector.sendData("LIST");
            }
        }
    }
    
    
    TextField {
        id: macFriendly;
        Kirigami.FormData.label: i18n("Alias");
        text: plasmoid.configuration.macFriendly;
    }
    
    
}
