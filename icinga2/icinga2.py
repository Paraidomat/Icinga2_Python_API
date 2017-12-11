from __future__ import absolute_import

import logging
import sys
from pprint import pprint

from icinga2.lib import client, downtimes, hosts, hostgroups, notifications
from icinga2.lib import services, servicegroups, usergroups, users
from icinga2.lib import configPackages, configStages, configStagesFiles
from icinga2.lib import configWrapper


class Icinga2API(object):
    """ Main Class to implement the Icinga2 API """

    def __init__(self, username=None, password=None, url=None, debug=False):
        """ Initialize all needed Classes """
        self.log = logging.getLogger(__class__.__name__)
        self.log.debug("initialized.")
        streamhandler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        streamhandler.setFormatter(formatter)
        self.log.addHandler(streamhandler)

        if debug:
            self.log.setLevel(logging.DEBUG)

        self.client = client.Client()
        self.client.setconfig(username, password, url)
        self.downtimes = downtimes.Downtimes(client=self.client)
        self.hosts = hosts.Hosts(client=self.client)
        self.hostgroups = hostgroups.Hostgroups(client=self.client)
        self.notifications = notifications.Notifications(client=self.client)
        self.services = services.Services(client=self.client)
        self.servicegroups = servicegroups.Servicegroups(client=self.client)
        self.usergroups = usergroups.Usergroups(client=self.client)
        self.users = users.Users(client=self.client)

        self.config_packages = \
            configPackages.ConfigPackages(client=self.client)

        self.config_stages = \
            configStages.ConfigStages(client=self.client)

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
