// main.qml

import QtQuick 2.0
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.15
 
import org.kde.plasma.plasmoid 2.0
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.kirigami 2.9 as Kirigami


import "../js/ColorLibrary.js" as JS
import "lib"


Item {
    id: root;
    
    // ------------------------------------------------------------------------------------------------------------------------

    property var cfg;
    property bool needsConfiguration;

    Component.onCompleted: {
        cfg = plasmoid.configuration;
        needsConfiguration = (cfg.macAddress == "");
        //console.log("Got "+JSON.stringify(cfg));
    }

    width: units.gridUnit * 15
    height: units.gridUnit * 15
    
    Plasmoid.backgroundHints: "NoBackground";
    //Plasmoid.preferredRepresentation: Plasmoid.fullRepresentation;
    //Plasmoid.preferredRepresentation: Plasmoid.compactRepresentation;
    
    
    
    // ------------------------------------------------------------------------------------------------------------------------
    
    PlasmaCore.DataSource {
        id: dataSource
    }
    

    BeaconSocket {
        id: beacon;
        wsUrl: "ws://"+cfg.daemonHost+":"+cfg.daemonPort;
        
        property real celsius: 0.0;
        property real humidity: 0.0;
        property int rssi: 0;
        property real batteryLevel: 0.0;
        property int counter: 0;
        
        
        onReceivedData: {
            
            var beaconData = dataReceived.split(",");
            console.log("Got "+JSON.stringify(beaconData))
            
            if (beaconData.length == 5) {
                celsius      = beaconData[0];
                humidity     = beaconData[1];
                rssi         = beaconData[2];
                batteryLevel = beaconData[3];
                counter      = beaconData[4];
            }
        }
        
        Timer {
            id: monitorTimer;
            interval: cfg.pollInterval * 1000;
            repeat: true;
            running: false;
            onTriggered: beacon.sendData(cfg.macAddress);
        }
        
        Component.onCompleted: {
            if (cfg.macAddress != "") {
                monitorTimer.running = true;
            }
        }
        
        // used as a trigger to force a refresh upon a config change that is quicker than the pollInterval would be
        // also doubles as the Timer's triggeredOnStart equivalent, as onTextChanged fires when first drawn 
        Text {
            id: macAddressText;
            visible: true;
            text: cfg.macAddress;
            onTextChanged: {
                root.needsConfiguration = false;
                console.log("Getting new MAC address data for " + cfg.macAddress);
                beacon.sendData(cfg.macAddress);
            }
        }
        
        
        
        function convertTemperature() {
            var temperature = celsius * 1.0;
            var unit = cfg.temperatureUnits[cfg.temperatureUnitSelected];
            var accuracy = cfg.temperatureDecimals;
            
            if (unit == "fahrenheit") {
                temperature = (temperature * 9 / 5) + 32;
                
            } else if (unit == "kelvin") {
                temperature = temperature + 273.15;
            }
            return temperature.toFixed(accuracy);
        }
        
        
        function displayTemperature(show = false) {
            var output = convertTemperature();
            if (cfg.showTemperatureUnits || show) {
                var tUnit = cfg.temperatureUnits[cfg.temperatureUnitSelected].toString().charAt(0).toUpperCase();
                output += "<sup>°" + tUnit + "</sup>";
            }
            return output;
        }
        
        function displayHumidity(show = false) {
            var output = humidity.toFixed(cfg.humidityDecimals);
            if (cfg.showHumidityPercent || show) {
                output += "<small>%</small>";
            }
            return output
        }
        
        
        function getToolTip() {
            var tooltips = [];
            if (! root.needsConfiguration) {
                tooltips.push(i18n("Temperature: %1", displayTemperature(true)));
                tooltips.push(i18n("Humidity: %1", displayHumidity(true)));
                tooltips.push(i18n("Signal Strength: %1", rssi));
                tooltips.push(i18n("Battery Level: %1<small>%</small>", batteryLevel));
                tooltips.push(i18n("Counter: %1", counter));
            } else {
                tooltips.push(i18nc("@info:tooltip", "Please configure me."));
            }
            return tooltips.join("<br>");
        }
        
    }
    
    
    // ------------------------------------------------------------------------------------------------------------------------

    
    Plasmoid.fullRepresentation: Item {
        id: representation;
        
        Layout.minimumWidth: units.gridUnit * 4;
        Layout.minimumHeight: units.gridUnit * 4;
        Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter;

        
        Circle {
            id: temperatureCircle;
            text: (! needsConfiguration) ? beacon.displayTemperature() : qsTr("temperature");
            
            colorInfill: plasmoid.configuration.temperatureBackgroundColor;
            colorBorder: Qt.rgba(0,0,0, 0.4);
            colorText: JS.getContrastingColor(colorInfill);
            
            sizeMain: parent.width < parent.height ? parent.width : parent.height;
            sizePadding: 40;
            
            showShadow: true;
            
            anchors.fill: parent;
        }
        
        Circle {
            id: humidityCircle;
            visible: cfg.showHumidity;
            
            text: (! needsConfiguration) ? beacon.displayHumidity() : qsTr("humidity");
            
            colorInfill: plasmoid.configuration.humidityBackgroundColor;
            colorBorder: Qt.rgba(0,0,0, 0.8);
            colorText: JS.getContrastingColor(colorInfill);
            
            sizeMain: 1 * (temperatureCircle.getRadius() - (temperatureCircle.getTextHeight() / 2));
            sizeBorder: 4;
            sizeText: 12;
            
            x: circularAnchorX(temperatureCircle, 45);
            y: circularAnchorY(temperatureCircle, 45);
            
        }
    
        Circle {
            id: aliasCircle;
            visible: cfg.showAlias;
            
            text: (! needsConfiguration) ? cfg.macFriendly : qsTr("mac");
            
            colorInfill: plasmoid.configuration.aliasBackgroundColor;
            colorBorder: Qt.rgba(0,0,0, 0.8);
            colorText: JS.getContrastingColor(colorInfill);
            
            sizeMain: 1.2 * (temperatureCircle.getRadius() - (temperatureCircle.getTextHeight() / 2));
            sizeBorder: 4;
            sizeText: 18;
            
            x: circularAnchorX(temperatureCircle, 225);
            y: circularAnchorY(temperatureCircle, 225);
        }
    
        
        
        FadingToolTip {
            anchors.fill: temperatureCircle
            title: cfg.macFriendly;
            body: beacon.getToolTip();
        }
        
        
        
        // 0 degrees in QML = east / 3 o'clock / due right...
        function circularAnchorX(circle, degrees) {
            var offset = circle.x + (circle.width / 2);
            return (circle.getRadius() * Math.cos((Math.PI/180) * degrees)) + offset;
        }
        function circularAnchorY(circle, degrees) {
            var offset = circle.y + (circle.height / 2);
            return (circle.getRadius() * Math.sin((Math.PI/180) * degrees)) + offset;
        }
    
    
    }
    
    
    
    
    
    
    
    Plasmoid.compactRepresentation: Item {
        id: iconRepresentation;
        anchors.fill: parent;
        
    
        Rectangle {
            color: Qt.rgba(0, 0, 0, 0.2);
            radius: parent.width < parent.height ? parent.width * 0.5 : parent.height * 0.5;
            border.color: Qt.rgba(0, 0, 0, 0.8);
            border.width: 4;
            
            anchors.fill: parent;
            
            
            Text {
                text: (! needsConfiguration) ? beacon.convertTemperature() : qsTr("temperature");
                anchors {
                    fill: parent;
                    margins: units.smallSpacing * 4;
                }
                horizontalAlignment: Text.AlignHCenter;
                verticalAlignment: Text.AlignVCenter;
                
                fontSizeMode: Text.Fit;
                minimumPixelSize: 8;
                font.pixelSize: 64;
                color: PlasmaCore.Theme.textColor;
            }
        }
        
    }
    
}
