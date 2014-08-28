#!/bin/bash

# This script checks, if the new event is empty and updates the message bay

# Check if there is a argument
if [ $# -gt 0 ]; then

    if ! [[ $@ = "-" ]] ;then
        SONG=$@
        echo 'rmlsend "LB '$SONG' "!'
        rmlsend "LB $SONG "!
        echo $SONG > /tmp/lastsong
    else
        SONG="Das war: `cat /tmp/lastsong`"
        if ! [[ SONG = "Das war: " ]] ;then
            echo 'rmlsend "LB '$SONG' "!'
            rmlsend "LB $SONG "!
        fi
    fi
else
    # Error output, if more then one argument is given at start time
    echo -e "\n\terror: at least. one argument (track info) \n" >&2
    exit 1
fi

