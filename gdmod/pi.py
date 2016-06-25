import datetime
import time
import logging
import random
import os
import picamera
from gpiozero import InputDevice
from gpiozero import LED

class Pi:

    def __init__(self):
        self.redLightOn = False
        self.yellowLightOn = False
        self.greenLightOn = False
        self.isDoorClosed = True # TODO: This will be a GPIO test and not a member variables
        self.gpio18 = InputDevice(18,False) # Pull down input device
        self.ledGreen = LED(17)
        self.ledYellow = LED(27)
        self.ledRed = LED(22)
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
        #return True if random.randrange(0,2) == 1 else False
        #return self.isDoorClosed
        return not self.gpio18.is_active

    def blink_green_light(self, interval=None):
        interval = interval if interval else 1
        logging.debug("Blinking green light with an interval of: {}".format(interval))
        try:
            self.greenLightOn = True
            self.ledGreen.on()
        except:
            logging.warn("Unable to blink green light", exc_info=True)

    def blink_yellow_light(self, interval=None):
        interval = interval if interval else 1
        logging.debug("Blinking yellow light with an interval of: {}".format(interval))
        try:
            self.yellowLightOn = True
            self.ledYellow.on()
        except:
            logging.warn("Unable to blink yellow light", exc_info=True)

    def blink_red_light(self, interval=None):
        interval = interval if interval else 1
        logging.debug("Blinking red light with an interval of: {}".format(interval))
        try:
            self.redLightOn = True
            self.ledRed.on()
        except:
            logging.warn("Unable to blink red light", exc_info=True)

    def off_green_light(self):
        logging.debug("Turning green light off")
        try:
            self.greenLightOn = False
            self.ledGreen.off()
        except:
            logging.warn("Unable to turn off green light", exc_info=True)

    def off_yellow_light(self):
        logging.debug("Turning yellow light off")
        try:
            self.yellowLightOn = False
            self.ledYellow.off()
        except:
            logging.warn("Unable to turn off yellow light", exc_info=True)

    def off_red_light(self):
        logging.debug("Turning red light off")
        try:
            self.redLightOn = False
            self.ledRed.off()
        except:
            logging.warn("Unable to turn off red light", exc_info=True)

    def is_green_light_on(self):
        return self.greenLightOn
        
    def is_yellow_light_on(self):
        return self.yellowLightOn
        
    def is_red_light_on(self):
        return self.redLightOn

    def take_picture(self, photoDir):
        logging.debug('taking a picture')
        if not os.path.exists(photoDir):
            os.makedirs(photoDir)
        fileName = ('{}_gd_photo.jpg'.format(datetime.datetime.now().strftime("%H%M%S")))
        file = ('{}/{}'.format(photoDir, fileName))

        camera = picamera.PiCamera()
        try:
            #camera.resolution = (1920, 1080)
            camera.resolution = (2592, 1944)
            camera.framerate = 15
            camera.brightness = 70 
            camera.capture(file)
        finally:
            camera.close()

        return file

    def diagnostics(self):
        diag = {}
        diag['Door'] = "closed" if self.is_door_closed() else "open"
        diag['Uptime'] = self.__find_uptime()
        diag['Network light on'] = self.is_yellow_light_on()
        diag['Error light on'] = self.is_red_light_on()
        return diag

    def __find_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(datetime.timedelta(seconds = uptime_seconds))        

