#!/bin/bash

# Time to blink in seconds (if you don't change the sleep statements )
LAST=20

# Color for the LC command
# possible values: white black red darkRed green darkGreen blue darkBlue cyan
# darkCyan magenta darkMagenta yellow darkYellow gray darkGray lightGray

COLOR=yellow

# Force Automatic Mode
# PM: Set RDAirplay Mode:
# 1 = LiveAssist, 2 = Auto, 3 = Manual.
rmlsend "PM 2"!

# Blink the String in the message widget of RDAirplay
I=0
while [ $I -lt $LAST ]
do 
  rmlsend "LB"! 
  sleep 0.3
  rmlsend "LC $COLOR ACHTUNG AUTOMATIK, DLF"!
  sleep 0.7
  I=$(($I+1))
done
