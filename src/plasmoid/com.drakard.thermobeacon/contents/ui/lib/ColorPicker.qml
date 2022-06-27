import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

import org.kde.plasma.plasmoid 2.0
import org.kde.kirigami 2.5 as Kirigami

import "../../js/ColorLibrary.js" as JS


Item {
        
    id: colorPicker;
    
    property string labelText;
    property color picked;
    
    property int paddingX: 14;
    property int paddingY: 12;
    
    
    height: buttonText.height + (paddingY * 2);
    
    
    Kirigami.FormData.label: labelText;
    
    
    Rectangle {
        id: button;
        width: buttonText.width + paddingX;
        height: buttonText.height + paddingY;
        
        radius: (height / 100) * 8;
        //x: + (paddingX / 2);
        y: - (height / 2);
        
        color: picked;
        border.color: picked;
        border.width: 2;
        //anchors.verticalCenter: parent.verticalCenter;
        
        Text {
            id: buttonText;
            anchors.centerIn: button;
            
            text: picked;
            color: JS.getContrastingColor(picked);
        }
    
        MouseArea {
            anchors.fill: button;
            hoverEnabled: true;
            cursorShape: Qt.PointingHandCursor;
            /*onEntered: {
                //button.color = Kirigami.Theme.buttonHoverColor;
            }
            onExited: {
                button.color = picked;
            }*/
            onClicked: {
                dialog.visible = true;
            }
        }
    }
    
    
    ColorDialog {
        id: dialog;
        title: i18n("%1 %2 Color", plasmoid.title, labelText);
        color: colorPicker.picked;
        
        onColorChanged: {
            //console.log("current "+currentColor);
            //colorPicker.picked = currentColor;
        }
        onAccepted: {
            //console.log("picked "+color);
            colorPicker.picked = color;
        }
    }
    

}
