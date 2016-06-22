#try:
#    from gdmod import config
#except ImportError as e:
#    print("Unable to load gdmoc")


#try:
#    import unittest.mock as mock
#except ImportError:
#    import mock


# ************************************************************************
# Mocks

# Mock when we reach out to truly 'external' service endpoints
class MockSms:
    def __init__(self, db, account_sid, auth_token, account_phone_number):
        self.sent_messages = []
 
    def send(self, toPhoneNumber, message):
        self.sent_messages.append(message)

    def list(self, dateSince=None):
        raise ValueError("Challenge should not be listing sms messages")   

class MockEmail:
    def __init__(self, gmailUsername, gmailPassword):
        self.sent_messages = []

    def send(self, recipients, subject, messageContent):
        self.sent_messages.append(messageContent)
        #print(messageContent)

