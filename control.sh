#!/bin/bash

nohup /home/sedhawk/gd/garage-door/sms_command.py --configdirectory=/home/sedhawk/gd/garage-door/conf > /var/local/gd/log/sms_command.nohup 2>&1 &

