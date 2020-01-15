import requests

from server_request.server_request import BaseRequest
from settings import BEACON_GATEWAY_ID


class BeaconServerRequest(BaseRequest):

    def gateway_beacons_gateway_watchpost(self):
        """
        Retorna os beacons pertencentes a monitoramentos ativos que estejam sendo feitos por este gateway
        :return:
        """
        try:
            r = requests.get(self.IP_SERVER + "gateway_beacon/?gateway_beacon_id=%s" % BEACON_GATEWAY_ID,
                             headers=self.AUTH)

            if r.status_code == 200:
                if len(r.json()) > 0:
                    return r.json()
                raise requests.exceptions.RequestException('Resposta vazia.')
            else:
                print(r.status_code)
                raise requests.exceptions.RequestException(r.status_code)

        except requests.exceptions.RequestException as re:
            print(re)
            return None

    def get_allowed_beacons(self):
        """
        Faz um request no servidor para pegar os beacons cadastrados no sistema e que podem ser ouvidos por este
        dispositivo.
        :return: [{beacon},] ou []
        """
        try:
            r = requests.get(self.IP_SERVER+"beacon/", headers=self.AUTH)
            if self.is_valid(r):
                return r.json()
            return []
        except requests.exceptions.RequestException as re:
            print(re)
            return None
