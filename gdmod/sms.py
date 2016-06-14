import datetime
#from twilio.rest import TwilioRestClient

class Sms:

    def __init__(self, account_sid, auth_token, account_phone_number):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.account_phone_number = account_phone_number
        #self.twilioRestClient = TwilioRestClient(self.account_sid, self.auth_token)
        pass

    def send(self, toPhoneNumber, message):
        print("Attempting to text {} with message: {}".format(toPhoneNumber, message))
        try:
            #response = self.twilioRestClient.sms.messages.create(body="{}".format(message),to="{}".format(toPhoneNumber),from_="{}".format(self.account_phone_number))
            response = "yay!"
            print("Response: {}".format(response))
        except:
            print("Unable to send message {} to {}".format(message, toPhoneNumber))
            pass


    def list(self, dateSince=None):
        dateSince = dateSince if dateSince else datetime.datetime.now() - datetime.timedelta(minutes=15)
        print("Attempting to list all messages since: {}".format(dateSince))

        messages = []
        #try:
        #messages = TwilioClient.messages.list(date_sent=datetime.datetime.utcnow())
        messages.append({'sid': '30_mins', 'body': 'Open', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=30)})
        messages.append({'sid': '5_hours', 'body': 'Close', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(hours=5)})
        messages.append({'sid': '123', 'body': 'Close', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=15)})
        messages.append({'sid': '10_mins', 'body': 'Status', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=10)})
        messages.append({'sid': '13_mins', 'body': 'Whoopy whoopy', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=13)})
        messages.append({'sid': 'mins_2', 'body': 'Close', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=2)})
        messages.append({'sid': 'None_mins', 'body': 'Close', 'status': 'received', 'sentAt':  None})
        messages.append({'sid': '12_mins', 'body': 'Close', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=12)})
        messages.append({'sid': 'mins_7', 'body': 'Lock', 'status': 'received', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=7)})
        messages.append({'sid': 'mins_1_recieving', 'body': 'Open', 'status': 'receiving', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=1)})
        messages.append({'sid': 'mins_1_failed', 'body': 'Open', 'status': 'failed', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=1)})
        messages.append({'sid': 'no status', 'body': 'Close', 'sentAt':  datetime.datetime.now() - datetime.timedelta(minutes=1)})
        #except:
        #    print("Unable to fetch message list")
        #    pass

        # only messages that have a status of 'received' are allowed to be returned.  received == On inbound messages only. The inbound message was received by one of your Twilio numbers.
        return (m for m in messages if m.get("status", None) == 'received')
