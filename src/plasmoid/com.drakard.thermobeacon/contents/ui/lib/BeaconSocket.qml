import QtQuick 2.15
import org.kde.plasma.plasmoid 2.0

// REQUIRES apt package: qml-module-qt-websockets
import QtWebSockets 1.0



Item {
    id: beaconSocket;
    
    // ------------------------------------------------------------------------------------------------------------------------

    property string wsUrl;
    property int timeOutInSeconds: 60;
    
    property string dataSent;
    property string dataReceived;
    
    
    // ------------------------------------------------------------------------------------------------------------------------

    signal sendData(string message);
    signal receivedData();
    
    onSendData: {
        dataSent = message;
        monitorSocket.active = true;
    }
    
    // ------------------------------------------------------------------------------------------------------------------------

    
    WebSocket {
        id: monitorSocket;
        url: wsUrl;
        active: false;
        
        onStatusChanged:
            if (monitorSocket.status == WebSocket.Connecting) {
                plasmoid.busy = true;
                connectionTimeoutTimer.start();
                
            } else if (monitorSocket.status == WebSocket.Open) {
                
                if (dataSent != "") {
                    console.log("Sending: " + dataSent);
                    monitorSocket.sendTextMessage(dataSent);
                    
                    plasmoid.busy = false;
                    connectionTimeoutTimer.stop();
                }
                
            } else if (monitorSocket.status == WebSocket.Closed) {
                monitorSocket.active = false;
                
            } else if (monitorSocket.status == WebSocket.Error) {
                console.log("Error: " + monitorSocket.errorString);
            }
            
            
        onTextMessageReceived: {
            if (! message.includes("Error")) {
                dataReceived = message;
                console.log("Received: "+dataReceived);
                beaconSocket.receivedData();
                
            } else {
                console.log(message);
            }
        }
    }
    
    
    Timer {
        id: connectionTimeoutTimer;
        interval: timeOutInSeconds * 1000;
        repeat: false;
        onTriggered: {
            monitorSocket.active = false;
            plasmoid.busy = false;
            console.log(i18n("Error: Timed out trying to retrieve data from the socket."));
        }
    }
    
}
