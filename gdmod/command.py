import time

class OpenCommand:

    def __init__(self, pi, db):
        self.pi = pi
        self.db = db
        pass

    def handle(self, message):
        print("Handling command to open door")
        if self.pi.is_door_closed():
            print("Door already open")
        elif self.db.find_door_lock() is None:
            print("Door locked, unable to open")
        else:
            self.pi.open_door()
            self.db.insert_door_state_history('open')

class CloseCommand:

    def __init__(self, pi, db):
        self.pi = pi
        self.db = db
        pass

    def handle(self, message):
        print("Handling command to close door")
        if self.pi.is_door_closed():
            print("Door already closed")
        elif self.db.find_door_lock() is None:
            print("Door locked, unable to close")
        else:
            self.pi.close_door()
            self.db.insert_door_state_history('close')

class LockCommand:

    def __init__(self, db):
        self.db = db
        pass

    def handle(self, message):
        print("Handling command to lock")
        self.db.insert_door_lock()

class StatusCommand:

    def __init__(self, pi, db, sms):
        self.pi = pi
        self.db = db
        self.sms = sms
        pass

    def handle(self, message):
        print("Handling command to status")
        phoneNumber = message.get("phoneFrom", None)
        if phoneNumber is not None:
            state = "closed" if self.pi.is_door_closed() else "open"
            statusMessage = ("State: {}".format(state))
            self.sms.send(phoneNumber, statusMessage)

class PhotoCommand:

    def __init__(self, pi, email):
        self.pi = pi
        self.email = email
        pass

    def handle(self, message):
        print("Handling command to photo")

class HelpCommand:

    def __init__(self, sms):
        self.sms = sms
        pass

    def handle(self, message):
        print("Handling command to help")

