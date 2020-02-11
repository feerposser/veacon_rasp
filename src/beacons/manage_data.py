import time
import statistics
from beacontools import BeaconScanner, EddystoneUIDFrame, EddystoneFilter

from beacons.beacons_server_request import BeaconServerRequest
from pubsub.pubsub import Message


class BeaconManager:

    def __init__(self, set_ble_read_time=15.0, set_allowed_beacons=False, allowed_beacons=None):
        """
        eddy_namespace_rssi = {'eddy_namespace': rssi,}
        scanned_beacons = list [('eddy_namespace', rssi)] beacons escaneados pelo read_ble. Ã‰ reiniciado a cada leitura
        allowed_beacons = ['eddy_namespace'] beacons que podem ser monitorados. Apenas os beacons cadastrados no sistema
        :param set_allowed_beacons: Bool. Inicializa os allowed beacons com os dados do sistema atravÃ©s da API.
        :param set_ble_read_time: Double. Seta o tempo que serÃ¡ usado para ler os bles em segundos
        Se for setado como False ou None o allowed_beacons serÃ¡ [] e nenhum beacon serÃ¡ lido.
        :param allowed_beacons: [] Se estiver preenchido irá setar a lista enviada à propriedade allowed beacons
        """
        self.eddy_namespace_rrsi = {}
        self.scanned_beacons = []

        self.ble_read_time = set_ble_read_time
        self.allowed_beacons = []

        if set_allowed_beacons:
            self.allowed_beacons = self.get_beacons_eddy_namespaces()

        if allowed_beacons:
            self.allowed_beacons = allowed_beacons
            print("allowed_beacons ->", self.allowed_beacons)

    @staticmethod
    def get_beacons_eddy_namespaces():
        """
        Faz uma busca na API do sistema para encontrar os beacons cadastrados.
        Retorna uma lista com os eddy_namespace dos beacons cadastrados
        ['eddy_namespace',]
        :return: ['eddy_namespace',] ou []
        """
        beacon_list = []
        allowed_beacons = BeaconServerRequest().get_allowed_beacons()
        if allowed_beacons:
            for beacon in allowed_beacons:
                beacon_list.append(beacon['eddy_namespace'])
            return beacon_list
        return []

    def proc_allowed_beacon(self, eddy_namespace):
        """
        Executa o procedimento de inserção de um novo beacon para um novo monitoramento do sistema
        vulnerabilidade: qualquer eddy_namespace que chegar via pubsub será adicionado.
        :param eddy_namespace:
        :return: None
        """

        rssis = []

        def read_a_ble(bt_addr, rssi, packet, additional_info):
            rssis.append(rssi)

        if eddy_namespace not in self.allowed_beacons:
            self.allowed_beacons.append(eddy_namespace)
            print("beacon '%s' autorizado" % eddy_namespace)

            scanner = BeaconScanner(callback=read_a_ble,
                                    device_filter=[eddy_namespace],
                                    packet_filter=[EddystoneUIDFrame])
            scanner.start()
            print("Coletando dados para '%s'" % eddy_namespace)
            time.sleep(self.ble_read_time)
            scanner.stop()
            near, far = max(rssis), min(rssis)
            return near, far

    def remove_allowed_beacons(self, eddy_namespace):
        """
        Remove um ou mais beacons já que essa é a única estrutura de monitoramento de beacons que não é reiniciada a
        cada processo do beacon_process
        :param eddy_namespace: str nome do beacon
        :return: Beacon removido ou None
        """
        try:
            self.allowed_beacons.remove(eddy_namespace)
            return eddy_namespace
        except ValueError as v:
            print(v)
            return None
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_median_list(rssi_list):
        """
        Retorna a mediana de uma lista
        :param rssi_list:
        :return:
        """
        return statistics.median(rssi_list)

    def create_eddy_namespace_rssi(self):
        """
        Itera sobre o o scanned_beacons para analisar quais beacons foram escaneados e quais sÃ£o os valores de rssis
        encontrados. Cria um dicionÃ¡rio com o nome do beacon escaneado e usa os rssis para criar a mediana que serÃ¡
        atribuida ao beacon no dicionÃ¡rio. {'eddy_namespace': rssi_median}
        :return:
        """
        try:
            self.eddy_namespace_rrsi.clear()
            for eddy_namespace, rssi in self.scanned_beacons:
                if eddy_namespace in self.eddy_namespace_rrsi:
                    self.eddy_namespace_rrsi[eddy_namespace].append(rssi)
                else:
                    self.eddy_namespace_rrsi[eddy_namespace] = [rssi]

            for key in self.eddy_namespace_rrsi.keys():
                self.eddy_namespace_rrsi[key] = self.get_median_list(self.eddy_namespace_rrsi[key])

            return
        except Exception as e:
            print(e)

    def read_callback(self, bt_addr, rssi, packet, additional_info):
        """
        Função executada quando o BeaconScanner do read_ble encontra um dispositivo emitindo um sinal.
        analisa se o beacon lido está na lista de beacons permitidos e adiciona à lista de leitura
        """
        if packet.namespace in self.allowed_beacons:
            self.scanned_beacons.append((packet.namespace, rssi))

    def read_ble(self, callback, beacon=None):
        """
        Lê os beacons por um determinado tempo
        Aqui a lib inicia uma thread. O scanner stop faz o join das threads.
        """

        scanner = BeaconScanner(
            callback,
            packet_filter=[EddystoneUIDFrame]
        )
        if beacon:
            scanner.device_filter = EddystoneFilter(namespace=beacon)

        scanner.start()
        print("reading ble for %s s" % self.ble_read_time)
        time.sleep(self.ble_read_time)
        scanner.stop()

    def beacon_process(self):
        assert self.allowed_beacons, "allowed_beacons must be initialize to run this function"

        self.scanned_beacons.clear()
        self.read_ble(self.read_callback, "edd1ebeac04e5defa017")
        self.create_eddy_namespace_rssi()

        print('final--->', self.eddy_namespace_rrsi)

