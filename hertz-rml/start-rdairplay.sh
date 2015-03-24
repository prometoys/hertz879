#!/bin/bash
set +x

rdairplay &

sleep 2

/usr/local/bin/load-today-log.sh `date +%H:%M`

gsettings set org.gnome.settings-daemon.plugins.power sleep-display-ac 0
gsettings set org.gnome.desktop.session idle-delay 0
