// Bo Thorsen @ https://www.vikingsoftware.com/blog/implementing-tool-tips-in-qml/

import QtQuick 2.0


Item {
    anchors.fill: parent;
    
    property string title;
    property string body;
    
    property bool showToolTip: false;
    
    property color colorBackground: "#000000";
    property color colorBorder: "#0a0a0a";
    property color colorText: "#ffffff";
    
    property int toolTipSensitivity: 500;
    property int fadeDuration: 750;
    property int textPaddingX: 32;
    property int textPaddingY: 16;
    
    
    Rectangle {
        id: toolTipRectangle;
        anchors.horizontalCenter: parent.horizontalCenter;
        anchors.verticalCenter: parent.verticalCenter;
        width: toolTipText.width + textPaddingX;
        height: toolTipText.height + textPaddingY;
        opacity: (title != "" || body != "") && showToolTip ? 1 : 0;
        
        radius: (width / 100) * 4;
        color: colorBackground;
        border.color: colorBorder;
        
        Column {
            id: toolTipText;
            anchors.centerIn: parent;
            spacing: units.smallSpacing * 2;
            
            // PlasmaExtras.Heading
            Text {
                text: title;
                color: colorText;
                font.bold: true;
                font.pointSize: bodyText.fontInfo.pointSize + 2;
            }
            // PlasmaExtras.Paragraph
            Text {
                id: bodyText;
                text: body;
                color: colorText;
            }
        }
        
        
        Behavior on opacity {
            PropertyAnimation {
                easing.type: Easing.InOutQuad;
                duration: fadeDuration;
            }
        }
    }
    
    MouseArea {
        id: mouseArea;
        anchors.fill: parent;
        onEntered: {
            showTimer.start();
        }
        onExited: { 
            showToolTip = false;
            showTimer.stop();
        }
        hoverEnabled: true;
    }
    
    Timer {
        id: showTimer;
        interval: toolTipSensitivity;
        onTriggered: {
            showToolTip = true;
        }
    }
}
