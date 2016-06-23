import unittest

import configparser
import datetime

from gdmod.command import *
from gdmod import Challenge
from gdmod.config import ApplicationConfiguration
from gdmod import Database
from gdmod import Pi
from gdmod import Sms
from gdmod.exception import CommandIgnoredException

from . import MockEmail

# garage-door> python3 -m unittest test.test_command
class CommandTest(unittest.TestCase):

    # ************************************************************************
    # Lifecycle

    def setUp(self):
        self.basicConfig = configparser.ConfigParser()
        self.basicConfig = configparser.ConfigParser()
        self.basicConfig['DEFAULT'] = {
                            'sms.door.command.challenge.timeframe': '', 
                            'sms.door.command.challenge.commands': '', 
                            'sms.door.command.challenge.commands.always': 'Lock', 
                            'sms.door.command.challenge.via.channel': 'email', 
                            }
        self.basicConfig['1112223333'] = {
                            'user.email.address': 'email@address.com', 
                            'user.name': 'Banjo, King of the Sea Monkies', 
                            }
        self.db = Database('./test/test-gd.db')
        self.mockEmail = MockEmail('gd@foo.com', 'gdpwd')
        self.sms = Sms(self.db, 'foo', 'foo', 'foo')
        self.sms.twilioClient.isMock = True
        self.config = ApplicationConfiguration(None, None)
        self.config.configurations.append(self.basicConfig)
        self.challenge = Challenge(self.config, self.db, self.sms, self.mockEmail)
        self.pi = Pi()

    def tearDown(self):
        self.db.destroy_database()

    # ************************************************************************
    # Test Cases

    def test_open_command_when_door_is_closed(self):
        self.pi.close_door()
        self.assertTrue(self.pi.is_door_closed())

        command = OpenCommand(self.pi, self.db)
        command.handle({'sid': '123', 'body': 'open'})
        self.assertFalse(self.pi.is_door_closed())

    def test_open_command_when_door_is_open(self):
        self.pi.open_door()
        self.assertFalse(self.pi.is_door_closed())

        command = OpenCommand(self.pi, self.db)
        with self.assertRaises(CommandIgnoredException):
            command.handle({'sid': '123', 'body': 'open'})

    def test_open_command_when_door_is_locked(self):
        self.pi.close_door()
        self.assertTrue(self.pi.is_door_closed())

        self.db.insert_door_lock()

        command = OpenCommand(self.pi, self.db)
        with self.assertRaises(CommandIgnoredException):
            command.handle({'sid': '123', 'body': 'open'})

    def test_diagnostics(self):
        command = DiagnosticsCommand(self.config, self.pi, self.db, self.mockEmail, self.sms)
        command.handle({'sid': '123', 'body': 'diagnostics', 'phoneFrom': '1112223333'})

        self.assertEqual(1, len(self.mockEmail.sent_messages))
