#!/bin/bash

# This script tries to load the log (aka playlist) for today and start
# the log afterwards. If a marker name is suplied, it tries to start
# jump to a marker with this label, otherwise it starts with the third 
# item (Line 2) to avoid events at the beginning of the list, like scheduled
# shows.

# expects MySQL credentials in ~/.my.cnf


# FAILSAFE load line 2, if we didn't have or find the marker
LOG_LINE=2
# TODO: get line 

# get the date in the form Rivendell use it: 2014_08_31
NOW_DATE=$(date +%Y_%m_%d)

# Check if there is a argument
if [ $# -eq 1 ]; then

    # Label name of the marker from command line
    MARKER_LABEL=$1
    
    # In which row we should lookup the number (ID or COUNT)?
    ROW="COUNT"
    
    # SQL Code to search for a line with the specified label
    SQL='SELECT '$ROW' FROM '${NOW_DATE}'_LOG L WHERE LABEL LIKE "%'${MARKER_LABEL}'%"'
    
    # only take the first found line number. 
    ID=$(echo $SQL | mysql -h localhost Rivendell | grep  '^[0-9]\+$' | head -n 1)
    
    # Test expression for positive integer numbers
    REGEXP_NUMBER='^[0-9]+$'

    # if the found ID is a number, save it as new value in $LOG_LINE
    if [[ $ID =~ $REGEXP_NUMBER ]] ; then
        LOG_LINE=$ID
    else
        echo "error:[${ID}] Not a number" >&2; exit 1
    fi
    
elif [ $# -gt 1 ]; then
    # Error output, if more then one argument is given at start time
    echo -e "\n\terror: max. one argument (marker label allowed)" >&2
    echo -e "\n\tusage: ${0} [MARKER_LABEL]}\n" >&2
    exit 1
fi

# Load the Log from today.
# LL <mach> <logname> <start-line>
#
# mach: 1=Main Log (we only use the main log)
# logname: Date with underscores e.g. 2014_08_31
echo rmlsend "LL 1 $NOW_DATE $LOG_LINE"!

# Wait, until Rivendell load the playlist
sleep 1

# MN <mach> <line>!
# TODO: Check: Necessary to set the next event? 
# rmlsend "MN 1 $LOG_LINE"!

# TODO: Check: WRONG: we dont want to use PL
# it only works, when rdairplay is not playing
# echo rmlsend "PL 1 $LOG_LINE"!

# Finally, we set the playmode back to automatic, in the case the presenter
# forgot to change it after the show.

# PM: Set RDAirplay Mode:
# 1 = LiveAssist, 2 = Auto, 3 = Manual.
echo rmlsend "PM 2"!



