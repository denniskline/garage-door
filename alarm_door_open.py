#!/usr/bin/python3

import os
import time
import logging
import getopt
import sys
from gdmod import ApplicationConfiguration
from gdmod import Database
from gdmod import Pi
from gdmod import Sms

# ************************************************************************
# Schedule to run whenever you would like to be alerted and for whatever interval :
#
# Run every 15 minutes between the hours of 10pm and 5am
# sudo crontab -e           (sudo is needed to access GPIO)
# */15 0-5,22,23 * * * <BASE_DIR>/gd/garage-door/control.sh start alarm_door_open
# ************************************************************************
def main():
    # Check command options to see if a custom configuration directory was supplied
    configDir = os.path.abspath(get_config_directory(sys.argv[1:], './conf'))
    if not os.path.isdir(configDir):
        raise ValueError('No such configuration directory exists: {}'.format(configDir))

    # Read in the configurations
    config = ApplicationConfiguration(configDir, ['door.ini', 'account-settings.ini'])

    # Setup logger
    logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s',
                        filename=config.get('door.alarm.open.log.file.directory') + '/' + config.get('door.alarm.open.log.file.name'), level=logging.INFO)

    # Instantiate all the required modules
    db = Database(config.get('app.database.file'))
    pi = Pi()
    sms = Sms(db, config.get('sms.account.id'), config.get('sms.account.token'), config.get('sms.account.phone.number'))

    logging.info("Starting Open Door Alarm Check")

    # Run the validation check with 5 retries if there is a failure
    for x in range(0, 5):

        try:
            logging.info('Executing check')
            if not pi.is_door_closed():
                logging.warn('Door is not closed.  Initiating Alarm')
                alarm(sms, find_user_sms_numbers(config))
            return
        except:
            logging.error('Failed on attempt {} exeucting door open alarm'.format(x), exc_info=True)
            time.sleep(300) # Wait a nice long time before retrying again
            pass

    logging.info("Completed Reporting")

def alarm(sms, phoneNumbers):
    message = "It is late and the garage door is still open.  Please close."
    for phoneNumber in phoneNumbers:
        sms.send(phoneNumber, message)
    return message

def find_user_sms_numbers(config):
    return [x.strip() for x in config.get('sms.door.command.allowed.phonenumbers').split(',')]

def get_config_directory(args, default):
    options, remainder = getopt.getopt(args, 'c:', ['configdirectory=',])

    for opt, arg in options:
        if opt in ('-c', '--configdirectory'):
            return arg
    return default

if __name__ == "__main__":
    main()
