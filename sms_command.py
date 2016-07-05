#!/usr/bin/python3

import os
import datetime
import time
import logging
import getopt
import sys
from gdmod import ApplicationConfiguration
from gdmod import Authorization
from gdmod import Challenge
from gdmod import Database
from gdmod import Email
from gdmod import NetworkDownException
from gdmod import Pi
from gdmod import Sms
from gdmod import GarageDoorCommand
from gdmod import Dropbox

def main():
    # Check command options to see if a custom configuration directory was supplied
    configDir = os.path.abspath(get_config_directory(sys.argv[1:], './conf'))
    if not os.path.isdir(configDir):
        raise ValueError('No such configuration directory exists: {}'.format(configDir))

    # Read in the configurations
    config = ApplicationConfiguration(configDir, ['door.ini', 'account-settings.ini'])

    # Setup logger
    logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', 
        filename=config.get('sms.door.command.log.file.directory') + '/' + config.get('sms.door.command.log.file.name'), level=logging.INFO)

    # Instantiate all the required modules
    az = Authorization(config.get('sms.door.command.allowed.phonenumbers'))
    db = Database(config.get('app.database.file'))
    pi = Pi()
    sms = Sms(db, config.get('sms.account.id'), config.get('sms.account.token'), config.get('sms.account.phone.number'))
    #sms.twilioClient.isMock = True # TODO
    #sms.twilioClient.mockMessages = __mock_messages() # TODO
    email = Email(config.get('door.email.address'), config.get('door.email.pword'), config.get_conf_file_contents('email-style.css'))
    challenge = Challenge(config, db, sms, email)
    dropbox = Dropbox(config.get('dropbox.gd.access.token'))
    command = GarageDoorCommand(config, db, challenge, pi, sms, email, dropbox)

    logging.info("Starting SMS Monitor Application")
    while True:
        try:
            # Turn on green light to indicate that work is being done
            pi.green_light_on()

            # fetch all the new messages that need processing
            smsMessages = sms.list()

            for message in smsMessages: 

                # regardless of any error or invalid command, save off the message for audit trail so it is never reprocessed
                db.insert_text_message(message) 

                # Make sure that this message is authorized
                if not az.is_authorized(message):
                    logging.warn('Unauthorized attempt detected: {}'.format(message))
                    db.update_text_message_status(message.get('sid'), 'unauthorized')
                    continue

                command.execute(message)

            # Clear any warn/error indicators
            pi.yellow_light_off()
            pi.red_light_off()
        except NetworkDownException as nde:
            logging.error('Unable to reach network, cannot process sms command messages', exc_info=True)
            pi.yellow_light_on()
        except:
            logging.error('Failure processing sms command messages', exc_info=True)
            pi.red_light_on(.5)
        finally:
            pi.green_light_off()
            time.sleep(5)

def get_config_directory(args, default):
    options, remainder = getopt.getopt(args, 'c:', ['configdirectory=',])

    for opt, arg in options:
        if opt in ('-c', '--configdirectory'):
            return arg
    return default

if __name__ == "__main__":
    main()
