#!/bin/bash

# This script tries to find short or long songs and set a label in the user
# defiened field of RDLibrary

# expects MySQL credentials in file with path $MYSQL_CREDENTIALS
    
MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";

# echo $((`date --utc -d '1970-01-01 0:00:26' +%s` * 1000))

# We need a reference to the start of unix time, to count seconds
# with date
REF_DATE="1970-01-01 00:"

# Minimum, which schould be used for short songs, to exclude faulty carts
MINIMUM=1

# Which table we check or change?
TABLE="CART"

# Which row we lookup?
LENGTH="AVERAGE_LENGTH"

# Where we write our tag
TAG_FIELD="USER_DEFINED"

#what is the string for the tag
TAG_NAME="kurzersong"

# What is the group name of our music
MUSIC_NAME="MUSIK"

# DEBUG: Which rows should select choose?
ROW="${LENGTH},NUMBER,TITLE,USER_DEFINED"

# Check if there is a argument
if [ $# -eq 1 ]; then

# TODO: While und Optionen
# --query-min Suche nach Minimum
# --query-max Suche nach Maximum
# --set-min   Update Min
# --set-max   Update Max
# --dry-run   Ausgabe SQL statements
# TODO: Wollen sie das wirklich Abfrage


    # Label name of the marker from command line
    if [[ $1 =~ ([0-9]{0,2}):([0-9]{2}) ]] ; then 
        
        # Add time of argument to reference date to calculate seconds
        TIME="${REF_DATE}${1}"
	SECOND=`date --utc -d "$TIME" +%s`
        TIME_MS=$(($SECOND * 1000))
        echo $TIME_MS; 


	# Our default filter
	FILTER_SQL="WHERE ${LENGTH} BETWEEN ${MINIMUM} AND ${TIME_MS} AND GROUP_NAME LIKE '${MUSIC_NAME}' AND (${TAG_FIELD} IS NULL OR ${TAG_FIELD} NOT LIKE '%${TAG_NAME}%')"

        # Select Query for testing 
        QUERY_SQL="SELECT ${ROW} FROM ${TABLE} ${FILTER_SQL};"

	# Update Query for real life
	UPDATE_SQL="UPDATE ${TABLE} SET ${TAG_FIELD} = IFNULL(CONCAT(${TAG_FIELD},' ${TAG_NAME}'),'${TAG_NAME}') ${FILTER_SQL};"

	SQL=${QUERY_SQL}
#	SQL=${UPDATE_SQL}

	# Print SQL command, helpful to paste in mysql-client 
	echo $SQL

	# Print MySQL command
        echo "echo \"$SQL\" | mysql  --defaults-file=${MYSQL_CREDENTIALS} -h localhost Rivendell"
        # Pipe SQL command to MySQL client and print output
        echo $SQL | mysql  --defaults-file=${MYSQL_CREDENTIALS} -h localhost Rivendell
	
    else 
        echo -e "\n\terror: garbled time (FORMAT: 01:23)" >&2
        echo -e "\tusage: ${0} mm:ss\n" >&2
    fi
else
    # Error output, if not exactly one argument is given at start time
    echo -e "\n\terror: exactly one argument (length)" >&2
    echo -e "\tusage: ${0} mm:ss\n" >&2
    exit 1
fi

