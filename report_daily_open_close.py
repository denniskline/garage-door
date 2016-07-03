#!/usr/bin/python3

import os
import datetime
import time
import logging
import getopt
import sys
from gdmod import ApplicationConfiguration
from gdmod import Database
from gdmod import Email

def main():
    # Check command options to see if a custom configuration directory was supplied
    configDir = os.path.abspath(get_config_directory(sys.argv[1:], './conf'))
    if not os.path.isdir(configDir):
        raise ValueError('No such configuration directory exists: {}'.format(configDir))

    # Read in the configurations
    config = ApplicationConfiguration(configDir, ['door.ini', 'account-settings.ini'])
    cssStyle = config.get_conf_file_contents('email-style.css')

    # Setup logger
    logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', 
        filename=config.get('door.reporting.log.file.directory') + '/' + config.get('door.reporting.log.file.name'), level=logging.INFO)

    # Instantiate all the required modules
    db = Database(config.get('app.database.file'))
    email = Email(config.get('door.email.address'), config.get('door.email.pword'), config.get_conf_file_contents('email-style.css'))

    logging("Starting Reporting")

    # Run the report with 5 retries if there is a failure
    for x in range(0, 5):

        try:
            logging.info('Executing reports')

            # Find all door histories in the past 24 hours
            now = datetime.datetime.now()
            yesterday = now - datetime.timedelta(days=1)
            histories = db.find_door_state_histories(yesterday)

            # Create the report
            reportMessage = create_histories_report(histories, cssStyle, now, yesterday)

            # Send the report to all the configured user addresses
            email.send(find_user_email_addresses(config), 
                'Garage Door Report: {} - {}'.format(yesterday.strftime("%b %d (%A) %I:%M%p"), datetime.datetime.now().strftime("%b %d (%A) %I:%M%p")), 
                reportMessage)

            return
        except:
            logging.error('Failed on attempt {} exeucting daily open/close report'.format(x), exc_info=True)
            time.sleep(300) # Wait a nice long time before retrying again: it's a daily report, waiting 5 mins is no biggie
            pass

def create_histories_report(histories, cssStyle, now, yesterday):
    body = '<H3>Garage Door Report: {} - {}</H3>\n'.format(yesterday.strftime("%b %d (%A) %I:%M%p"), datetime.datetime.now().strftime("%b %d (%A) %I:%M%p"))
    body += '<table>\n<tr><th>Time</th><th>State</th></tr>\n'
    for history in histories:
        body += '<tr><td>{}</td><td>{}</td></tr>\n'.format(history.get('changedAt').strftime("%b %d %I:%M%p"), history.get('state'))
    body += '</table>\n'
    return body

def find_user_email_addresses(config):
    phoneNumbers = [x.strip() for x in config.get('sms.door.command.allowed.phonenumbers').split(',')]
    emailAddresses = []
    for phoneNumber in phoneNumbers:
        emailAddresses.append(config.get(phoneNumber, 'user.email.address'))
    return emailAddresses

def get_config_directory(args, default):
    options, remainder = getopt.getopt(args, 'c:', ['configdirectory=',])

    for opt, arg in options:
        if opt in ('-c', '--configdirectory'):
            return arg
    return default

if __name__ == "__main__":
    main()
