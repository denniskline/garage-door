import time
import logging

class Pi:

    def __init__(self):
        self.redLightOn = False
        self.yellowLightOn = False
        self.greenLightOn = False
        self.isDoorClosed = True # TODO: This will be a GPIO test and not a member variables
        pass

    def open_door(self):
        logging.info("Opening door")
        self.isDoorClosed = False
        #time.sleep(1) # Garage door takes N seconds to open, wait a bit for that to finish

    def close_door(self):
        logging.info("Closing door")
        self.isDoorClosed = True
        #time.sleep(1) # Garage door takes N seconds to close, wait a bit for that to finish

    def is_door_closed(self):
        return self.isDoorClosed

    def blink_green_light(self, interval=None):
        interval = interval if interval else 1
        logging.debug("Blinking green light with an interval of: {}".format(interval))
        try:
            self.greenLightOn = True
        except:
            logging.warn("Unable to blink green light", exc_info=True)

    def blink_yellow_light(self, interval=None):
        interval = interval if interval else 1
        logging.debug("Blinking yellow light with an interval of: {}".format(interval))
        try:
            self.yellowLightOn = True
        except:
            logging.warn("Unable to blink yellow light", exc_info=True)

    def blink_red_light(self, interval=None):
        interval = interval if interval else 1
        logging.debug("Blinking red light with an interval of: {}".format(interval))
        try:
            self.redLightOn = True
        except:
            logging.warn("Unable to blink red light", exc_info=True)

    def off_green_light(self):
        logging.debug("Turning green light off")
        try:
            self.greenLightOn = False
        except:
            logging.warn("Unable to turn off green light", exc_info=True)

    def off_yellow_light(self):
        logging.debug("Turning yellow light off")
        try:
            self.yellowLightOn = False
        except:
            logging.warn("Unable to turn off yellow light", exc_info=True)

    def off_red_light(self):
        logging.debug("Turning red light off")
        try:
            self.redLightOn = False
        except:
            logging.warn("Unable to turn off red light", exc_info=True)

    def is_green_light_on(self):
        return self.greenLightOn
        
    def is_yellow_light_on(self):
        return self.yellowLightOn
        
    def is_red_light_on(self):
        return self.redLightOn

