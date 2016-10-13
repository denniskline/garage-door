# SMS Garage Door Opener

  - Configurable **Two Factor Authentication**
  - Lock and Unlock commands over SMS
  - Photos on door open
  - Dropbox tie-in of photos for easy access
  - Diagnostics to stay on top of the Raspberry PI and your dropbox and twilio accounts
  - Usage reports emailed daily

[https://cloud.githubusercontent.com/assets/4529833/19367969/b4a06dee-916b-11e6-8298-798a88cfdbe7.JPG]

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

###### Download Raspberry PI Operatin System:
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


