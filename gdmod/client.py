import datetime
import logging
from twilio.rest import TwilioRestClient

# Wrapper around the wilio clinet that enables easy mocking and testing on platforms 
# that does not have the twilio rest client installed
class TwilioClient:

    #try:
    #from twilio.rest import TwilioRestClient
    #except:
    #    pass

    def __init__(self, account_sid, auth_token):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.isMock = False
        self.mockMessages = []
        #try:
        self.twilioRestClient = TwilioRestClient(self.account_sid, self.auth_token)
        #except:
        #    logging.error('Twilio rest client is not installed, unable to make any real sms calls')
        #    self.twilioRestClient = None
        pass

    def send(self, phoneTo, phoneFrom, message):
        if self.isMock:
            response = ''
        elif self.twilioRestClient is not None:       
            response = self.twilioRestClient.sms.messages.create(body="{}".format(message),to="{}".format(phoneTo),from_="{}".format(phoneFrom))
        else:
            raise ValueError('TwilioRestClient not installed, unable to make any real sms calls')

        return response

    def list(self, dateSent):
        if self.isMock:
            twilioMessages = self.mockMessages
        elif self.twilioRestClient is not None:
            twilioMessages = self.twilioRestClient.messages.list(date_sent=dateSent)
        else:
            raise ValueError('TwilioRestClient not installed, unable to make sms calls')
        
        return twilioMessages

#     def __mock_messages(self):
#        messages = []
#        messages.append(MockMessage({'sid': '1-close', 'body': 'Close', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=15), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=15)}))
#        messages.append(MockMessage({'sid': '2-lock', 'body': 'Lock', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=12), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=12)}))
#        messages.append(MockMessage({'sid': '22-lock', 'body': 'Lock', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=12), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=12)}))
#        messages.append(MockMessage({'sid': '3-open', 'body': 'Open', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=11), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=11)}))
#        messages.append(MockMessage({'sid': '4-unlock', 'body': 'Unlock', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=10), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=10)}))
#        messages.append(MockMessage({'sid': '5-open', 'body': 'Open', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=9), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=9)}))
#        messages.append(MockMessage({'sid': '6-ignore-me', 'body': 'This is just an arbitrary text', 'status': 'received', 'from_': '+15551113333', 'to': '+15552229999', 'direction': 'outbound-api', 'date_created': datetime.datetime.now() - datetime.timedelta(minutes=9), 'date_sent': datetime.datetime.now() - datetime.timedelta(minutes=9)}))
#
#        for message in messages:
#            logging.info("Mock Message: {}".format(vars(message)))
#
#        return messages

