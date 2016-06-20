import string
import random
import datetime
import time
import logging

class Challenge:

    def __init__(self, config, db, sms, email):
        self.config = config
        self.db = db
        self.sms = sms
        self.email = email
        self.codeSize = 6
        self.chars = string.ascii_uppercase + string.digits
        pass

    def is_challenge_required(self, commandName, command):
        if command is None or commandName is None:
            return False

        timeFrame = self.config.get('DEFAULT', 'sms.door.command.challenge.timeframe')
        challengeOnCommands = [x.strip() for x in self.config.get('DEFAULT', 'sms.door.command.challenge.commands', '').split(',')]
        awlaysChallengeCommands = [x.strip() for x in self.config.get('DEFAULT', 'sms.door.command.challenge.commands.always', '').split(',')]

        return (awlaysChallengeCommands is not None and commandName in awlaysChallengeCommands) or (challengeOnCommands is not None and commandName in challengeOnCommands and self.__is_now_within_range(timeFrame))

    # Generate a challenge code, store it for later reference, and send it to the user via sms or email
    def create(self, message):
        logging.debug("Attempting to create a challenge to text message: {}".format(message))
        if message is None or 'sid' not in message: raise ValueError('Message must contain a sid, unable to create challenge')
        if message is None or 'phoneFrom' not in message: raise ValueError('Message must contain a phoneFrom, unable to create challenge')
        
        code = self.__generate_challenge_code()
        logging.debug("generated code: {}".format(code))

        # Relate the challenge code to the message sid and persist it   
        self.db.insert_door_challenge(code, message.get('sid'))

        phoneNumber = message.get('phoneFrom')
        channel = self.config.get(phoneNumber, 'sms.door.command.challenge.via.channel', 'email')
        logging.debug('[create]Challenge channel: {}'.format(channel))

        # If this user wants to recieve challenges via email, then send an email
        if 'email' == channel:
            emailAddress = self.config.get(phoneNumber, 'user.email.address')
            userName = self.config.get(phoneNumber, 'user.name')
            emailMessage = self.__build_code_email_message(userName, code)
            self.email.send(emailAddress, 'Garage Challenge', emailMessage)

        # Or send it via sms text
        else:
            self.sms.send(phoneNumber, code)

    def fetch_message(self, code):
        logging.debug("Attempting to fetch a text message using challenge code: {}".format(code))
        if self.__looks_like_a_challenge_code(code):
            textMessage = self.db.find_door_challenge(code)
            if textMessage is not None:
                self.db.delete_door_challenge(code) # make sure the same code is never found more than once
            return textMessage
        return None

    def __generate_challenge_code(self):
        return ''.join(random.choice(self.chars) for _ in range(self.codeSize))

    def __looks_like_a_challenge_code(self, code):
        return code is not None and len(set(self.chars).intersection(code)) == self.codeSize

    # Where timeframe is a range of integers in 'hour:min - hour:min'.  ie: 22:00 - 7:00
    def __is_now_within_range(self, timeFrame):
        isWithinRange = True
        try:
            if timeFrame is not None:
                timeFrameList = [x.strip() for x in timeFrame.split('-')]
                if len(timeFrameList) is 2: # Must be in the form of hh:mm - hh:mm
                    beginHourMin = [int(x) for x in timeFrameList[0].split(':') if x.strip().isdigit()]
                    endHourMin = [int(x) for x in timeFrameList[1].split(':') if x.strip().isdigit()]
                    now = datetime.datetime.now()
                    beginRange = now.replace(hour=beginHourMin[0], minute=beginHourMin[1])
                    endRange = now.replace(hour=endHourMin[0], minute=endHourMin[1])
                    isWithinRange = now > beginRange or now < endRange
                    logging.debug("__is_now_within_range: now: {}, begin: {}, end: {}, isWithinRange: {}".format(now, beginRange, endRange, isWithinRange))
        except:
            logging.warn("Unable to determine timeframe, defaulting to challenge is within: True")

        return isWithinRange;

    def __build_code_email_message(self, userName, code):
        html = """\
        <html>
          <head>
            <style>
                body {
                    background-color: #EEEEEE;
                    color: #153643; 
                    font-family: Arial, 
                    sans-serif; 
                    font-size: 16px; 
                    line-height: 20px;
                }

                div {
                    background-color: #FFFFFF;
                    border-radius: 25px;
                    border: 2px solid #CCCCCC;
                    padding: 20px;
                    box-shadow: 10px 10px 5px #b7b7b7;
                }
            </style>
          </head>
          <body>
              <div>
              Hello <i>%s</i>,<p>
              Your challenge code is:<br><br>
              <p style="font-weight: bold; font-size: larger">%s</p>
              <br>
              You have 15 minutes from %s before it expires.<p>
              Sincerly,<br>
              <i>The Garage Door</i>
              </div>
          </body>
        </html>
        """
        # time could be a little off, but should be pretty close
        return html % (userName, code, datetime.datetime.now().strftime("%b %d (%A) %I:%M%p"))