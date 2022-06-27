#!/usr/bin/env bash

# delete the old plasmoid
rm -rf ~/.local/share/plasma/plasmoids/com.drakard.thermobeacon/

# install the update
kpackagetool5 -t Plasma/Applet -i ../src/plasmoid/com.drakard.thermobeacon

# restart plasma to flush the qml cache
kquitapp5 plasmashell
kstart5 plasmashell </dev/null &>/dev/null &
