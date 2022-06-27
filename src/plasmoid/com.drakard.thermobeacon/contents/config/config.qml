
import QtQuick 2.15

import org.kde.plasma.configuration 2.0

ConfigModel {

    ConfigCategory {
         name: i18nc("@title", "Appearance")
         icon: "preferences-desktop-color"
         source: "config/Appearance.qml"
    }
    
    ConfigCategory {
         name: i18nc("@title", "Network")
         icon: "preferences-system-network"
         source: "config/Network.qml"
    }

}
 
