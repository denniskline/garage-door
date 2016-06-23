import unittest
from gdmod.challenge import Challenge
from gdmod.config import ApplicationConfiguration
from gdmod import Database
from gdmod import Sms
import configparser
import datetime
from . import MockEmail
import time

# garage-door> python3 -m unittest test.test_challenge
class ChallengeTest(unittest.TestCase):

    # ************************************************************************
    # Lifecycle

    def setUp(self):
        self.basicConfig = configparser.ConfigParser()
        self.basicConfig['DEFAULT'] = {
                            'sms.door.command.challenge.timeframe': '22:00 - 07:00', 
                            'sms.door.command.challenge.commands': 'Open, Close', 
                            'sms.door.command.challenge.commands.always': 'Lock', 
                            'sms.door.command.challenge.via.channel': 'email', 
                            }
        self.basicConfig['1112223333'] = {
                            'user.email.address': 'email@address.com', 
                            'user.name': 'Banjo, King of the Sea Monkies', 
                            'sms.door.command.challenge.commands.always': 'Lock', 
                            }
        self.db = Database('./test/test-gd.db')
        self.mockEmail = MockEmail('gd@foo.com', 'gdpwd')
        self.mockEmail = MockEmail('gd@foo.com', 'gdpwd')
        self.sms = Sms(self.db, 'foo', 'foo', 'foo')
        self.sms.twilioClient.isMock = True

    def tearDown(self):
        self.db.destroy_database()

    # ************************************************************************
    # Test Cases

    def test_always_challenged_command_when_configured_to_do_so(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.commands.always'] = 'Lock'
        self.basicConfig['DEFAULT']['sms.door.command.challenge.timeframe'] = ''
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        self.assertTrue(challenge.is_challenge_required('Lock'))

    def test_when_not_configured_to_always_challenge_a_command_do_not_challenge(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.commands.always'] = ''
        self.basicConfig['DEFAULT']['sms.door.command.challenge.timeframe'] = ''
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        self.assertFalse(challenge.is_challenge_required('Lock'))

    def test_challenge_normal_command_when_no_timeframe_is_given(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.commands'] = 'Open'
        self.basicConfig['DEFAULT']['sms.door.command.challenge.timeframe'] = ''
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        self.assertTrue(challenge.is_challenge_required('Open'))

    def test_only_challenge_normal_command_within_timeframe(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.commands'] = 'Open'
        self.basicConfig['DEFAULT']['sms.door.command.challenge.timeframe'] = '{} - {}'.format((datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%H:%M"), (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M"))
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        self.assertTrue(challenge.is_challenge_required('Open'))

    def test_do_not_challenge_normal_command_outside_timeframe(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.commands'] = 'Open'
        self.basicConfig['DEFAULT']['sms.door.command.challenge.timeframe'] = '{} - {}'.format((datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%H:%M"), (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%H:%M"))
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        self.assertFalse(challenge.is_challenge_required('Open'))

    def test_create_challenge_code_by_email(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.via.channel'] = 'email'
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        code = challenge.create({'sid': '1234', 'phoneFrom': '1112223333'})

        self.assertTrue(6, len(code))
        self.assertEqual(1, len(self.mockEmail.sent_messages))

    def test_create_challenge_code_by_sms(self):
        self.basicConfig['DEFAULT']['sms.door.command.challenge.via.channel'] = 'sms'
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        code = challenge.create({'sid': '1234', 'phoneFrom': '1112223333'})

        self.assertTrue(6, len(code))
        self.assertEqual(0, len(self.mockEmail.sent_messages))

    def test_create_challenge_code_and_find_original_message_based_on_the_created_code(self):
        config = ApplicationConfiguration(None, None)
        config.configurations.append(self.basicConfig)
        challenge = Challenge(config, self.db, self.sms, self.mockEmail)

        originalMessage = {'sid': '1234', 'phoneFrom': '1112223333', 'body': 'Open'}
        self.db.insert_text_message(originalMessage) 
        code = challenge.create(originalMessage)
        self.assertIsNone(challenge.fetch_message(code.lower())) # Case is important
        foundMessage = challenge.fetch_message(code)

        self.assertIsNotNone(foundMessage)
        self.assertEqual(originalMessage['sid'], foundMessage['sid'])
        self.assertEqual(originalMessage['body'], foundMessage['body'])
        self.assertEqual(originalMessage['phoneFrom'], foundMessage['phoneFrom'])
        self.assertIsNone(challenge.fetch_message(code)) # Codes cannot be reused, make sure that no message is found

if __name__ == '__main__':
    unittest.main()