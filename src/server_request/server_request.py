import requests

from settings import IP_SERVER, TOKEN


class BaseRequest:

    def __init__(self):
        self.allowed_resources = ('beacon', 'watchpost', 'teste')
        self.AUTH = {'Authorization': "Token "+TOKEN}
        self.IP_SERVER = IP_SERVER

    def create_url(self, resource, kwargs=None):
        url = self.IP_SERVER+resource+'/'

        if kwargs:
            query_string = "?"
            for index, key in enumerate(kwargs):
                if index != 0:
                    query_string += "&{}={}".format(key, str(kwargs[key]))
                else:
                    query_string += "{}={}".format(key, str(kwargs[key]))
            url += query_string

        return url

    @staticmethod
    def is_valid(r):
        try:
            if r.status_code == 200:
                if len(r.json()) > 0:
                    return True
            return False
        except requests.exceptions.RequestException as re:
            print(re)
            return None

    def get_resources(self, resources):
        responses = {}

        for resource in resources:

            assert resource in self.allowed_resources, "Recurso %s não disponível. Recursos diponíveis: %s" % \
                                                       (resource, self.allowed_resources)
            if resource in responses:
                continue

            try:
                r = requests.get(IP_SERVER+resource+'/', headers=self.AUTH)
                if r.status_code == 200:
                    if len(r.json()) > 0:
                        responses[resource] = r.json()

                return responses
            except requests.exceptions.RequestException as re:
                print(re)
                return None



