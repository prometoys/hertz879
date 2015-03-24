#!/bin/bash

# This script add a string for short songs, to find them easier.

# expects MySQL credentials in file with path $MYSQL_CREDENTIALS
    
#MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";
MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";

# Which table we check or change?
TABLE="CART, CUTS"

# Where we write our string
STRING_FIELD="USER_DEFINED"

# What is the name of our string?
STRING_NAME="kurzersongs"

# Where are the Scheduler codes for further limiting
TAG_FIELD="SCHED_CODES"

# We just want to add this string to easy listening songs ;)
TAG_NAME="xTag"

# What is the group name of our music
MUSIC_NAME="MUSIK"

# How long is short song (in ms)? We use 2min = 120000 milliseconds
MAX_TIME=120000

# DEBUG: Which rows should select choose?
ROW="NUMBER,TITLE,${TAG_FIELD}, ${STRING_FIELD}"

# Check if there is no argument

if [ $# -lt 2 ]; then

    # Our default filter
    DEFAULT_FILTER_SQL="AND GROUP_NAME LIKE '${MUSIC_NAME}' AND NUMBER = CART_NUMBER AND CUT_QUANTITY = 1"

    FILTER_SQL="WHERE CUTS.LENGTH <= ${MAX_TIME} AND ${TAG_FIELD} LIKE '%${TAG_NAME}%' AND ${STRING_FIELD} NOT LIKE '%${STRING_NAME}%' "

    # Select Query for testing 
    QUERY_SQL="SELECT ${ROW} FROM ${TABLE} ${FILTER_SQL}  ${DEFAULT_FILTER_SQL};"

    # Update Query for real life
    UPDATE_SQL="UPDATE ${TABLE} SET ${STRING_FIELD} = CONCAT(${STRING_FIELD}, ' ${STRING_NAME}') ${FILTER_SQL} ${DEFAULT_FILTER_SQL};"

#USER_DEFINED = concat(USER_DEFINED, concat(' 5fadeprob2015 ', FADEDOWN_POINT)),

    # SQL=${QUERY_SQL}
    SQL=${UPDATE_SQL}

    # Print SQL command, helpful to paste in mysql-client 

    echo "$SQL"

    # Check if script was started with ' --perform' 
    # We only change database, with this to avoid modifications
    # when somebody just test the script or find it in $PATH
    if [ ""$1 == "--perform" ]; then

        # Print MySQL command
        # echo "echo \"$SQL\" | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell"

        # Pipe SQL command to MySQL client and print output
        echo "$SQL" | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell
    fi
    
    if [ ""$1 != "--perform" ]; then
        echo "Just showing Query, doing nothing. Use '$0 --perform' to run query." 
    fi
else
    # Error output, if not exactly one argument is given at start time
    echo -e "\n\terror: Not more then one argument allowed" >&2
    echo -e "\terror: usage: '${0} [--perform]' \n" >&2
    exit 1
fi


