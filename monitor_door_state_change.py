#!/usr/bin/python3

import os
import datetime
import time
import logging
import getopt
import sys
from gdmod import ApplicationConfiguration
from gdmod import Database
from gdmod import Pi
from gdmod import Dropbox

def main():
    # Check command options to see if a custom configuration directory was supplied
    configDir = os.path.abspath(get_config_directory(sys.argv[1:], './conf'))
    if not os.path.isdir(configDir):
        raise ValueError('No such configuration directory exists: {}'.format(configDir))

    # Read in the configurations
    config = ApplicationConfiguration(configDir, ['door.ini', 'account-settings.ini'])

    # Setup logger
    logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', 
        filename=config.get('door.state.change.log.file.directory') + '/' + config.get('door.state.change.log.file.name'), level=logging.INFO)

   # Instantiate all the required modules
    db = Database(config.get('app.database.file'))
    pi = Pi()
    basePhotoDir = config.get('door.media.photo.directory')
    dropbox = Dropbox(config.get('dropbox.gd.access.token'))

    # Watch for any changes to the state of the door.  At least until True stops being True
    while True:
        try:
            doorState = 'closed' if pi.is_door_closed() else 'open'
            latestStateHistory = db.find_door_state_history_latest()
            logging.debug('latestStateHistory: {}'.format(latestStateHistory))

            # If a state change is detected, persist the new state
            if latestStateHistory is None or doorState != latestStateHistory.get('state', None):
                logging.info("Setting door state to: {}".format(doorState))
                db.insert_door_state_history(doorState, datetime.datetime.now())
                
                # When to door is opening, take a few pictures
                if doorState == 'open':
                    take_some_pictures(pi, dropbox, basePhotoDir, 4)

        except:
            logging.error('Failure while monitoring door state change', exc_info=True)
            pass

        # Pause a little before checking again
        time.sleep(2)

# Take a series of pictures with a small pause so we can 'record' the view of the door state change
def take_some_pictures(pi, dropbox, basePhotoDir, numPhotos):
    photoDir = ('{}/{}'.format(basePhotoDir, datetime.datetime.now().strftime("%Y%m%d")))
    photos = []
    for x in range(0, numPhotos):
        photoFileName = pi.take_picture(photoDir)
        photos.append(photoFileName)
        time.sleep(2)

    # TODO Offload this in another thread (takes too long in the root thread)
    for photo in photos:
        dropbox.upload(photo)

def get_config_directory(args, default):
    options, remainder = getopt.getopt(args, 'c:', ['configdirectory=',])

    for opt, arg in options:
        if opt in ('-c', '--configdirectory'):
            return arg
    return default

if __name__ == "__main__":
    main()
