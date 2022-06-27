import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml 2.15

import org.kde.plasma.plasmoid 2.0
import org.kde.kirigami 2.5 as Kirigami

import "../lib"


Kirigami.FormLayout {
    id: configGeneralPage;

    // ------------------------------------------------------------------------------------------------------------------------

    property alias cfg_showAlias : showAlias.checked;
    property alias cfg_aliasBackgroundColor : aliasBackgroundColor.picked;
    
    property alias cfg_temperatureBackgroundColor : temperatureBackgroundColor.picked;
    property alias cfg_temperatureUnitSelected : temperatureUnitSelected.currentIndex;
    property alias cfg_temperatureDecimals : temperatureDecimals.value;
    property alias cfg_showTemperatureUnits : showTemperatureUnits.checked;
    
    property alias cfg_showHumidity : showHumidity.checked;
    property alias cfg_humidityBackgroundColor : humidityBackgroundColor.picked;
    property alias cfg_humidityDecimals : humidityDecimals.value;
    property alias cfg_showHumidityPercent : showHumidityPercent.checked;
    
    
    // ------------------------------------------------------------------------------------------------------------------------
    
    Item {
        Kirigami.FormData.label: i18n("Beacon Alias");
        Kirigami.FormData.isSection: true;
    }
    
    CheckBox {
        id: showAlias;
        Kirigami.FormData.label: i18n("Show");
        checked: plasmoid.configuration.showAlias;
    }
    
    ColorPicker {
        id: aliasBackgroundColor;
        labelText: i18n("Background");
        picked: cfg_aliasBackgroundColor;
    }
    
    
    // ------------------------------------------------------------------------------------------------------------------------
    
    Item {
        Kirigami.FormData.label: i18n("Temperature");
        Kirigami.FormData.isSection: true;
    }
    
    ColorPicker {
        id: temperatureBackgroundColor;
        labelText: i18n("Background");
        picked: cfg_temperatureBackgroundColor;
    }
    
    
    
    ComboBox {
        id: temperatureUnitSelected;
        width: 200
        Kirigami.FormData.label: i18n("Temperature Units");
        model: plasmoid.configuration.temperatureUnits;
        //onCurrentIndexChanged: plasmoid.configuration.temperatureUnitSelected = temperatureUnitSelected.currentIndex;
    }
    
    SpinBox {
        id: temperatureDecimals;
        Kirigami.FormData.label: i18n("Decimal Places");
        valueFromText: function(text) {
            return parseInt(text);
        }
        from: 0;
        to: 3;
    }
    
    CheckBox {
        id: showTemperatureUnits;
        Kirigami.FormData.label: i18n("Show Unit");
        checked: plasmoid.configuration.showTemperatureUnits;
    }
    
    // ------------------------------------------------------------------------------------------------------------------------
    
    Item {
        Kirigami.FormData.label: i18n("Humidity");
        Kirigami.FormData.isSection: true;
    }
    
    CheckBox {
        id: showHumidity;
        Kirigami.FormData.label: i18n("Show Humidity");
        checked: plasmoid.configuration.showHumidity;
    }
    
    ColorPicker {
        id: humidityBackgroundColor;
        labelText: i18n("Background");
        picked: cfg_humidityBackgroundColor;
    }
    
    SpinBox {
        id: humidityDecimals;
        visible: showHumidity.checked;
        Kirigami.FormData.label: i18n("Decimal Places");
        valueFromText: function(text) {
            return parseInt(text);
        }
        from: 0;
        to: 3;
    }
    
    CheckBox {
        id: showHumidityPercent;
        visible: showHumidity.checked;
        Kirigami.FormData.label: i18n("Show %");
        checked: plasmoid.configuration.showHumidityPercent;
    }
    
}
