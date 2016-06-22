import unittest
from gdmod.config import ApplicationConfiguration

# garage-door> python3 -m unittest test.test_config
class ApplicationConfigurationTest(unittest.TestCase):

    # ************************************************************************
    # Test Cases

    def test_find_property_value(self):
        config = ApplicationConfiguration('./conf', ['door.ini', 'test.ini'])
        self.assertEqual('sms_door.log', config.get('sms.door.command.log.file.name'))

    def test_config_returns_default_when_no_matching_property_found(self):
        config = ApplicationConfiguration('./conf', ['door.ini', 'test.ini'])
        self.assertEqual('not-found-default-value', config.get('DEFAULT', 'some.no.name.property', 'not-found-default-value'))

    def test_config_NONE_when_no_property_found_and_no_default_supplied(self):
        config = ApplicationConfiguration('./conf', ['door.ini', 'test.ini'])
        self.assertIsNone(config.get('some.no.name.property'))

    def test_find_default_property_value_in_second_config_ini(self):
        config = ApplicationConfiguration('./conf', ['door.ini', 'test.ini'])
        self.assertEqual('15551112222, 15551113333', config.get('sms.door.command.allowed.phonenumbers'))

    def test_find_user_specific_property_value_in_second_config_ini(self):
        config = ApplicationConfiguration('./conf', ['door.ini', 'test.ini'])
        self.assertEqual('me.user@gmail.com', config.get('15551112222', 'user.email.address'))

    def test_read_in_conf_css_file(self):
        config = ApplicationConfiguration('./conf', ['door.ini', 'test.ini'])
        css = config.get_conf_file_contents('email-style.css')
        #print('css: {}'.format(css))
        self.assertIsNotNone(css)

if __name__ == '__main__':
    unittest.main()