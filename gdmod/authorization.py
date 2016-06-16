class Authorization:

    def __init__(self, phoneNumbers):
        self.phoneNumbers = [x.strip() for x in phoneNumbers.split(',')]
        pass

    def authorize(self, message):
        if not self.is_authorized(message):
            raise ValueError("Unauthorized message: sid='{}', phone='{}', body='{}'".format(message.get('sid', ''), message.get('phoneFrom', ''), message.get('body', '')))

    def is_authorized(self, message):
        if message is None or 'phoneFrom' not in message: raise ValueError('Message must contain a phoneFrom, unable to authorize: {}'.format(message.get('sid')))

        phoneNumber = message.get('phoneFrom')
        return phoneNumber in self.phoneNumbers

