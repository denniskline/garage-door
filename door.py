#!/usr/bin/python3

import configparser
import datetime
from operator import itemgetter
from gdmod import Database
from gdmod import Sms
from gdmod import Pi
from gdmod import Email
from gdmod import Challenge
from gdmod import OpenCommand
from gdmod import CloseCommand
from gdmod import LockCommand
from gdmod import StatusCommand
from gdmod import PhotoCommand
from gdmod import HelpCommand

# Search for items in list1 that do not exist in list2
def messages_not_in_messages(list1, list2):
    notIns = []
    for l in list1: 
        if not any(d['sid'] == l.get('sid') for d in list2):
            notIns.append(l)
    return notIns

# Ask the database for a list of all the messages that have already been processed 
db = Database('data/gd.db')
processedMessages = db.find_messages(datetime.datetime.now() - datetime.timedelta(days=3))
for l in processedMessages: print("processedMessage: {}".format(l))

# Pull the message list for any possible new commands
sms = Sms('accountsid', 'authtoken', 16143334444)
messages = sms.list()

# Find all the messages that have not been processed already
newMessages = messages_not_in_messages(messages, processedMessages)

# Sort all the unprocessed messages so that the oldest is executed first
newMessages.sort(key=lambda k: (k['sentAt'] is None, k['sentAt'] == datetime.datetime.now(), k['sentAt']))

pi = Pi()
email = Email('garage@gmail.com', 'garage-pword')
challenge = Challenge(db)

commands = {
    'close': CloseCommand(pi, db),
    'help': HelpCommand(sms),
    'lock': LockCommand(db),
    'open': OpenCommand(pi, db),
    'photo': PhotoCommand(pi, email),
    'status': StatusCommand(pi, db, sms)
}

def run_command(command, textMessage):
    db.insert_text_message(textMessage) # regardless of any error or invalid command, we don't want to reprocess any messages
    if command is not None:
        try:
            command.handle(textMessage)
        except:
            print("Unable to handle {}".format(textMessage))
    else:
        print("No such command found, ignoring message: {}".format(textMessage))


# Ignore contradicting commands. ie: don't process an 'open' command if there is a subsequent 'close' command
for nm in newMessages: 
    print("new message: {}".format(nm))
    command = commands.get(nm.get('body', '').lower(), None)
    if command is None:
        challengedMessage = challenge.fetch_message(commands.get(nm.get('body', '').upper(), None))
        if challengedMessage is not None:
            print("Found a challenged message: {}".format(challengedMessage))
            command = commands.get(challengedMessage.get('body', '').lower(), None)
            db.insert_text_message(nm) # Insert the text message containing the challenge code so it is not run again
            nm = challengedMessage # Switch to the challenge message so we know what command was originally attempted

    run_command(command, nm)

#for h in db.find_door_state_histories():
#    print(h)

#challengeCode = challenge.generate_code()
#print("challengeCode: {}".format(challengeCode))
#print("123456 looks like a challenge code? {}".format(challenge.looks_like_a_code("123456")))
#print("123AB6 looks like a challenge code? {}".format(challenge.looks_like_a_code("123AB6")))
#print("123456C looks like a challenge code? {}".format(challenge.looks_like_a_code("123456C")))
#print("1234#6 looks like a challenge code? {}".format(challenge.looks_like_a_code("1234#6")))
#print("123__1 looks like a challenge code? {}".format(challenge.looks_like_a_code("123__1")))

