from . import client

import logging

class ConfigStagesFiles():
    """ Class that contains all informations about downtimes and
    corresponding funtions
    """

    def __init__(self, config=None, client=None):
        """ Initialize the Object with a given set of configurations. """

        self.client = client

        if config:
            self.config = config

        self.log = logging.getLogger(
            'Icinga2API.{}'.format(__class__.__name__))

        self.filter = "configStagesFiles"

    def add(self, config_package_name=None, configuration_data=None,
            restart=False):
        """ Add a Configuration Stage to a Config Package.

        configuration_data = {
            'files': {
                'filename_a': 'configuration_a',
                'filename_b': 'configuration_b'
            }
        }"""

        self.log.debug('''Add-method got values:
                       config_package_name: {},
                       configuration_data: {},
                       restart: {}'''.format(config_package_name,
                                             configuration_data,
                                             restart))

        if not config_package_name:
            err = 'config_package_name not specified'
            self.log.error(err)
            raise ValueError(err)
        if not configuration_data:
            err = 'configuration_data not specified'
            self.log.error(err)
            raise ValueError(err)

        try:
            data = {
                'files': configuration_data['files']
            }
            if restart:
                data['reload'] = restart
        except KeyError:
            err = 'configuration_data must have key "files"'
            self.log.error(err)
            raise KeyError(err)

        self.log.debug('Adding configuration stage to Configuration Package')
        return self.client.post_Data(self.client.URLCHOICES['configStages']
                                         + '/' + config_package_name,
                                     data, False)

    def list(self, config_package_name=None, config_stage_name=None):
        """ Get Information about all or one specific configuration stage. """

        if not config_package_name:
            err = 'config_package_name not specified.'
            self.log.error(err)
            raise ValueError(err)
        if not config_stage_name:
            err = 'config_stage_name not specified.'
            self.log.error(err)
            raise ValueError(err)

        self.log.debug('Get Information about config stage')
        url = (self.client.URLCHOICES['configStages']
               + '/' + config_package_name
               + '/' + config_stage_name)
        return self.client.get_Data(url)

    def delete(self, config_package_name=None, config_stage_name=None):
        """ Delete a Config Stage based on it's name """

        if not config_package_name:
            err = 'config_package_name not specified.'
            self.log.error(err)
            raise ValueError(err)
        if not config_stage_name:
            err = 'config_stage_name not specified.'
            self.log.error(err)
            raise ValueError(err)

        return self.client.delete_Data(self.client.URLCHOICES['configStage']
                                       + '/' + config_package_name
                                       + '/' + config_stage_name)
