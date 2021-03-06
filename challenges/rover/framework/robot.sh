#!/bin/bash


if [[ $BROKER ]] ; then
    echo "broker set $BROKER"
else
    BROKER="10.10.10.30"
    echo "use default broker ip $BROKER"
fi

if [[ $PORT ]] ; then
    echo "port set $PORT"
else
    PORT="1883"
    echo "use default broker port $PORT"
fi

python3 run_ev3robot.py --broker $BROKER --port $PORT