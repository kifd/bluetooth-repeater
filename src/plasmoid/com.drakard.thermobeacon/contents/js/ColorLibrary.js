// mark as a library that doesn't need shared access to the qml objects
// https://doc.qt.io/qt-5/qtqml-javascript-resources.html
.pragma library



function getContrastingColor(toThisOne) {
    return isDark(toThisOne) ? "white" : "black";
}


// https://stackoverflow.com/a/56678483 by https://stackoverflow.com/users/10315269/myndex
function isDark(color) {
    var t = Qt.darker(color, 1); // conversion to color QML type object (rgb = 0.0-1.0)
    var y = getLuminance(t);
    var lstar = YtoLstar(y);
    //console.log(color, t, y, lstar);
    return (lstar < 50);
}

// takes a decimal sRGB object, and returns the luminance
function getLuminance(sRGB) {
    return (0.2126 * sRGBtoLin(sRGB.r) + 0.7152 * sRGBtoLin(sRGB.g) + 0.0722 * sRGBtoLin(sRGB.b));
}

// takes a channel color value between 0.0 and 1.0, and returns a linearized value
function sRGBtoLin(channel) {
    return (channel <= 0.04045) ? channel / 12.92 : Math.pow(((channel + 0.055) / 1.055), 2.4);
}

// takes a luminance value between 0.0 and 1.0, and returns the L* ("perceptual lightness" between 0-100)
function YtoLstar(Y) {
    return (Y <= (216/24389)) ? Y * (24389/27) : Math.pow(Y, (1/3)) * 116 - 16;
}
