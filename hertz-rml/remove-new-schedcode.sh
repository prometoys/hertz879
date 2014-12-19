#!/bin/bash

# This script deletes the scheduler code for new songs.

# expects MySQL credentials in file with path $MYSQL_CREDENTIALS
    
MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";

# Which table we check or change?
TABLE="CART"

# Where we write our tag
TAG_FIELD="SCHED_CODES"

# What is the string for the tag
# must be exactly 11 chars long
#        '           '
TAG_NAME="rNeu       "

# What is the group name of our music
MUSIC_NAME="MUSIK"

# DEBUG: Which rows should select choose?
ROW="NUMBER,TITLE,${TAG_FIELD}"

# Check if there is no argument
if [ $# -lt 2 ]; then

    # TODO:
    # echo " test test test " | tr -d ' '

    TAG_SEARCH="$(echo ${TAG_NAME} | tr -d ' ')"

    # Our default filter
    FILTER_SQL="WHERE GROUP_NAME LIKE '${MUSIC_NAME}' AND ${TAG_FIELD} LIKE '%${TAG_SEARCH}%'"

    # Select Query for testing 
    QUERY_SQL="SELECT ${ROW} FROM ${TABLE} ${FILTER_SQL};"

    # Update Query for real life
    UPDATE_SQL="UPDATE ${TABLE} SET ${TAG_FIELD} = REPLACE(${TAG_FIELD},'${TAG_NAME}','') ${FILTER_SQL};"

    # SQL=${QUERY_SQL}
    SQL=${UPDATE_SQL}

    # Print SQL command, helpful to paste in mysql-client 

    echo $SQL

    # Check if script was started with ' --perform' 
    # We only change database, with this to avoid modifications
    # when somebody just test the script or find it in $PATH
    if [ ""$1 == "--perform" ]; then

        # Print MySQL command
        # echo "echo \"$SQL\" | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell"

        # Pipe SQL command to MySQL client and print output
        echo $SQL | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell

    else

        echo "Just showing Query, doing nothing. Use '$0 --perform' to run query." 

    fi	

else
    # Error output, if not exactly one argument is given at start time
    echo -e "\n\terror: Not more then one argument allowed" >&2
    echo -e "\terror: usage: '${0} [--perform]' \n" >&2
    exit 1
fi
