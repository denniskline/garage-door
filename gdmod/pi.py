import datetime
import time
import logging
import random
import os
import picamera
from gpiozero import InputDevice
#from gpiozero import DigitalOutputDevice
from gpiozero import OutputDevice
from gpiozero import LED

# OutputDevice: active_high must be false or the wall panel will shut off
class Pi:

    def __init__(self):
        self.redLightOn = False
        self.yellowLightOn = False
        self.greenLightOn = False
        #self.garageOpener = OutputDevice(18, active_high=True, initial_value=False)
        self.garageOpener = OutputDevice(18, active_high=False, initial_value=False)
        self.reedSwitch = InputDevice(23,False) # Pull down input device
        self.ledGreen = LED(22)
        self.ledYellow = LED(27)
        self.ledRed = LED(17)
        pass

    def click_door(self):
        logging.info("Clicking door")
        self.garageOpener.on()
        time.sleep(1)
        self.garageOpener.off()
        time.sleep(5) # Wait a few seconds for the door to fully do its thing

    def is_door_closed(self):
        #return True if random.randrange(0,2) == 1 else False
        return not self.reedSwitch.is_active

    def green_light_on(self):
        logging.debug("green light on")
        try:
            self.greenLightOn = True
            self.ledGreen.on()
        except:
            logging.warn("Unable to turn on green light", exc_info=True)

    def yellow_light_on(self):
        logging.debug("yellow light on")
        try:
            self.yellowLightOn = True
            self.ledYellow.on()
        except:
            logging.warn("Unable to turn on yellow light", exc_info=True)

    def red_light_on(self):
        logging.debug("red light on")
        try:
            self.redLightOn = True
            self.ledRed.on()
        except:
            logging.warn("Unable to turn on red light", exc_info=True)

    def green_light_off(self):
        logging.debug("Turning green light off")
        try:
            self.greenLightOn = False
            self.ledGreen.off()
        except:
            logging.warn("Unable to turn off green light", exc_info=True)

    def yellow_light_off(self):
        logging.debug("Turning yellow light off")
        try:
            self.yellowLightOn = False
            self.ledYellow.off()
        except:
            logging.warn("Unable to turn off yellow light", exc_info=True)

    def red_light_off(self):
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
            camera.resolution = (1920, 1080)
            #camera.resolution = (2592, 1944)
            camera.framerate = 15
            #camera.brightness = 70 
            camera.rotation = 90
            camera.capture(file)
        finally:
            camera.close()

        return file

    def diagnostics(self):
        diag = {}
        diag['Door'] = "closed" if self.is_door_closed() else "open"
        diag['Uptime'] = self.__find_uptime()
        diag['Temp'] = ("{}'C (80'C is high)".format(self.__find_system_temp()))
        diag['Network Down'] = self.is_yellow_light_on()
        diag['Error'] = self.is_red_light_on()
        return diag

    def __find_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(datetime.timedelta(seconds = uptime_seconds))        

    def __find_system_temp(self):
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        return float(temp.split('=')[1][:-3])
