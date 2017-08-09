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
class DoorRemote:

    def __init__(self):
        self._garageOpener = OutputDevice(18, active_high=False, initial_value=False)
        pass

    def click_door(self):
        logging.info("Clicking door")
        self._garageOpener.on()
        time.sleep(.5)
        self._garageOpener.off()


class DoorState:

    def __init__(self):
        self._reedSwitch = InputDevice(23,False) # Pull down input device
        pass

    def is_door_closed(self):
        #return True if random.randrange(0,2) == 1 else False
        return not self._reedSwitch.is_active


class Light:

    def __init__(self):
        self._ledGreen = LED(22)
        self._ledYellow = LED(27)
        self._ledRed = LED(17)
        pass

    def green_light_on(self):
        logging.debug("green light on")
        try:
            self._ledGreen.on()
        except:
            logging.warn("Unable to turn on green light", exc_info=True)

    def yellow_light_on(self):
        logging.debug("yellow light on")
        try:
            self._ledYellow.on()
        except:
            logging.warn("Unable to turn on yellow light", exc_info=True)

    def red_light_on(self):
        logging.debug("red light on")
        try:
            self._ledRed.on()
        except:
            logging.warn("Unable to turn on red light", exc_info=True)

    def green_light_off(self):
        logging.debug("Turning green light off")
        try:
            self._ledGreen.off()
        except:
            logging.warn("Unable to turn off green light", exc_info=True)

    def yellow_light_off(self):
        logging.debug("Turning yellow light off")
        try:
            self._ledYellow.off()
        except:
            logging.warn("Unable to turn off yellow light", exc_info=True)

    def red_light_off(self):
        logging.debug("Turning red light off")
        try:
            self._ledRed.off()
        except:
            logging.warn("Unable to turn off red light", exc_info=True)

    def is_green_light_on(self):
        return self._ledGreen.is_lit()
        
    def is_yellow_light_on(self):
        return self._ledYellow.is_lit()
        
    def is_red_light_on(self):
        return self._ledRed.is_lit()


class Camera:

    def take_picture(self, photoDir, overlayMessage=None):
        logging.debug('taking a picture')
        if not os.path.exists(photoDir):
            os.makedirs(photoDir)
        fileName = ('{}_gd_photo.jpg'.format(datetime.datetime.now().strftime("%H%M%S")))
        file = ('{}/{}'.format(photoDir, fileName))

        overlay = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if overlayMessage is not None:
            overlay += ('  {}'.format(overlayMessage))

        camera = picamera.PiCamera()
        try:
            camera.resolution = (1024, 768)
            camera.rotation = 90
            camera.annotate_background = picamera.Color('black')
            camera.annotate_text = overlay
            camera.capture(file)
        finally:
            camera.close()

        return file

         
class Pi:

    def __init__(self):
        pass

   def diagnostics(self):
        diag = {}
        diag['Uptime'] = self.__find_uptime()
        diag['Temp'] = ("{}'C (80'C is high)".format(self.__find_system_temp()))
        return diag

    def __find_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(datetime.timedelta(seconds = uptime_seconds))        

    def __find_system_temp(self):
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        return float(temp.split('=')[1][:-3])
