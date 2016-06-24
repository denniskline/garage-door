import datetime
import logging
from .exception import NetworkDownException
from twilio.rest import TwilioRestClient

class Sms:

    def __init__(self, db, account_sid, auth_token, account_phone_number):
        self.db = db
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.account_phone_number = account_phone_number
        self.twilioRestClient = TwilioRestClient(self.account_sid, self.auth_token)
        pass

    def send(self, toPhoneNumber, message):
        logging.info("Attempting to text {} with message: {}".format(toPhoneNumber, message))

        # Try to send message.  If sending fails, retry 5 times before giving up
        for x in range(0, 5):
            if x is not 0:
                time.sleep(5) # Wait 5 seconds if this is a retry

            try:
                response = self.twilioRestClient.sms.messages.create(body="{}".format(message),to="{}".format(toPhoneNumber),from_="{}".format(self.account_phone_number))
                #response = "yay!"
                logging.info("Response from sending message:{} = {}".format(message, response))
                return
            except Exception as e:
                logging.warn("Failed on attempt {} of sending message: {}, {}, {} Because: {}".format(x, message, toPhoneNumber, e))
                failure = e

        # Assume network down.  Could be other things, but most likely this
        raise NetworkDownException('Unable to call twilio to send to {} message {}'.format(toPhoneNumber, message)) from failure

    def list(self, dateSince=None):
        dateSince = dateSince if dateSince else datetime.datetime.now() - datetime.timedelta(minutes=15)
        logging.info("Attempting to list all unprocessed messages since: {}".format(dateSince))

        twilioMessages = self.__list_all(dateSince)
        processedMessages = self.db.find_messages(datetime.datetime.now() - datetime.timedelta(days=3))

        # Find all the messages that have not been processed already
        messages = self.__messages_not_in_messages(twilioMessages, processedMessages)

        # Sort all the unprocessed messages so that the oldest is executed first
        messages.sort(key=lambda k: (k['sentAt'] is None, k['sentAt'] == datetime.datetime.now(), k['sentAt']))
        return messages

    def __list_all(self, dateSince):
        messages = []
        try:
            logging.info('calling twilio')
            twilioMessages = self.twilioRestClient.messages.list(date_sent=datetime.datetime.utcnow())
            for message in twilioMessages:
                messages.append({
                    "sid": message.sid,
                    "phoneFrom": message.from_[1:], # remove the +
                    "phoneTo": message.to[1:],
                    "direction": message.direction,
                    "createdAt": message.date_created,
                    "sentAt": message.date_sent,
                    "status": message.status,
                    "body": message.body,
                })
        except Exception as e:
            raise NetworkDownException('Unable to call twilio to get list of messages from: {}'.format(dateSince)) from e

        #for message in messages:
        #    print("Translated message: {}".format(message))

        # only messages that have a status of 'received' are allowed to be returned.  received == On inbound messages only. The inbound message was received by one of your Twilio numbers.
        return (m for m in messages if m.get("status", None) == 'received')

    # Search for items in list1 that do not exist in list2
    def __messages_not_in_messages(self, list1, list2):
        notIns = []
        for l in list1: 
            if not any(d['sid'] == l.get('sid') for d in list2):
                notIns.append(l)
        return notIns

    def diagnostics(self):
        diag = {}
        return diag
