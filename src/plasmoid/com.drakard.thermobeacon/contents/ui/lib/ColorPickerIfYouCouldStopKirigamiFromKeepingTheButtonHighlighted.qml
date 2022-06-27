import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

import org.kde.plasma.plasmoid 2.0
import org.kde.kirigami 2.5 as Kirigami


Button {
        
    id: colorPicker;
    
    property string labelText;
    property color picked;

    
    Kirigami.FormData.label: labelText
    text: picked;
    
    onClicked: dialog.visible = true;
    
    
    
    // Material.background:Material.Red
    palette {
        button: picked;
        buttonText: lightDark(picked, "black", "white");
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
            console.log("picked "+color);
            colorPicker.picked = color;
        }
    }
    
    function lightDark(background, lightColor, darkColor) {
        return isDarkColor(background) ? darkColor : lightColor
    }
    function isDarkColor(background) {
        var temp = Qt.darker(background, 1) // Force conversion to color QML type object
        var a = 1 - ( 0.299 * temp.r + 0.587 * temp.g + 0.114 * temp.b);
        return temp.a > 0 && a >= 0.3
    }

}
