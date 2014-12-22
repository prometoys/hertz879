#!/bin/bash

# This script checks, if the new event is empty and updates the message bay
LASTSONG=/tmp/lastsong
LOGFILE=/tmp/setlabel.log
DEBUG=TRUE

MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";

#function debug {
# print a log a message
log () {
	DATE=$(date +"%Y-%m-%d %H:%M:%S %z")
	echo "$DATE: $@" >&2 >>  $LOGFILE
}

log "running set-label"

# 
touch $LASTSONG
chmod g+w  $LASTSONG
touch $LOGFILE
chgrp rivendell  $LOGFILE
chmod g+w  $LOGFILE 

# Check if there is a argument
if [ $# -gt 0 ]; then

    # Check, if the submitted string is not empty
    # Format is artist-title, if artist and title are empty
    # the string contains only "-"
    # if ! [[ $@ = "-" ]] ;then
	# Put th full string [artist-title] in the variable
	NUMBER=$@
        
        TABLE="CART"
        ROW="ARTIST,TITLE"
        
        SQL='SELECT '$ROW' FROM '${TABLE}' WHERE  NUMBER='${NUMBER}''
        
#        echo "SELECT ARTIST,TITLE FROM CART WHERE NUMBER=300048" | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell | tail -n1 |  sed -e 's/^ *//' -e 's/ *$//' | sed -e 's/\t/ - /'
	echo $SQL
        SONG=$(echo $SQL | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell |  tail -n1 |  sed -e 's/^ *//' -e 's/ *$//' | sed -e 's/\t/ - /')
        log 'newsong: rmlsend "LB '$SONG' "!'
        # Send the 
        rmlsend "LB $SONG "!
        echo $SONG >  $LASTSONG
    else
        SONG="Das war: `cat  $LASTSONG`"
        if ! [[ SONG = "Das war: " ]] ;then
            log 'daswar:  rmlsend "LB '$SONG' "!'
            rmlsend "LB $SONG "!
        else
	    log "failed-daswarcheck: $SONG"
	fi
    fi
#else
#    # Error output, if more then one argument is given at start time
#    echo -e "\n\terror: at least. one argument (track info) \n" >&2
#    log "error: at least. one argument (track info)" 
#    exit 1
#fi
