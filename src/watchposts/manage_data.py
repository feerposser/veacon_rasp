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
            assert 'rssi_near' in watchpost, "'rssi_near' not found"
            assert 'rssi_far' in watchpost, "'rssi_far' not found"
            assert 'beacon' in watchpost, "'beacon' not found"
            assert 'eddy_namespace' in watchpost['beacon'], "'beacon.eddy_namespace' not found"

            self.watchposts[watchpost['beacon']['eddy_namespace']] = {
                'rssi_near': watchpost['rssi_near'],
                'rssi_far': watchpost['rssi_far'],
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
        o mínimo.
        O rssi é medido através de números negativos. Quanto mais próximo a 0 mais perto se está do beacon.
        :param eddy_namespace:  str nome do beacon
        :param median_rssi: float negativo mediana
        :return: True se estiver fora do range rssi near e far, senão falso
        """
        if self.watchposts[eddy_namespace]['rssi_near'] < median_rssi > self.watchposts[eddy_namespace]['rssi_far']:
            return True
        return False

    def validate_read_beacons(self, eddy_namespace_rrsi, set_warning=False):
        """
        Valida uma lista de beacons escaneados com mediana.
        :param eddy_namespace_rrsi_list: {"beacon_name": rssi_median,}
        :param set_warning: se true envia um alerta para o VeaconSys através de API
        :return: retorna uma lista com os ids dos beacons em estado de alerta
        """
        warning_list = []

        for beacon in eddy_namespace_rrsi.keys():
            result = self.compare_beacon_rssi(beacon, eddy_namespace_rrsi[beacon])
            if result:
                warning_list.append(self.watchposts[beacon]['id'])

        if set_warning:
            for warning in warning_list:
                WatchpostServerRequest().post_alert(warning)

        return warning_list
