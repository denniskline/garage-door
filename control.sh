#!/bin/bash
# ----------------------------------------------------------------------
# Program: control.sh
#
# Purpose: Use to start/stop/tail (control) the garage door scripts that need to run as services
# 
# Usage: control.sh start door_up_down
#        control.sh start all
#        control.sh stop all
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
ACTION=$1
if [ "$ACTION" == "help" ] ; then
    echo "USAGE:"
    echo "$0 [command] [service name|all]"
    echo "$0 [start|stop|tail] [door_up_down|sms_command|reporting_daily|alarm_door_open]"
    echo "-----------------------------------------"
    exit 0
fi

# ----------------------------------------------------------------------
SERVICE_DIR=$HOME/gd/garage-door
LOG_DIR=/var/local/gd/log

declare -a SERVICES=(door_up_down sms_command reporting_daily alarm_door_open)

while [ "$ACTION" != "start" ] && [ "$ACTION" != "stop" ] && [ "$ACTION" != "tail" ] && [ "$ACTION" != "clean" ]; do
    read -p "What would you like to do [start or stop or tail or clean] groot services? " ACTION
done

# ----------------------------------------------------------------------
if [ "$ACTION" == "start" ]; then
    SERVICE_NAME=$2
    if [ -z "$SERVICE_NAME" ]; then
        read -p "Start which service (default: all)? " SERVICE_NAME
        SERVICE_NAME=${SERVICE_NAME:-all}
    fi

    if [ "$SERVICE_NAME" == "all" ]; then
        for srvs in ${SERVICES[@]}
        do
            GD_SERVICE="$srvs"
            echo "Starting node: $GD_SERVICE"
            date >> $LOG_DIR/$GD_SERVICE.nohup
            echo "Starting node: $GD_SERVICE" >> $LOG_DIR/$GD_SERVICE.nohup
            nohup $SERVICE_DIR/$GD_SERVICE.py --configdirectory=$SERVICE_DIR/conf >> $LOG_DIR/$GD_SERVICE.nohup 2>&1 &
            sleep 1
        done
    else
        GD_SERVICE="$SERVICE_NAME"
        date >> $LOG_DIR/$GD_SERVICE.nohup
        echo "Starting node: $GD_SERVICE" >> $LOG_DIR/$GD_SERVICE.nohup
        nohup $SERVICE_DIR/$GD_SERVICE.py --configdirectory=$SERVICE_DIR/conf >> $LOG_DIR/$GD_SERVICE.nohup 2>&1 &
    fi        

# ----------------------------------------------------------------------
elif [ "$ACTION" == "stop" ]; then
    SERVICE_NAME=$2
    if [ -z "$SERVICE_NAME" ]; then
        read -p "Stop which service (default: all)? " SERVICE_NAME
        SERVICE_NAME=${SERVICE_NAME:-all}
    fi

    if [ "$SERVICE_NAME" == "all" ]; then
        for srvs in ${SERVICES[@]}
        do
            GD_SERVICE="$srvs"
            echo "Stopping $GD_SERVICE ..."
            ps -ef | grep -i $GD_SERVICE | grep -iv grep | grep python3 | awk "{print \$2}" | xargs kill
            sleep 1
        done
    else
        GD_SERVICE="$SERVICE_NAME"
        echo "Stopping $GD_SERVICE ..."
        ps -ef | grep -i $GD_SERVICE | grep -iv grep | grep python3 | awk "{print \$2}" | xargs kill
    fi

# ----------------------------------------------------------------------
elif  [ "$ACTION" == "tail" ]; then
    SERVICE_NAME=$2
    if [ -z "$SERVICE_NAME" ]; then
        read -p "Tail which service (default: all)? " SERVICE_NAME
        SERVICE_NAME=${SERVICE_NAME:-all}
    fi

    if [ "$SERVICE_NAME" == "all" ]; then
        echo "Tailing all services ..."
        for srvs in ${SERVICES[@]}
        do
            GD_SERVICE="$srvs"
            if [ -a $LOG_DIR/$GD_SERVICE.log ]; then
                echo "Service: $GD_SERVICE ::"
                tail -1 $LOG_DIR/$GD_SERVICE.log
                echo "-----------------------------------------"
            fi
        done
    else
        GD_SERVICE="$SERVICE_NAME"
        if [ -a $LOG_DIR/$GD_SERVICE.log ]; then
            tail -f $LOG_DIR/$GD_SERVICE.log
        else
            echo "File does not exist to tail: $LOG_DIR/$GD_SERVICE.log .  Did you start that service?  $0 start $GD_SERVICE"
        fi
    fi

# ----------------------------------------------------------------------
else 
    echo "Unknown command"
fi
