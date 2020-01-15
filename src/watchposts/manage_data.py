from .watchpost_server_request import WatchpostServerRequest


class WatchpostManager:

    def __init__(self, set_watchpost=True):
        self.watchposts = {}
        if set_watchpost:
            watchposts = WatchpostServerRequest().get_watchposts()
            for watchposts in watchposts:
                self.add_watchpost(watchposts)

    def compare_beacon_rssi(self, eddy_namespace, current_rssi):
        """
        Compara o rssi de monitoramento de um beacon com um rssi atual
        :param eddy_namespace:
        :param current_rssi:
        :return:
        """
        if eddy_namespace in self.watchposts:
            if self.watchposts[eddy_namespace]['rssi'] > current_rssi or \
                    self.watchposts[eddy_namespace]['rssi'] < current_rssi:
                print(eddy_namespace, current_rssi)

    def add_watchpost(self, watchpost):
        """
        Adiciona um novo monitoramento no dicionário de monitoramentos
        :param watchpost: Estrutura vinda da API
        :return: None
        """
        try:
            assert 'id' in watchpost, "'id' não encontrado"
            assert 'rssi' in watchpost, "'rssi' não encontrado"
            assert 'beacon' in watchpost, "'beacon' não encontrado"
            assert watchpost['beacon']['eddy_namespace'] not in self.watchposts, 'Beacon %s já monitorado' % \
                                                                                 watchpost['beacon']['eddy_namespace']

            self.watchposts[watchpost['beacon']['eddy_namespace']] = {
                'rssi': watchpost['rssi'],
                'id': watchpost['id']
            }

        except AssertionError as a:
            print(a)
            return
        except Exception as e:
            print(e)
            return

    def get_all_listening_watchposts_beacons(self):
        return self.watchposts.keys()

    def get_listening_watchpost(self, eddy_namespace):
        """
        Recupera dados do dicionário de monitoramento através no eddy_namespace do beacon monitorado
        :param eddy_namespace: nome do beacon
        :return:
        """

        try:
            if eddy_namespace in self.watchposts:
                return self.watchposts[eddy_namespace]
            raise Exception("%s não encontrado no dicionário de monitoramento" % eddy_namespace)
        except Exception as e:
            print(e)
            return None
