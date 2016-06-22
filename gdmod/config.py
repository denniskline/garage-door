from configparser import ConfigParser
import os

class ApplicationConfiguration:

    def __init__(self, configDir=None, configFiles=None):
        self.configurations = []
        self.configDir = configDir

        if configFiles is not None:
            for configFile in configFiles:
                config = ConfigParser(os.environ)
                config.read('{}/{}'.format(configDir, configFile))
                self.configurations.append(config)

    def get(self, section, property=None, default=None):
        # If only the section is passed in, then let's assume that the caller is attempting to get a property from the 'DEFAULT' section
        if property is None:
            property = section
            section = 'DEFAULT'

        # Look for the first occurence of this property in the first configuration file that was read in
        for config in self.configurations:
            try:
                #print('Looking in section "{}" for "{}"'.format(section, property))
                return config.get(section, property)
            except Exception as e:
                #print("There was an error: {}".format(e))
                pass

        return default

    def get_conf_file_contents(self, fileName):
        if self.configDir is None or fileName is None:
            return ''

        with open('{}/{}'.format(self.configDir, fileName), 'r') as confFile:
            data=confFile.read()

        return data
