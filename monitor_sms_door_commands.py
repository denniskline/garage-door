#!/usr/bin/python3

# Basic imports
from configparser import SafeConfigParser
import os
import datetime
from operator import itemgetter
import logging

# Library imports
from gdmod import ApplicationConfiguration
from gdmod import Authorization
from gdmod import Challenge
from gdmod import Database
from gdmod import Email
from gdmod import NetworkDownException
from gdmod import Pi
from gdmod import Sms
from gdmod import GarageDoorCommand

# Pull in the configuration for this application
config = SafeConfigParser(os.environ)
config.read('conf/door.ini')
appConfig = ApplicationConfiguration(config)

accountConfig = SafeConfigParser(os.environ)
accountConfig.read('conf/account-settings.ini')
appAccountConfig = ApplicationConfiguration(accountConfig)

# Setup logger
logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', 
    filename=appConfig.get('sms.door.command.log.file.directory') + '/' + appConfig.get('sms.door.command.log.file.name'), level=logging.INFO)

# Instantiate all the required modules
az = Authorization(appConfig.get('sms.door.command.allowed.phonenumbers'))
db = Database(appConfig.get('app.database.file'))
sms = Sms(db, appAccountConfig.get('sms.account.id'), appAccountConfig.get('sms.account.token'), appAccountConfig.get('sms.account.phone.number'))
pi = Pi()
email = Email(appConfig.get('door.email.address'), appConfig.get('door.email.pword'))
challenge = Challenge(appConfig, db, sms, email)
command = GarageDoorCommand(db, challenge, pi, sms, email)

try:
    # Visual indicator that work is being performed
    pi.blink_green_light(.5)

    # fetch all the new messages that need processing
    messages = sms.list()

    # Handle contradictory commands: Open followed by a Close.  Only process the last state change command
    # This is hard to do due to challenges.  If every message is a challenge response that could lead to an open or close then ????
    #lastOpenOrClose = [d for d in messages if get_message_body(d) == "close" or get_message_body(d) == "open"][-1]
    #print('found an open or close message: {}'.format(lastOpenOrClose))

    for message in messages: 

        # regardless of any error or invalid command, save off the message for audit trail and so it is never reprocessed
        db.insert_text_message(message) 

        # Make sure that this message is authorized
        if not az.is_authorized(message):
            logging.warn('Unauthorized attempt detected: {}'.format(message))
            db.update_text_message_status(message.get('sid'), 'unauthorized')
            continue

        command.execute(message)

    # Clear any warn/error indicators
    pi.off_yellow_light()
    pi.off_red_light()
except NetworkDownException as nde:
    logging.error('Unable to reach network, cannot process messages', exc_info=True)
    pi.blink_yellow_light(.5)
except:
    logging.error('Failure processing messages', exc_info=True)
    pi.blink_red_light(.5)
finally:
    # Toggle off the visual indicator that work is being performed
    pi.off_green_light()
