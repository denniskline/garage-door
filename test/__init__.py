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

class MockPi:

    def __init__(self):
        self.redLightOn = False
        self.yellowLightOn = False
        self.greenLightOn = False
        self.isDoorClosed = True 
        pass

    def open_door(self):
        self.isDoorClosed = False

    def close_door(self):
        self.isDoorClosed = True

    def is_door_closed(self):
        return self.isDoorClosed

    def green_light_on(self):
        self.greenLightOn = True

    def yellow_light_on(self):
        self.yellowLightOn = True

    def red_light_on(self):
        self.redLightOn = True

    def green_light_off(self):
        self.greenLightOn = False

    def yellow_light_off(self):
        self.yellowLightOn = False

    def red_light_off(self):
        self.redLightOn = False

    def is_green_light_on(self):
        return self.greenLightOn

    def is_yellow_light_on(self):
        return self.yellowLightOn

    def is_red_light_on(self):
        return self.redLightOn

    def take_picture(self, photoDir):
        fileName = ('{}_gd_photo.jpg'.format(datetime.datetime.now().strftime("%H%M%S")))
        file = ('{}/{}'.format(photoDir, fileName))

    def diagnostics(self):
        diag = {}
        diag['Door'] = "closed" if self.is_door_closed() else "open"
        return diag

