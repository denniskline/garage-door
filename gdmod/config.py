from configparser import SafeConfigParser
import os

class ApplicationConfiguration:

    def __init__(self, configDir, configFiles):
        self.configurations = []

        for configFile in configFiles:
            config = SafeConfigParser(os.environ)
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
