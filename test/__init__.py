import logging
logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)

# ************************************************************************
# Mocks

class MockEmail:
    def __init__(self, gmailUsername, gmailPassword):
        self.sent_messages = []

    def send(self, recipients, subject, messageContent):
        self.sent_messages.append(messageContent)
        logging.debug('Sending email message content: {}'.format(messageContent))

class MockMessage:
    def __init__(self, dictionary):
        for k,v in dictionary.items():
            setattr(self, k, v)
        pass
