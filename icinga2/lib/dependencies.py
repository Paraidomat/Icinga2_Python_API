from pprint import pformat
import urllib.parse
import logging
class Dependencies():
    """ Class that contains all informations about Hosts and corresponding
    funtions
    """

    def __init__(self, config=None, client=None):
        """ Initialize the Object with a given set of configurations."""

        self.client = client
        if config:
            self.config = config

        self.log = logging.getLogger('Icinga2API.dependency')

        self.filter = 'dependencies'

    def add(self, dependencyname=None, hostname=None, data=None):
        def validate_data(data):
            NEEDED_VALUES = ["parent_host_name", "parent_service_name",
                             "child_host_name", "child_service_name",
                             "disable_checks"]

            for need in NEEDED_VALUES:
                if not need in data['attrs']:
                    message = "Error in data, expected {} but was not found".format(need)
                    self.log.error(message)
                    raise ValueError(message)

        data['attrs']['child_host_name'] = hostname
        if not data:
            message = "data not set"
            self.log.error(message)
            raise ValueError(message)
        else:
            validate_data(data)

        self.log.debug("Adding dependency with the following data: {}".format(pformat(data)))
        url = '{}/{}!{}!{}'.format(
            self.client.URLCHOICES[self.filter],
            hostname,
            urllib.parse.quote(data['attrs']['child_service_name'], safe='§'),
            dependencyname)
        return self.client.put_Data(url, data)


    def delete(self, name=None, cascade=False):
        """
        Delete a Dependency based on the name

        :param name: Hostname of the Host that is to be deleted
        """
        if not name:
            raise ValueError("Hostname not set")
        else:
            url = self.client.URLCHOICES[self.filter] + "/" + name
            if cascade:
                url = url + "?cascade=1"
            self.log.debug("Deleting Host with name: {}".format(name))
            return self.client.delete_Data(url)

    def list(self, name=None, custom_filter=None, custom_filter_vars=None):
        """
        Method to list all dependencies or only a select one
        Returns a list of all Dependencies

        :param name: can be used to only list one Dependency, if not set it will retrieve all Hosts
        """
        if name is not None:
            dependency_filter = {
                "attrs": ["name"],
                "filter": "dependency.name == name",
                "filter_vars": {
                    "name": name
                }
            }
        else:
            if custom_filter and custom_filter_vars:
                filters=custom_filter,
                for key, value in custom_filter_vars:
                    filter_vars[key] = value
            else:
                dependency_filter = {"attrs": ["name"]}

        self.log.debug("Listing all Dependencies that match: {}".format(pformat(dependency_filter)))
        ret = self.client.post_Data(self.client.URLCHOICES[self.filter], dependency_filter)

        return_list = []

        for attrs in ret['results']:
            return_list.append(attrs['name'])

        self.log.debug("Finished list of all matches: {}".format(pformat(return_list)))
        return return_list


    def exists(self, name=None):
        """
        Method to check if a single Dependency exists

        :param name: Is needed to check if the Host exists, will throw a Value Exception when not set
        """
        if name:
            result = self.list(name=name)

            if not result:
                return False
            else:
                return True
        else:
            raise ValueError("Dependencyname was not set")
