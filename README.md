# SMS Garage Door Opener

  - Configurable **Two Factor Authentication**
  - Lock and Unlock commands over SMS
  - Photos on door open and close
  - All photos uploaded to Dropbox for easy browsing
  - Diagnostics to stay on top of the Raspberry PI, Dropbox, and Twilio
  - Usage reports emailed daily
  - Alarm to text warnings if your garage door was left open late at night

![garage-finished-product](https://cloud.githubusercontent.com/assets/4529833/19368282/4c33ce52-916d-11e6-816a-868597adec0c.png)

### Available Text Commands
  - Open
    - Opens the garage door if it is closed and not locked
  - Close
    - Closes the garage door if it is opened and not locked
  - Diagnostics
    - Emails diagnostic information from the PI, Twilio, and Dropbox
  - Help
     - Replies back with the list of possible commands
  - Lock
     - Lock the garage door which will prevent it from accepting open or close commands until unlocked
  - Unlock
     - Remove the lock on the garage door so that it will accept open and close commands (all unlock commands will issue a challenge code)
  - Photo
     - Activate the camera on the PI to take a picture and then email it to you
  - Status
     - Reply back with the current state of the garage door: opened or closed

### Shopping List
  - Rasbperry Pi 3 https://www.amazon.com/gp/product/B01C6FFNY4
  - Raspberry Pi Case https://www.amazon.com/gp/product/B00MQLB1N6
  - Pi Camera https://www.amazon.com/gp/product/B012V1HEP4
  - SanDisk Ultra 32GB microSDHC https://www.amazon.com/gp/product/B010Q57T02
  - Relay https://www.amazon.com/gp/product/B0057OC6D8
  - Case https://www.amazon.com/gp/product/B017LB9XY4

### Extended Shopping List 
  - LED Light Emitting Diodes https://www.amazon.com/gp/product/B0087ZT1VO
  - Resistors https://www.amazon.com/gp/product/B016NXK6QK
  - Breadboards https://www.amazon.com/gp/product/B01DDI54II
  - Wires https://www.amazon.com/gp/product/B00B4ZRPEY
  - Soldering Iron https://www.amazon.com/gp/product/B019BSQAS2
  - Soldering Iron Tip Cleaner https://www.amazon.com/gp/product/B005C789EU
  - PCB Circuit Boards https://www.amazon.com/gp/product/B012YZ2PXI
  - Helping Hands https://www.amazon.com/gp/product/B000RB38X8
  - Screw Mounts https://www.amazon.com/gp/product/B00EZ3QPCU
  - Terminals (for Case) https://www.amazon.com/gp/product/B00D6AICR4
  - Banana Plugs (for Case) https://www.amazon.com/gp/product/B01AH0TRTW

### Setup Rasbperry PI

###### Download Raspberry PI Operating System:
  - https://www.raspberrypi.org/downloads/noobs/
  - zip file

###### Insert Micro SDC into Windows PC
  - Right click: Format
  - Copy all contents of zip file to Micro SDC

###### Initial Boot:
  - Hookup keyboard, mouse, and HDMI monitor
  - Insert Micro SDC
  - Hookup power (wait ~5/10 minutes)

###### Initial Setup:
  - Terminal:
    - sudo apt-get update
    - sudo apt-get upgrade
  - Change any router/firewall rules to allow mac address to connect to wifi: ifconfig
  - Click top-right menu network, select SID, enter password

###### Add new user
  - sudo useradd -m YOUR_USERNAME -G sudo
  - sudo passwd YOUR_USERNAME
  - make sure this works: sudo visudo
  - sudo raspi-config   (Boot to CLI instead of desktop)
    - Boot Options
    - B1 Console
  - Restart PI
    - shutdown: sudo shutdown -r now
  - Delete default pi user
    - sudo deluser -remove-home pi
    - sudo visudo
    - Change last line from pi to YOUR_USERNAME

###### Firewall
  - sudo apt-get install ufw
  - sudo ufw allow 22   (only allow connections on ssh port)
  - sudo ufw enable

###### Locale
  - sudo raspi-config
  - Internationalisatic

###### Watchdog
  - https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=147935
  - https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=125213
  - Setup watchdog (bcm2708_wdog) or (bcm2835_wdt)?
    - sudo modprobe bcm2708_wdog
    - sudo sh -c "echo 'bcm2708_wdog' >> /etc/modules"
    - sudo apt-get install watchdog chkconfig
    - sudo chkconfig watchdog on
    - sudo service watchdog start
    - echo "options bcm2708_wdog nowayout=1 heartbeat=13" | sudo tee /etc/modprobe.d/watchdog.conf
  - Uncomment two lines in file: /etc/watchdog.conf
    - sudo vi /etc/watchdog.conf
    - watchdog-device = /dev/watchdog
    - max-load-1 = 24
   - Reboot
    - sudo reboot

###### Camera:
  - Run sudo raspi-config and choose in the menu to enable the pi camera. A reboot is needed after this
  - Install python libs:
    - sudo apt-get update
    - sudo apt-get install python3-picamera
    - sudo apt-get upgrade
    - sudo raspistill -o image.jpg
  - Turn off red light
    - sudo vi /boot/config.txt
    - disable_camera_led=1

###### Twilio:
  - Sign up
      - https://www.twilio.com/
  - Remove auto reply:
      - Go to "Manage Numbers": 
        - https://www.twilio.com/console/phone-numbers
      - Click on number
      - Replace the https:// demo link for sms with:
        - http://twimlets.com/echo?Twiml=%3CResponse%3E%3C%2FResponse%3E
  - On Raspberry PI, install libraries:
    - sudo apt-get install python3-pip
    - sudo pip3 install twilio

###### Dropbox
  - Sign up
      - https://www.dropbox.com/
  - On Raspberry PI, install libraries:
    - sudo pip3 install dropbox

## Installing and Running the Application

All scripts need to run as sudo/root in order for them to access the GPIO pins on the PI.  While I'm not a fan of scripts running as root, the workarounds are convoluted and create more complexity than is necessary.

###### Python Scripts:

  - alarm_door_open.py
      - Will send a text every time it is run if the garage door is in an open state after hours
      - Controlled via cron and set to any desired frequency.
      - Example: Run every 15 minutes between the hours of 10pm and 5am everyday.
         - ```*/15 0-5,22,23 * * * <BASE_DIR>/gd/garage-door/control.sh start alarm_door_open```
  - door_up_down.py
      - Watches the reed switch attached to the garage door in order to detect whenever it is opened or closed.
      - Runs in a continuous loop once started
  - reporting_daily.py
      - Will run a report summarizing all the commands and door state changes in the past 24 hours as well reporting each one with timestamps
      - Controlled via cron and set to any desired frequency.
      - Example: Run at 10:30pm everyday.
         - ```30 22 * * * <BASE_DIR>/gd/garage-door/control.sh start reporting_daily```
  - sms_command.py
      - Watches the twilio account for any messages sent in the past 15 minutes that have not already been processed and executes the message command
      - Runs in a continuous loop once started

###### Control Script:

A control script exists to make it easier to start, stop, and monitor the logs of all the python scripts.

  - start
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh start alarm_door_open```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh start door_up_down```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh start reporting_daily```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh start sms_command```
  - stop
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh stop alarm_door_open```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh stop door_up_down```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh stop reporting_daily```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh stop sms_command```
  - tail
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh tail alarm_door_open```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh tail door_up_down```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh tail reporting_daily```
      - ```sudo <BASE_DIR>/gd/garage-door/control.sh tail sms_command```

###### Setting Up Cron:

Anything run via cron will need entered into root's crontab:  ```sudo crontab -e```

Script | Cron Entry
------ | ----------
alarm_door_open | ```*/15 0-5,22,23 * * * <BASE_DIR>/gd/garage-door/control.sh start alarm_door_open```
door_up_down | ```@reboot <BASE_DIR>/gd/garage-door/control.sh start door_up_down```
reporting_daily | ```30 22 * * * <BASE_DIR>/gd/garage-door/control.sh start reporting_daily```
sms_command | ```@reboot <BASE_DIR>/gd/garage-door/control.sh start sms_command```

## Building Opener

##### Circuit Board

<img src="https://cloud.githubusercontent.com/assets/4529833/19371889/fda1e8ec-9184-11e6-95ff-5e5997556b52.png" width="300" height="300">

##### Wiring Guide


