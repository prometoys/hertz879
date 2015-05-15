#!/bin/bash

# Start RDAirplay
rdairplay &

# Wait until RDAirplay is probably ready
sleep 2

# Activate ON AIR Flag
rmlsend "TA 1"!

# Load the log of today at now position.
/usr/local/bin/load-today-log.sh `date +%H:%M`

# Disable gnome screen blanking, if needed.
gsettings set org.gnome.settings-daemon.plugins.power sleep-display-ac 0
gsettings set org.gnome.desktop.session idle-delay 0
