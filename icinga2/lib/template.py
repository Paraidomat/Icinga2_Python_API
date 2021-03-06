from pprint import pformat
import logging
class Templates():
    """ Class that contains all informations about Hosts and corresponding
    funtions
    """

    def __init__(self, config=None, client=None):
        """ Initialize the Object with a given set of configurations."""

        self.client = client
        if config:
            self.config = config

        self.log = logging.getLogger('Icinga2API.template')

        self.filter = 'templates'

    def add(self, data=None):
        def validate_data(data):
            NEEDED_VALUES = ["name"]

            for need in NEEDED_VALUES:
                if not need in data['attrs']:
                    message = "Error in data, expected {} but was not found".format(need)
                    self.log.error(message)
                    raise ValueError(message)

        if not data:
            message = "data not set"
            self.log.error(message)
            raise ValueError(message)
        else:
            validate_data(data)

        name = data['attrs'].pop("name")


        self.log.debug("Adding template with the following data: {}".format(pformat(data)))
        return self.client.put_Data(self.client.URLCHOICES[self.filter] + "/" + name, data)


    def delete(self, name=None, cascade=False):
        """
        Delte a Host based on the hostname

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

    def list(self, name=None):
        """
        Method to list all hosts or only a select one
        Returns a list of all Hosts

        :param name: can be used to only list one Host, if not set it will retrieve all Hosts
        """
        if name is not None:
            host_filter = {
                "attrs": ["name"],
                "filter": "host.name == name",
                "filter_vars": {
                    "name": name
                }
            }
        else:
            host_filter = {
                "attrs": ["name"]
            }

        self.log.debug("Listing all Hosts that match: {}".format(pformat(host_filter)))
        ret = self.client.post_Data(self.client.URLCHOICES[self.filter], host_filter)

        return_list = []

        for attrs in ret['results']:
            return_list.append(attrs['name'])

        self.log.debug("Finished list of all matches: {}".format(pformat(return_list)))
        return return_list


    def exists(self, name=None):
        """
        Method to check if a single host exists

        :param name: Is needed to check if the Host exists, will throw a Value Exception when not set
        """
        if name:
            result = self.list(name=name)

            if not result:
                return False
            else:
                return True
        else:
            raise ValueError("Hostname was not set")

    def objects(self, attrs=None, _filter=None, joins=None):
        """
        returns host objects that fit the filter and joins

        :attrs List: List of Attributes that are returned
        :_filter List: List of filters to be applied
        :joins List:
        """

        def problem_count(data, value):
            problems = 0

            for attrs in data:
                if attrs['attrs']['state'] == value:
                    problems += 1

            return problems

        payload = {}

        if attrs:
            payload['attrs'] = attrs
        else:
            payload['attrs'] = ['name', 'state', 'acknowledgement', 'downtime_depth', 'last_check']

        self.log.debug("Attrs set to: {}".format(pformat(payload['attrs'])))

        if _filter:
            payload['filter'] = _filter
            self.log.debug("Filter set to: {}".format(pformat(payload['filter'])))

        if joins:
            payload['joins'] = joins
            self.log.debug("Joins set to: {}".format(pformat(payload['joins'])))

        self.log.debug("Payload: {}".format(pformat(payload)))

        result = self.client.post_Data(self.client.URLCHOICES[self.filter], payload)

        self.log.debug("Result: {}".format(result))

        if result['results']:
            self.problems_down = problem_count(result['results'], self.HOST_STATUS['DOWN'])
            self.problems_critical = problem_count(result['results'], self.HOST_STATUS['CRITICAL'])
            self.problems_unknown = problem_count(result['results'], self.HOST_STATUS['UNKNOWN'])

        return result['results']

    def problem_count(self):
        """
        Return the count of hosts with problems that are neither acknowledged or have a downtime
        """
        count = 0

        host_data = self.objects()

        for data in host_data:
            if data['attrs']['downtime_depth'] == 0 and data['attrs']['acknowledgement'] == 0 and data['attrs']['state'] != 0:
                self.log.debug("Found match for Host: {}".format(pformat(data['name'])))
                count += 1

        return count

    def problem_list(self):
        """
        Lists all Hosts and their severity count in a sorted order
        """

        host_problems = {}

        host_data = self.objects()

        for host in host_data:
            if host['attrs']['state'] != 0:
                host_problems[host['name']] = self.host_severity(host['attrs'])
                self.log.debug("Calculated Severity for {} is {}".format(host['name'], host_problems[host['name']]))

        if len(host_problems) != 0:
            host_problems_severity = sorted(host_problems, reverse=True)
            return host_problems_severity
        else:
            return {}

    def severity(self, attrs):
        """
        Calculate the severity
        """

        def last_check(last_check_time):
            from datetime import datetime, timedelta

            last_check_time = datetime.fromtimestamp(last_check_time)
            now = datetime.now

            if now > last_check_time + timedelta(seconds=20):
                return False
            else:
                return True

        severity = 0

        self.log.debug("calculating severity for {}".format(pformat(attrs['name'])))

        if attrs['acknowledgement'] != 0:
            severity += 2
        elif attrs['downtime_depth'] > 0:
            severity += 1
        else:
            severity += 4

        check_status = last_check()

        if check_status:
            severity += 16

        if attrs['state'] != 0:
            if attrs['state'] == 1:
                severity += 32
            elif attrs['state'] == 2:
                severity += 64
            else:
                severity += 256

        self.log.debug("calculated severity for {} is {}".format(pformat(attrs['name']), severity))
        return severity
