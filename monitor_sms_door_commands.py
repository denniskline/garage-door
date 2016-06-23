#!/usr/bin/python3

import os
import datetime
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
    sms = Sms(db, config.get('sms.account.id'), config.get('sms.account.token'), config.get('sms.account.phone.number'))
    sms.twilioClient.isMock = True # TODO
    sms.twilioClient.mockMessages = __mock_messages() # TODO
    pi = Pi()
    email = Email(config.get('door.email.address'), config.get('door.email.pword'), config.get_conf_file_contents('email-style.css'))
    challenge = Challenge(config, db, sms, email)
    command = GarageDoorCommand(config, db, challenge, pi, sms, email)

    try:
        # Visual indicator that work is being performed
        pi.blink_green_light(.5)

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
        pi.off_yellow_light()
        pi.off_red_light()
    except NetworkDownException as nde:
        logging.error('Unable to reach network, cannot process sms command messages', exc_info=True)
        pi.blink_yellow_light(.5)
    except:
        logging.error('Failure processing sms command messages', exc_info=True)
        pi.blink_red_light(.5)
    finally:
        # Toggle off the visual indicator that work is being performed
        pi.off_green_light()

def get_config_directory(args, default):
    options, remainder = getopt.getopt(args, 'c:', ['configdirectory=',])

    for opt, arg in options:
        if opt in ('-c', '--configdirectory'):
            return arg
    return default

class MockMessage:
    def __init__(self, dictionary):
        for k,v in dictionary.items():
            setattr(self, k, v)
        pass

# TODO: Delete all this and move it into test case:
def __mock_messages():
    messages = []
    messages.append(MockMessage({'sid': '1-close', 'body': 'Close', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=15), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=15)}))
    messages.append(MockMessage({'sid': '2-lock', 'body': 'Lock', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=12), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=12)}))
    messages.append(MockMessage({'sid': '22-lock', 'body': 'Lock', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=12), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=12)}))
    messages.append(MockMessage({'sid': '3-open', 'body': 'Open', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=11), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=11)}))
    messages.append(MockMessage({'sid': '4-unlock', 'body': 'Unlock', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=10), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=10)}))
    messages.append(MockMessage({'sid': '5-open', 'body': 'Open', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=9), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=9)}))
    messages.append(MockMessage({'sid': '6-ignore-me', 'body': 'This is just an arbitrary text', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=9), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=9)}))
    #for message in messages:
    #    logging.info("Mock Message: {}".format(vars(message)))
    return messages

if __name__ == "__main__":
    main()