
import QtQuick 2.15
import QtGraphicalEffects 1.13


Item {
    id: circle;
    
    // ------------------------------------------------------------------------------------------------------------------------

    property string text: "?";
    
    property color colorInfill: "gray";
    property color colorBorder: "black";
    property color colorText: "white";
    
    property int sizeMain: 100;
    property int sizeBorder: 8;
    property int sizeText: 24;
    property int sizePadding: 0;
    
    // If we're using software rendering, draw outlines instead of shadows
    // See https://bugs.kde.org/show_bug.cgi?id=398317
    readonly property bool softwareRendering: GraphicsInfo.api === GraphicsInfo.Software
    property bool showShadow: false;
    
    property var anchorObject: parent;
    property bool anchorOnCircumference: false;
    property int anchorAngle: 0;
    
    
    // ------------------------------------------------------------------------------------------------------------------------

    
    
    function getRadius() {
        return inner.width * 0.5;
    }
    
    function getTextHeight() {
        return innerText.fontInfo.pixelSize;
    }


    /*
    // 0 degrees in QML = east / 3 o'clock / due right...
    function circularAnchorX(radius, degrees) {
        return (radius * Math.cos((Math.PI/180) * degrees));
    }
    function circularAnchorY(radius, degrees) {
        return (radius * Math.sin((Math.PI/180) * degrees));
    }
    
    Component.onCompleted: {
        anchors.centerIn = anchorObject.centerIn;
            
        if (anchorOnCircumference) {
            
            anchors.horizontalCenterOffset = circularAnchorX(anchorObject.getRadius(), anchorAngle)
            anchors.verticalCenterOffset = circularAnchorY(anchorObject.getRadius(), anchorAngle)
            console.log(anchorObject.getRadius(), x,y);
            
        }
    }
    */
    
    
    
    // ------------------------------------------------------------------------------------------------------------------------

    
    
    Rectangle {
        id: inner;
        
        color: circle.colorInfill;
        
        radius: circle.sizeMain * 0.5;
        width: circle.sizeMain - sizePadding;
        height: width;
        
        border {
            color: circle.colorBorder;
            width: circle.sizeBorder;
        }
        anchors {
            horizontalCenter: circle.horizontalCenter;
            verticalCenter: circle.verticalCenter;
        }
        
        z: 1;
        
    }
    
    Text {
        id: innerText;
        
        text: circle.text; // +":"+circle.sizeMain.toFixed(0);
        
        anchors {
            fill: inner;
            leftMargin: circle.sizeMain * 0.18;
            rightMargin: circle.sizeMain * 0.18;
            topMargin: units.smallSpacing * 2;
            bottomMargin: units.smallSpacing * 2;
        }
        horizontalAlignment: Text.AlignHCenter;
        verticalAlignment: Text.AlignVCenter;
        
        elide: Text.ElideRight;
        fontSizeMode: Text.HorizontalFit;
        minimumPixelSize: circle.sizeText;
        font.pixelSize: circle.sizeText * 8;
        color: circle.colorText;
        
        z: 1;
    }
    
    
    DropShadow {
        id: shadow;
        anchors.fill: inner;
        source: inner;
        visible: !softwareRendering & showShadow;
        radius: sizePadding * 0.75;
        samples: 21;
        spread: 0.3;
        color: circle.colorBorder;
        z: 0;
    }
    
    /*
    transform: Scale {
        origin.x: x + (width / 2);
        origin.y: y + (height / 2);
        xScale: 1;
        yScale: xScale;
    }*/
    
}
