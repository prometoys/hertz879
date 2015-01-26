#!/bin/bash

# This script add scheduler code for several intro times.

# expects MySQL credentials in file with path $MYSQL_CREDENTIALS
    
#MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";
MYSQL_CREDENTIALS="/srv/rivendell/my.cnf";

# Which table we check or change?
TABLE="CART, CUTS"

# Where we write our tag
TAG_FIELD="SCHED_CODES"

# What is the group name of our music
MUSIC_NAME="MUSIK"

# What subset of music we just want to tag?
TAG_FIELD_SUBSET="xTag"

# Which Ramps do we need? In seconds, separated by space
# Don't use ramps with more or less than two digits!
# Use 05 instead of 5.
RAMPS="10 15 20 30 45 60 90"

# We start with minimum time of 8 Seconds in milliseconds
MIN_TIME=8000
    
# DEBUG: Which rows should select choose?
ROW="NUMBER,TITLE,${TAG_FIELD}"

# Check if there is no argument

if [ $# -lt 2 ]; then

    FIRSTRUN=TRUE

    # Our default filter
    DEFAULT_FILTER_SQL="AND GROUP_NAME LIKE '${MUSIC_NAME}' AND NUMBER = CART_NUMBER AND CUT_QUANTITY = 1 AND ${TAG_FIELD} LIKE '%${TAG_FIELD_SUBSET}%'"

    for RAMP_TIME in $RAMPS ; do
    
        if [ $FIRSTRUN == "TRUE" ] ; then
            echo "Erster Durchlauf, mache nix."
            MIN_TIME=$((${RAMP_TIME}*1000))
            FIRSTRUN=FALSE
        else
            
            
            MAX_TIME=$((${RAMP_TIME}*1000))
        
            FILTER_SQL="WHERE TALK_END_POINT < ${MAX_TIME} AND TALK_END_POINT >= ${MIN_TIME} AND  ${TAG_FIELD} NOT LIKE '%${TAG_NAME}%'"

            # Select Query for testing 
            QUERY_SQL="SELECT ${ROW} FROM ${TABLE} ${FILTER_SQL}  ${DEFAULT_FILTER_SQL};"

            # Update Query for real life
            UPDATE_SQL="UPDATE ${TABLE} SET ${TAG_FIELD} = REPLACE(${TAG_FIELD},'.',CONCAT('${TAG_NAME}','.')) ${FILTER_SQL} ${DEFAULT_FILTER_SQL};"

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
            elif [ ""$1 == "--search" ]; then
                echo "# Just showin query for search, to examine affected datasets. use | grep -v UPDATE to filter noise."
                #TODO better option parser 
                echo ${QUERY_SQL}
            fi
            # Set current max time as new min time
            MIN_TIME=$MAX_TIME
        fi
        TAG_NAME="aRampe${RAMP_TIME}   "
        
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

    


