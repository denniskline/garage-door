#!/usr/bin/python3

# Basic imports
from configparser import SafeConfigParser
import os
import datetime
from operator import itemgetter
import logging

# Library imports
from gdmod import ApplicationConfiguration
from gdmod import Database
from gdmod import Pi

# Pull in the configuration for this application
config = SafeConfigParser(os.environ)
config.read('conf/door.ini')
appConfig = ApplicationConfiguration(config)

print('environment variable in ini test: {}'.format(appConfig.get('env.var.in.ini.test')))

# Setup logger
logging.basicConfig(format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', 
    filename=appConfig.get('sms.door.log.file.directory') + '/' + appConfig.get('sms.door.log.file.name'), level=logging.INFO)

# Instantiate all the required modules
db = Database(appConfig.get('app.database.file'))
pi = Pi()

try:

except:
    logging.error('Failure', exc_info=True)
finally:
    logging.info('done')
