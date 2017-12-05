from . import client

class ConfigPackages():
    """ Class that contains all informations about downtimes and
    corresponding funtions
    """

    def __init__(self, config=None, client=None):
        """ Initialize the Object with a given set of configurations. """

        self.client = client

        if config:
            self.config = config

        self.log = logging.getLogger('Icinga2API.configPackages')

        self.filter = "configPackages"

    def add(self, name=None):
        """ Add a Config Package with a specific name. """

        # Package names starting with underscore are reserved for internal
        # usage and they may not be added via the API
        if name[0] == '_':
            self.log.error('Package name {} starts with a _.'.format(name))
            raise ValueError('Package name {} starts with a _.'.format(name))

        self.log.debug('Adding Config Package with name: {}'.format(name))
        return self.client.post_Data(self.client.URLCHOICES[self.filter]
                                     + '/' + name)

    def list(self, name=None):
        """ Get all or one specific config package """

        self.log.debug('Get all Config Packages')

        config_packages = self.client.get(self.client.URLCHOICES[self.filter])
        config_packages = config_packages['results']

        if name:
            config_packages = [cp for cp in config_packages
                               if cp['name'] == name]

        return config_packages

    def delete(self, name=None):
        """ Delete a Config Package based on it's name """

        if not name:
            self.log.error('name not set!')
            raise ValueError('name not set!')

        self.log.debug('Deleting config package with name: {}'.format(name))
        return self.client.delete_Data(self.client.URLCHOICES[self.filter]
                                       + '/' + name)
