#!/bin/bash

# This script add scheduler code for several intro times.

# expects MySQL credentials in file with path $MYSQL_CREDENTIALS
    
MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";

# Which table we check or change?
TABLE="CART, CUTS"

# Where we write our tag
TAG_FIELD="SCHED_CODES"

# What is the group name of our music
MUSIC_NAME="MUSIK"

# Which Ramps do we need? In seconds, separated by space
# Don't use ramps with more or less than two digits!
# Use 05 instead of 5.
RAMPS="10 15 20 30 45 60"
    
# DEBUG: Which rows should select choose?
ROW="NUMBER,TITLE,${TAG_FIELD}"

TAG_PREFIX="aRampe"

# Check if there is no argument

if [ $# -lt 2 ]; then

    # Our default filter
    DEFAULT_FILTER_SQL="WHERE GROUP_NAME LIKE '${MUSIC_NAME}' AND NUMBER = CART_NUMBER AND CUT_QUANTITY = 1 AND  ${TAG_FIELD} LIKE '%${TAG_PREFIX}%'"

    for RAMP_TIME in $RAMPS ; do
        TAG_NAME="${TAG_PREFIX}${RAMP_TIME}   "
        
        # Select Query for testing 
        QUERY_SQL="SELECT ${ROW} FROM ${TABLE} ${DEFAULT_FILTER_SQL};"

        # Update Query for real life
        UPDATE_SQL="UPDATE ${TABLE} SET ${TAG_FIELD} = REPLACE(${TAG_FIELD},'${TAG_NAME}','') ${DEFAULT_FILTER_SQL};"

        # SQL=${QUERY_SQL}
        SQL=${UPDATE_SQL}

        # Print SQL command, helpful to paste in mysql-client 

        echo "$SQL"

        # Check if script was started with ' --perform' 
        # We only change database, with this to avoid modifications
        # when somebody just test the script or find it in $PATH
        if [ ""$1 == "--perform" ]; then

            # Print MySQL command
            # echo "echo \"$SQL\" | mysql  --defaults-file=${MYSQL_CREDENTIALS} -h localhost Rivendell"

            # Pipe SQL command to MySQL client and print output
            echo "$SQL" | mysql  --defaults-file=${MYSQL_CREDENTIALS} Rivendell
        fi
        
    done
    if [ ""$1 != "--perform" ]; then
        echo "Just showing Query, doing nothing. Use '$0 --perform' to run query." 
    fi
else
    # Error output, if not exactly one argument is given at start time
    echo -e "\n\terror: Not more then one argument allowed" >&2
    echo -e "\terror: usage: '${0} [--perform]' \n" >&2
    exit 1
fi

    


