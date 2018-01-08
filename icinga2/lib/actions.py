from pprint import pformat
import logging


class Actions():
    """ Class that contains all informations about Hosts and corresponding
    funtions
    """

    def __init__(self, config=None, client=None):
        """ Initialize the Object with a given set of configurations."""

        self.client = client
        if config:
            self.config = config

        self.log = logging.getLogger('Icinga2API.action')

        self.filter = 'actions'

    def restart_process(self):
        """ Restarts the Icinga2 process """
        self.log.debug("Restarting Icinga2 process")
        return self.client.post_Data(
            self.client.URLCHOICES[self.filter]["restart-process"],
            data=None,
            override=False)

