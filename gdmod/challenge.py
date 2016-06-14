import string
import random

class Challenge:

    def __init__(self, db):
        self.db = db
        self.codeSize = 6
        self.chars = string.ascii_uppercase + string.digits
        pass

    def create(self, sid):
        print("Attempting to create a challenge to text message sid: {}".format(sid))
        code = self.generate_code()
        self.db.insert_door_challenge(code, sid)

    def fetch_message(self, code):
        print("Attempting to fetch a text message using challenge code: {}".format(code))
        if self.looks_like_a_code(code):
            textMessage = self.db.find_door_challenge(code)
            if textMessage is not None:
                self.db.delete_door_challenge(code) # make sure the same code is never found more than once
            return textMessage
        return None

    def generate_code(self):
        return ''.join(random.choice(self.chars) for _ in range(self.codeSize))

    def looks_like_a_code(self, code):
        return len(set(self.chars).intersection(code)) == self.codeSize
