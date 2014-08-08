#!/bin/bash

# This script tries to load the log (aka playlist) for today and start
# the log afterwards. If a marker name is suplied, it tries to start
# jump to this marker, otherwise it starts with the third item (Line 2) 
# to avoid events at the beginning of the list, like scheduled shows.


# FAILSAFE load line 2, if we didn't have or find the marker
LOG_LINE=2
# TODO: get line 

# get the date in the form Rivendell use it: 2014_08_31
NOW_DATE=$(date +%Y_%m_%d)

ID="None"

# Accept a marker name
if [ $# -gt 0 ]; then
  MARKER_NAME=$1
  SQL='SELECT ID FROM '${NOW_DATE}'_LOG L WHERE COMMENT LIKE "%'${MARKER_NAME}'%"'
  ID=$(echo $SQL | mysql -h localhost Rivendell | grep -v ID)
fi

# Check, Number
REGEXP_NUMBER='^[0-9]+$'
if [[ $ID =~ $REGEXP_NUMBER ]] ; then
   LOG_LINE=$ID
   echo "error: Not a number" >&2; exit 1
fi

# Load the Log from today.
# LL <mach> <logname>
#
# mach: 1=Main Log (we only use the main log)
echo rmlsend "LL 1 $NOW_DATE"!

# TODO: Check: Necessary to set the next event? 
# rmlsend "MN 1 $LOG_LINE"!

# 
echo rmlsend "PL 1 $LOG_LINE"!

# Now we set the playmode back to automatic, in the case the presenter
# forgot to change it after the show.

# PM: Set RDAirplay Mode:
# 1 = LiveAssist, 2 = Auto, 3 = Manual.
echo rmlsend "PM 2"!



