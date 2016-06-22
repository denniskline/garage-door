import unittest
from gdmod.authorization import Authorization

# garage-door> python3 -m unittest test.test_authorization
class AuthorizationTest(unittest.TestCase):

    # ************************************************************************
    # Test Cases

    def test_authorized_phone_numbers_are_authorized(self):
        az = Authorization(' 1112223333, 1112224444 ')
        self.assertTrue(az.is_authorized({'phoneFrom': '1112223333'}))
        self.assertTrue(az.is_authorized({'phoneFrom': '1112224444'}))

    def test_unauthorized_phone_numbers_are_NOT_authorized(self):
        az = Authorization(' 1112223333, 1112224444 ')
        self.assertFalse(az.is_authorized({'phoneFrom': '9991118888'}))
        self.assertFalse(az.is_authorized({'phoneFrom': 'abc'}))
        self.assertFalse(az.is_authorized({'phoneFrom': '111-222-3333'}))

    def test_message_does_not_contain_a_key_phoneFrom(self):
        az = Authorization(' 1112223333, 1112224444 ')
        with self.assertRaises(ValueError): 
            az.is_authorized({})

    def test_authorize_raises_error_when_unauthorized(self):
        az = Authorization(' 1112223333, 1112224444 ')
        with self.assertRaises(ValueError): 
            az.authorize({'phoneFrom': '9991118888'})

if __name__ == '__main__':
    unittest.main()