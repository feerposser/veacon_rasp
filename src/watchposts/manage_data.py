from .watchpost_server_request import WatchpostServerRequest


class WatchpostManager:

    def __init__(self, set_watchpost=True):
        """
        Inicia buscando monitoramentos cadastrados no sistema e cria um dicionário que armazena as informações
        dos dados que o rasp está monitorando.
        :param set_watchpost:
        """
        self.watchposts = {}
        if set_watchpost:
            watchposts = WatchpostServerRequest().get_watchposts()
            for watchpost in watchposts:
                self.add_watchpost(watchpost)

    def add_watchpost(self, watchpost):
        """
        Adiciona um novo monitoramento no dicionário de monitoramentos
        :param watchpost: Estrutura vinda da API
        :return: None
        """
        try:
            assert 'rssi_max' in watchpost, "'rssi_max' not found"
            assert 'rssi_min' in watchpost, "'rssi_min' not found"
            assert 'beacon_namespace' in watchpost, "'beacon_namespace' not found"

            self.watchposts[watchpost['beacon']['eddy_namespace']] = {
                'rssi_max': watchpost['rssi_max'],
                'rssi_min': watchpost['rssi_min'],
                'id': watchpost['id']
            }

        except AssertionError as a:
            print(a)
        except Exception as e:
            print(e)
        finally:
            return

    def compare_beacon_rssi(self, eddy_namespace, median_rssi):
        """
        Compara a mediana do rssi escaneado com o max e min rssi. Verifica se não é maior que o máximo e menor que
        o mínimo
        :param eddy_namespace:
        :param median_rssi:
        :return:
        """
        if self.watchposts[eddy_namespace]['rssi_max'] > \
                median_rssi < self.watchposts[eddy_namespace]['rssi_min']:
            return True
        return False

    def validate_read_beacons(self, eddy_namespace_rrsi, set_warning=False):
        warning_list = []

        for beacon in eddy_namespace_rrsi:
            result = self.compare_beacon_rssi(beacon, eddy_namespace_rrsi[beacon])
            if not result:
                warning_list.append(self.watchposts[beacon]['id'])

        return warning_list
