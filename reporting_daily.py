#!/usr/bin/python3

import os
import datetime
import time
import logging
import getopt
import sys
from dateutil import tz
from gdmod import ApplicationConfiguration
from gdmod import Database
from gdmod import Email

# ************************************************************************
# Schedule the report to run every night at 10:30pm :
#
# crontab -e
# 30 22 * * * <BASE_DIR>/gd/garage-door/control.sh start reporting_daily
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
        filename=config.get('door.reporting.log.file.directory') + '/' + config.get('door.reporting.log.file.name'), level=logging.INFO)

    # Instantiate all the required modules
    db = Database(config.get('app.database.file'))
    email = Email(config.get('door.email.address'), config.get('door.email.pword'), config.get_conf_file_contents('email-style.css'))

    logging.info("Starting Reporting")

    # Run the report with 5 retries if there is a failure
    for x in range(0, 5):

        try:
            logging.info('Executing reports')

            # Find all door histories in the past 24 hours
            now = datetime.datetime.now()
            yesterday = now - datetime.timedelta(days=1)
            histories = db.find_door_state_histories(yesterday)
            smsMessages = db.find_messages(yesterday)
            doorActions = combine_histories_and_messages(histories, smsMessages)

            # Create the report
            reportMessage = create_header(yesterday, now)
            reportMessage += "\n<p>\n"
            reportMessage += create_summary(histories, smsMessages)
            reportMessage += "\n</p><p>\n"
            reportMessage += create_action_detail(doorActions)
            reportMessage += "\n</p>\n"
            logging.info(reportMessage)

            # Send the report to all the configured user addresses
            email.send(find_user_email_addresses(config), 
                'Garage Door Report: {} - {}'.format(yesterday.strftime("%b %d (%a) %I:%M%p"), datetime.datetime.now().strftime("%b %d (%a) %I:%M%p")), 
                reportMessage)

            return
        except:
            logging.error('Failed on attempt {} exeucting daily open/close report'.format(x), exc_info=True)
            time.sleep(300) # Wait a nice long time before retrying again: it's a daily report, waiting 5 mins is no biggie
            pass

    logging.info("Completed Reporting")

def create_summary(histories, smsMessages):
    opens = (1 for k in histories if k.get('state').lower() == 'open')
    closes = (1 for k in histories if k.get('state').lower() == 'closed')
    failures = (1 for k in smsMessages if k.get('status').lower() == 'failed')
    unauthorizeds = (1 for k in smsMessages if k.get('status').lower() == 'unauthorized')
    ignores = (1 for k in smsMessages if k.get('status').lower() == 'ignored')
    summary = "<table>\n<tr><th>Open</th><th>Close</th><th>Failure</th><th>Unauthorized</th><th>Ignore</th></tr>\n"
    summary += ("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n</table>\n".format(sum(opens), sum(closes), sum(failures),  sum(unauthorizeds),  sum(ignores)))
    return summary

def create_action_detail(doorActions):
    body = '<table>\n<tr><th>Time</th><th>Action</th></tr>\n'
    for action in doorActions:
        body += '<tr><td>{}</td><td><span {}>{}</span></td></tr>\n'.format(action.get('timestamp').strftime("%b %d %I:%M%p"), action.get('style'), action.get('action'))
    body += '</table>\n'
    return body

def create_header(startTime, endTime):
    return '<H4>{} - {}</H4>\n'.format(startTime.strftime("%b %d (%a) %I:%M%p"), endTime.strftime("%b %d (%a) %I:%M%p"))

def combine_histories_and_messages(histories, smsMessages):
    cmdSuccessStyle = 'class="commandSuccess"'
    cmdErrorStyle = 'class="commandError"'
    basicStyle = ''

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    combinedList = []
    for history in histories:
        combinedList.append({"action": history.get('state'), "timestamp": history.get('changedAt'), "style": basicStyle})
    for smsMessage in smsMessages:
        style = cmdSuccessStyle if smsMessage.get('status').lower() == 'processed' else cmdErrorStyle
        createdAt = smsMessage.get('createdAt').replace(tzinfo=from_zone)
        combinedList.append({"action": smsMessage.get('body').lower(), "timestamp": createdAt.astimezone(to_zone), "style": style})

    combinedList.sort(key=lambda c: c.get("timestamp"))
    return combinedList

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
