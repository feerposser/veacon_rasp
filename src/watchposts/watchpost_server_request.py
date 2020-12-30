from builtins import enumerate

import requests

from server_request.server_request import BaseRequest
from settings import BEACON_GATEWAY_ID


class WatchpostServerRequest(BaseRequest):

    def get_watchposts(self, add_watchpost_format=False, **kwargs):
        """
        Não me orgulho desse método. Retorna os dados de monitoramento ativo do sistema.
        :param add_watchpost_format: Bool. Indica se deve estar formatado ou não
        :return: list
        """
        try:
            url = self.create_url('watchpost', kwargs)

            print(url)

            r = requests.get(url=url, headers=self.AUTH)

            if self.is_valid(r):
                if add_watchpost_format:
                    data = []
                    for item in r.json():
                        data.append({'id': item['id'],
                                     'eddy_namespace': item['beacon']['eddy_namespace'],
                                     'status': item['status'],
                                     'rssi_near': item['rssi_near'],
                                     'rssi_far': item['rssi_far']})
                    return data
                return r.json()

            raise Exception("data returned is not valid. {}".format(r.content))
        except Exception as e:
            print('server request get watchposts', e)
            return []

    def patch_watchpost(self, **kwargs):
        """ Envia uma atualização para o watchpost que mudou de status proc para A no rasp """
        try:
            id = kwargs.pop("id")

            print("\t\n\n... Enviando patch id {} para servidor: {}\n\n".format(id, kwargs))

            url = self.create_url('watchpost')

            r = requests.patch(url=url+'{}/'.format(id), headers=self.AUTH, data=kwargs)

            if r.status_code == 200:
                print("\t... Status enviado")
                return True
            print("warning: problema no status = {}".format(r.status_code))
            return False
        except Exception as e:
            print("patch watchpost", e)


class AlertServerRequest(BaseRequest):

    def post_alert(self, watchpost_id):
        """
        cria um novo alerta no sistema através do método post.
        :param: watchpost_id: id do monitoramento
        :return: True se deu certo ou None
        """
        try:
            print("sending warning for '%s' watchpost" % watchpost_id)
            data = {'watchpost_fk': watchpost_id}
            r = requests.post(self.IP_SERVER+'alert/', headers=self.AUTH, data=data)

            print(r.json())
            if r.status_code == 200:
                return True
            return None
        except Exception as e:
            print("POST ALERT ERROR:", e)
            return None
