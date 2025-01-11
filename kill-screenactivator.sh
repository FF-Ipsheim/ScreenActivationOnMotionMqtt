#!/bin/bash

# get all pid's of running instances of:
# ScreenActivationOnMotionMqtt/main.py
list=$(pgrep -f ScreenActivationOnMotionMqtt/main.py)


# terminate all instances stored in $list:
for pid in $list
do
  echo "killing process $pid..."
  kill -TERM $pid
done

exit 0
