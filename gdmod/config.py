class ApplicationConfiguration:

    def __init__(self, config):
        self.config = config
        pass

    def get(self, section, property=None, default=None):
        # If only the section is passed in, then let's assume that the caller is attempting to get a property from the 'DEFAULT' section
        if property is None:
            property = section
            section = 'DEFAULT'
        try:
            return self.config.get(section, property)
        except:
            return default
