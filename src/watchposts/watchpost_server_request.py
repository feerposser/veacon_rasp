import requests

from server_request.server_request import BaseRequest
from settings import BEACON_GATEWAY_ID


class WatchpostServerRequest(BaseRequest):

    def get_watchposts(self):
        """

        :return:
        """
        r = requests.get(self.IP_SERVER+'watchpost', headers=self.AUTH)
        if self.is_valid(r):
            return r.json()
        return {}

    def get_watchposts_gateway_beacon(self):
        """
        Retorna monitoramentos (watchposts) cadastrados neste gateway
        :return:
        """
        r = requests.get(self.IP_SERVER+'watchpost_gateway/?gateway_beacon_id=%s' % BEACON_GATEWAY_ID,
                         header=self.AUTH)

        if self.is_valid(r):
            return r.json()
        return None
