import time
from datetime import timedelta
import logging
from .exception import CommandIgnoredException

class GarageDoorCommand:

    def __init__(self, config, db, challenge, pi, sms, email):
        self.config = config
        self.db = db
        self.challenge = challenge
        self.pi = pi
        self.sms = sms
        self.email = email

        # All the accepted commands.  These must appear as the body of a text message (case insensitive).
        self.commands = {
            'close': CloseCommand(self.pi, self.db),
            'diagnostics': DiagnosticsCommand(self.config, self.pi, self.db, self.email),
            'help': HelpCommand(self.sms),
            'lock': LockCommand(self.db, self.sms),
            'open': OpenCommand(self.pi, self.db),
            'photo': PhotoCommand(self.pi, self.email),
            'status': StatusCommand(self.pi, self.db, self.sms),
            'unlock': UnlockCommand(self.db, self.sms),
        }
        pass

    def execute(self, message):
        logging.info("Processing message command: {}".format(message))

        # Find the command that has been requested to run
        messageBody = self.__get_message_body(message)
        command = self.commands.get(messageBody, None)

        # Does this command require a challenge to be issued?
        if self.challenge.is_challenge_required(messageBody, command):
            self.challenge.create(message)

        else:
            # Unable to determine what the command action is, which means it could be a challenge response
            if command is None:
                challengedMessage = self.challenge.fetch_message(messageBody.upper())
                if challengedMessage is not None:
                    logging.info("Found a challenged message: {}".format(challengedMessage))
                    messageBody = self.__get_message_body(challengedMessage)
                    command = commands.get(messageBody, None)
                    message = challengedMessage # Switch to the challenge message so we know what command was originally attempted

            # run this message command
            self.__run_command(command, message)

    def __run_command(self, command, message):
        if command is not None:
            try:
                command.handle(message)
                self.db.update_text_message_status(message.get('sid'), 'processed')

                if (command.is_ack_success()):
                    self.__safe_sms_send(message.get('phoneFrom'), "Command: '{}' completed successfully.".format(self.__get_message_body(message)))

            except CommandIgnoredException as e:
                self.db.update_text_message_status(message.get('sid'), 'ignored', '{}'.format(e))
                self.__safe_sms_send(message.get('phoneFrom'), "Command: '{}' ignored because: {}".format(self.__get_message_body(message), e))

            except Exception as e:
                self.db.update_text_message_status(message.get('sid'), 'failed', "Unable to handle '{}' because: '{}'".format(message.get('body', None), e))
                self.__safe_sms_send(message.get('phoneFrom'), "Command: '{}' ignored because: {}".format(self.__get_message_body(message), e))
                raise e
        else:
            logging.info("No such command found, ignoring message: {}".format(message))
            self.db.update_text_message_status(message.get('sid'), 'ignored', 'No such command')

    # Safely pull out the message body
    def __get_message_body(self, message):
        if message is not None:
            return message.get('body', '').lower()
        return ''

    # Do not fail if unable to send ack response back to phoneNumber about state of actioned command
    def __safe_sms_send(self, phoneNumber, message):
        try:
            self.sms.send(phoneNumber, message)
        except Exception as e:
            logging.warn("Unable to reply to '{}' message '{}' because: '{}'".format(phoneNumber, message, e), exc_info=True)

class OpenCommand:

    def __init__(self, pi, db):
        self.pi = pi
        self.db = db
        pass

    def handle(self, message):
        logging.info("Handling command to open door")
        if not self.pi.is_door_closed():
            raise CommandIgnoredException('Door already open')
        elif self.db.find_door_lock() is not None:
            raise CommandIgnoredException('Door locked, unable to open')
        else:
            self.pi.open_door()
            #self.db.insert_door_state_history('open')

    def is_ack_success(self):
        return True

class CloseCommand:

    def __init__(self, pi, db):
        self.pi = pi
        self.db = db
        pass

    def handle(self, message):
        logging.info("Handling command to close door")
        if self.pi.is_door_closed():
            raise CommandIgnoredException("Door already closed")
        else:
            self.pi.close_door()
            #self.db.insert_door_state_history('close')

    def is_ack_success(self):
        return True

# Locks the garage door preventing it from being opened via sms commands
class LockCommand:

    def __init__(self, db, sms):
        self.db = db
        self.sms = sms
        pass

    def handle(self, message):
        logging.info("Handling command to lock")
        try:
            self.db.insert_door_lock()
        except ValueError as e:
            raise CommandIgnoredException(e)

    def is_ack_success(self):
        return True

# Unlocks the garage door allowing it to be opened from sms commands
class UnlockCommand:

    def __init__(self, db, sms):
        self.db = db
        self.sms = sms
        pass

    def handle(self, message):
        logging.info("Handling command to unlock")
        self.db.remove_door_lock()

    def is_ack_success(self):
        return True

class StatusCommand:

    def __init__(self, pi, db, sms):
        self.pi = pi
        self.db = db
        self.sms = sms
        pass

    def handle(self, message):
        logging.info("Handling command to status")
        state = "closed" if self.pi.is_door_closed() else "open"
        statusMessage = ("Door: {}".format(state))
        self.sms.send(message.get('phoneFrom'), statusMessage)

    def is_ack_success(self):
        return False

class DiagnosticsCommand:

    def __init__(self, config, pi, db, email):
        self.config = config
        self.pi = pi
        self.db = db
        self.email = email
        pass

    def handle(self, message):
        logging.info("Handling command to diagnostics")
        state = "closed" if self.pi.is_door_closed() else "open"
        uptime = self.find_uptime()
        diagnosticMessage = ("Door: {}\nUptime: {}\nNetwork light on: {}\nError light on: {}\n".format(state, uptime, self.pi.is_yellow_light_on(), self.pi.is_red_light_on()))
 
        # Send the diagnostic report to all the configured user addresses
        self.email.send(self.config.get(message.get('phoneFrom'), 'user.email.address'), 'Diagnostics', diagnosticMessage)

    def is_ack_success(self):
        return False

    def find_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds = uptime_seconds))        

class PhotoCommand:

    def __init__(self, pi, email):
        self.pi = pi
        self.email = email
        pass

    def handle(self, message):
        logging.info("Handling command to photo")
        # TODO

    def is_ack_success(self):
        return False

class HelpCommand:

    def __init__(self, sms):
        self.sms = sms
        pass

    def handle(self, message):
        logging.info("Handling command to help")
        helpMessage = 'Commands:\n  close\n  help\n  lock\n  open\n  photo\n  status\n  unlock'
        self.sms.send(message.get('phoneFrom'), helpMessage)

    def is_ack_success(self):
        return False


