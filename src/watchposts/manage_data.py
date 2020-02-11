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

    def remove_watchpost(self, eddy_namespace):
        """
        remove um item do dicionario de monitoramento
        :param eddy_namespace: nome do beacon que está sendo monitorado
        :return: valor do item monitorado ou None
        """
        try:
            assert eddy_namespace in self.watchposts, "'eddy_namespace' not in watchposts"

            removed = self.watchposts.pop(eddy_namespace)
            return removed
        except AssertionError as a:
            print(a)
            return None
        except Exception as e:
            print(e)
            return None

    def validate_read_beacon(self, beacon, send_warning=False):
        """
        Valida uma lista de beacons escaneados com mediana.
        :param beacon: Beacon objeto Beacon
        :param send_warning: bool se true envia um alerta para o VeaconSys através de API
        :return: retorna uma lista com os ids dos beacons em estado de alerta
        """
        try:
            warning_item = None
            if beacon.rssi_comparation():
                warning_item = self.watchposts[beacon.eddy_namespace]['id']
            else:
                return None

            if send_warning:
                print('entrou no if')
                for warning in warning_item:
                    print('enviando', warning)
                    WatchpostServerRequest().post_alert(warning)

            return warning_item
        except Exception as e:
            print(e)
            return None
