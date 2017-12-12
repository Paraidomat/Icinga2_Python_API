from requests import Session
import urllib3
import logging
import json


class Client(object):
    """ Main Class to implement the Icinga2 API Client """

    URLCHOICES = {
        "hosts": "/v1/objects/hosts",
        "hostgroups": "/v1/objects/hostgroups",
        "services": "/v1/objects/services",
        "servicegroups": "/v1/objects/servicegroups",
        "notifications": "/v1/objects/notifications",
        "downtimes": "/v1/objects/downtimes",
        "users": "/v1/objects/users",
        "usergroups": "/v1/objects/usergroups",
        "dependencies": "/v1/objects/dependencies",
        "configPackages": "/v1/config/packages",
        "configStages": "/v1/config/stages",
        "configStagesFiles": "/v1/config/files",
    }

    def __init__(self):
        """ Initialize all needed Variables """

        self.log = logging.getLogger(
            'Icinga2API.{}'.format(__class__.__name__))
        self.connection = Session()
        self.connection.headers.update({'Accept': 'application/json'})
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def setconfig(self, username=None, password=None, url=None):
        if url is not None:
            self.baseurl = url
        else:
            raise ValueError("No URL set")

        self.connection.auth = (username, password)

    def get_Data(self, url):
        """ Get Data from icinga2 """

        try:
            ret = self.connection.get(self.baseurl + url, verify=False)
            self.log.debug('Got return data: {}'.format(
                json.dumps(ret.json(), indent=2)))
            if not (200 <= ret.status_code <= 299):
                logging.error(json.dumps(ret.json()["results"], indent=2))
                ret.raise_for_status()
            return json.loads(ret.text)
        except Exception as e:
            self.log.error(e)
            raise

    def delete_Data(self, url):
        """ Delete Data from icinga2 """

        try:
            ret = self.connection.delete(self.baseurl + url, verify=False)
            if not (200 <= ret.status_code <= 299):
                logging.error(json.dumps(ret.json()["results"], indent=2))
                ret.raise_for_status()
            self.log.debug('Got return data: {}'.format(
                json.dumps(ret.json(), indent=2)))
            return json.loads(ret.text)
        except Exception as e:
            self.log.error(e)
            raise

    def put_Data(self, url, data):
        """ Put Data into Icinga2 via the API

        :param url: type of uri to attach to url
        :param data: Data Dictionary that is used to add values to Icinga2
        """

        try:
            ret = self.connection.put(
                self.baseurl + url,
                data=json.dumps(data),
                verify=False)
            self.log.debug('Got return data: {}'.format(
                json.dumps(ret.json(), indent=2)))
            if not (200 <= ret.status_code <= 299):
                try:
                    logging.error(json.dumps(ret.json()["results"], indent=2))
                except KeyError:
                    logging.error(json.dumps(ret.json(), indent=2))
                ret.raise_for_status()
            return json.loads(ret.text)
        except Exception as e:
            self.log.error(e)
            raise


    def post_Data(self, url, data, override=True):
        """ POST method

        :param type: type of uri to attach to url
        :param data: Data Dictionary that is used to query the Icinga2API
        """
        try:
            if override:
                headers = {'X-HTTP-Method-Override': 'GET'}
            else:
                headers = None
            self.log.debug(
                'This is the request: url: {} headers: {} data: {}'.format(
                    self.baseurl + url, headers + self.connection.headers,
                    json.dumps(data, indent=2)))
            ret = self.connection.post(
                self.baseurl + url,
                headers=headers,
                data=json.dumps(data),
                verify=False)
            self.log.debug('Got return data: {}'.format(ret.text))
            if not (200 <= ret.status_code <= 299):
                try:
                    logging.error(json.dumps(ret.json()["results"], indent=2))
                except KeyError:
                    logging.error(json.dumps(ret.json(), indent=2))
                ret.raise_for_status()
            return json.loads(ret.text)
        except Exception as e:
            self.log.error(e)
            raise
