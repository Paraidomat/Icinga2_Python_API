from __future__ import absolute_import

import logging
import logging.config
import sys
from pprint import pprint

from icinga2.lib import actions, client, dependencies, downtimes, hosts
from icinga2.lib import hostgroups, notifications, services, servicegroups
from icinga2.lib import usergroup, susers, configPackages, configStagesFiles
from icinga2.lib import configWrapper


class Icinga2API(object):
    """ Main Class to implement the Icinga2 API """

    def __init__(self, username=None, password=None, url=None, debug=False):
        """ Initialize all needed Classes """
        self.log = logging.getLogger(__class__.__name__)
        self.log.debug("initialized.")
        stream_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler('/var/tmp/Icinga2API.log')
        #formatter = logging.Formatter(logging.BASIC_FORMAT)
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format_string)
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        #self.log.addHandler(stream_handler)
        self.log.addHandler(file_handler)

        if debug:
            self.log.setLevel(logging.DEBUG)

        self.client = client.Client()
        self.actions = actions.Actions(client=self.client)
        self.client.setconfig(username, password, url)
        self.downtimes = downtimes.Downtimes(client=self.client)
        self.dependencies = dependencies.Dependencies(client=self.client)
        self.hosts = hosts.Hosts(client=self.client)
        self.hostgroups = hostgroups.Hostgroups(client=self.client)
        self.notifications = notifications.Notifications(client=self.client)
        self.services = services.Services(client=self.client)
        self.servicegroups = servicegroups.Servicegroups(client=self.client)
        self.usergroups = usergroups.Usergroups(client=self.client)
        self.users = users.Users(client=self.client)

        self.config_packages = \
            configPackages.ConfigPackages(client=self.client)

        self.config_stages_files = \
            configStagesFiles.ConfigStagesFiles(client=self.client)

        self.config_wrapper = \
            configWrapper.ConfigWrapper(client=self.client)



if __name__ == '__main__':
    api = Icinga2API(username="root",
                     password="icinga2",
                     url="https://localhost:5665",
                     debug=True)
    pprint(api.hosts.problem_count())
