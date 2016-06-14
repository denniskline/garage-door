import time

class Pi:

    def __init__(self):
        self.redLightOn = False
        self.yellowLightOn = False
        self.isDoorClosed = True # TODO: This will be a GPIO test and not a member variables
        pass

    def open_door(self):
        print("Opening door")
        self.isDoorClosed = False
        #time.sleep(1) # Garage door takes N seconds to open, wait a bit for that to finish

    def close_door(self):
        print("Closing door")
        self.isDoorClosed = True
        #time.sleep(1) # Garage door takes N seconds to close, wait a bit for that to finish

    def is_door_closed(self):
        return self.isDoorClosed

    def blink_red_light(self, interval=None):
        interval = interval if interval else 1
        print("Blinking red light with an interval of: {}".format(interval))
        self.redLightOn = True

    def blink_yellow_light(self, interval=None):
        interval = interval if interval else 1
        print("Blinking yellow light with an interval of: {}".format(interval))
        self.yellowLightOn = True

    def off_red_light(self):
        print("Turning red light off")
        self.redLightOn = False

    def off_yellow_light(self):
        print("Turning yellow light off")
        self.redLightOn = False

    def is_red_light_on(self):
        return self.redLightOn

    def is_yellow_light_on(self):
        return self.yellowLightOn
