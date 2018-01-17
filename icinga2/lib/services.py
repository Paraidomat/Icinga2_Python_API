from pprint import pformat
import logging
class Services():
    """
    Class that contains all informations about Services and corresponding funtions
    """

    SERVICE_STATUS = {
        "OK": 0,
        "WARNING": 1,
        "CRITICAL": 2,
        "UNKNOWN": 3
    }

    unhandled = []

    def __init__(self, config=None, client=None):
        """
        Initialize the Object with a given set of configurations.
        """
        self.client = client
        if config:
            self.config = config

        self.log = logging.getLogger('Icinga2API.service')

        self.filter = 'services'

    def add(self, servicename, hostname, servicedata=None):
        """
        Adding a Service with a given set of Attributes and/or Templates

        :param servicedata: Provides the needed variables to create a service.
        Example:
        data = {
            "templates": [ "generic-service" ],
            "attrs": {
                "check_command": "ping4",
            }
        }
        """

        def validate_servicedata(servicedata):
            NEEDED_VALUES = ["check_command"]

            for need in NEEDED_VALUES:
                if not need in servicedata['attrs']:
                    raise ValueError("Error in Servicedata, expected {} but was not found".format(need))

        if not servicedata:
            raise ValueError("ServiceData not set")
        else:
            validate_servicedata(servicedata)

        self.log.debug("Adding service with the following data: {}".format(pformat(servicedata)))
        self.client.put_Data(self.client.URLCHOICES[self.filter] + "/" + hostname + "!" + servicename, servicedata, override=False)

    def delete(self, hostname=None, servicename=None):
        """
        Delte a Service based on the hostname and servicename

        :param hostname: Hostname of the Host that is to be deleted
        """
        if not hostname and not servicename:
            raise ValueError("Hostname or Servicename not set")
        else:
            self.log.debug("Deleting Host with name: {}".format(hostname))
            self.client.delete_Data(self.client.URLCHOICES[self.filter] + "/" + hostname + "!" + servicename)

    def list(self, hostname=None, servicename=None, custom_filter=None,
             custom_filter_vars=None):
        """
        Method to list all services or only those for a single host

        :param hostname: can be used to only list one Host, if not set it will retrieve all Hosts
        :param servicename: used to narrow down services
        """
        attrs = ["name"]
        joins = []
        filters = None
        filter_vars = {}

        if hostname and not(custom_filter or custom_filter_vars):
            joins.append("host.name")
            filters = "host.name == hostname"
            filter_vars['hostname'] = hostname

        if servicename and not(custom_filter or custom_filter_vars):
            if filters:
                filters += " && match('servicename', service.name)"
            else:
                filters = "service.name == servicename"
            filter_vars['servicename'] = servicename

        if custom_filter and custom_filter_vars:
            filters = custom_filter
            filter_vars = custom_filter_vars

        payload = {}
        payload['attrs'] = attrs
        if joins:
            payload['joins'] = joins
        if filters:
            payload['filter'] = filters
            payload['filter_vars'] = filter_vars

        self.log.debug("Listing all Services that match: {}".format(pformat(payload)))
        ret = self.client.post_Data(self.client.URLCHOICES[self.filter], payload)

        return_list = []

        for attrs in ret['results']:
            return_list.append(attrs['name'])

        self.log.debug("Finished list of all matches: {}".format(pformat(return_list)))
        return return_list

    def unhandled_list(self):
        """
        Returns a list of all unhandled Services that is generated by the objects function
        """

        return self.unhandled

    def exists(self, servicename=None, hostname=None, custom_filter=None,
               custom_filter_vars=None):
        """
        Experimental
        """
        if not custom_filter and custom_filter_vars:
            if hostname and servicename:
                ret = self.list(servicename=servicename, hostname=hostname)
            else:
                ret = self.list(servicename=servicename)
        else:
            ret = self.list(custom_filter=custom_filter,
                            custom_filter_vars=custom_filter_vars)
        try:
            if ret.status_code == 200:
                return True
            else:
                return False
        except AttributeError:
            if len(ret) > 0:
                return True
            else:
                return False

    def objects(self, attrs=None, _filter=None, joins=None, process=True):
        """
        returns host objects that fit the filter and joins

        :attrs List: List of Attributes that are returned
        :_filter List: List of filters to be applied
        :joins List:
        :process Boolean: Used to control if Objects are being parsed
        """

        def unhandled(data):
            unhandled_list = []

            for attrs in data:
                if attrs['attrs']['state'] != 0.0 and attrs['attrs']['acknowledgement'] == 0.0 and attrs['attrs']['downtime_depth'] == 0.0:
                    unhandled_list.append(attrs['attrs']['__name'])
            return unhandled_list

        def handled(data, value):
            handled_list = []

            for attrs in data:
                if attrs['attrs']['state'] == value and attrs['attrs']['acknowledgement'] != 0.0 and attrs['attrs']['downtime_depth'] != 0.0:
                    handled_list.append(attrs['attrs']['__name'])
            return handled_list

        def count(data, value):
            problems = 0

            for attrs in data:
                if attrs['attrs']['state'] == value:
                    problems += 1

            return problems

        payload = {}

        if attrs:
            payload['attrs'] = attrs
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

        if process:
            self.warning_handled = handled(result['results'], self.SERVICE_STATUS["WARNING"])
            self.critical_handled = handled(result['results'], self.SERVICE_STATUS["CRITICAL"])
            self.unknown_handled = handled(result['results'], self.SERVICE_STATUS["UNKNOWN"])
            self.unhandled = unhandled(result['results'])
            self.ok = count(result['results'], self.SERVICE_STATUS['OK'])
            self.warning = count(result['results'], self.SERVICE_STATUS['WARNING'])
            self.critical = count(result['results'], self.SERVICE_STATUS['CRITICAL'])
            self.unknown = count(result['results'], self.SERVICE_STATUS['UNKNOWN'])

        return result['results']

    def problem_count(self):
        """
        Returns the ammount of services that are either CRITICAL, WARNING or UNKNOWN
        """
        return self.warning + self.critical + self.unknown

    def problem_handled_count(self):
        """
        Returns the ammount of services that are either CRITICAL, WARNING or UNKNOWN that are handled
        """
        return (self.warning + self.critical + self.unknown) - len(self.unhandled)

    def warning_count(self):
        """
        Returns the ammount of services that are in state Warning
        """
        return self.warning

    def warning_handled_count(self):
        """
        To be filled
        """
        return len(self.warning_handled)

    def critical_count(self, arg):
        """
        Returns the ammount of services that are in state Warning
        """
        return self.critical

    def critical_handled_count(self):
        """
        To be filled
        """

        return len(self.critical_handled)

    def unknown_count(self, arg):
        """
        To be filled
        """
        return self.unknown

    def unknown_handled_count(self, arg):
        """
        To be filled
        """
        return len(self.unknown_handled)
