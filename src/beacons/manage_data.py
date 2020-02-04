import time
import statistics
from beacontools import BeaconScanner, EddystoneUIDFrame

from beacons.beacons_server_request import BeaconServerRequest


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
                self.eddy_namespace_rrsi[key] = statistics.median(self.eddy_namespace_rrsi[key])

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

    def read_ble(self):
        """
        Lê os beacons por um determinado tempo
        Aqui a lib inicia uma thread. O scanner stop faz o join das threads.
        :return:
        """
        self.scanned_beacons.clear()
        scanner = BeaconScanner(self.read_callback, packet_filter=[EddystoneUIDFrame])
        scanner.start()
        print("reading ble for %s s" % self.ble_read_time)
        time.sleep(self.ble_read_time)
        scanner.stop()

    def beacon_process(self):
        assert self.allowed_beacons, "allowed_beacons must be initialize for run this function"

        self.read_ble()
        self.create_eddy_namespace_rssi()

        print('final--->', self.eddy_namespace_rrsi)

