import time
from beacontools import BeaconScanner, EddystoneUIDFrame


class BeaconManager:

    def __init__(self, set_ble_read_time=15.0, allowed_beacons=None):
        """
        beacon_state = {'eddy_namespace': Beacon,}
        scanned_beacons = list [('eddy_namespace', rssi)] beacons escaneados pelo read_ble. Ã‰ reiniciado a cada leitura
        allowed_beacons = ['eddy_namespace'] beacons que podem ser monitorados. Apenas os beacons cadastrados no sistema
        :param set_ble_read_time: Double. Seta o tempo que serÃ¡ usado para ler os bles em segundos
        Se for setado como False ou None o allowed_beacons serÃ¡ [] e nenhum beacon serÃ¡ lido.
        :param allowed_beacons: [] Se estiver preenchido irá setar a lista enviada à propriedade allowed beacons
        """
        print("\t... Iniciando Beacon Manager")
        self.ble_read_time = set_ble_read_time
        self.beacon_rssis = {}
        self.scanned_beacons = []
        self.allowed_beacons = []

        if allowed_beacons:
            self.allowed_beacons = allowed_beacons
            print("allowed_beacons ->", self.allowed_beacons)

    def insert_allowed_beacon(self, eddy_namespace):
        """
        Adiciona um novo beacon à lista de beacons permitidos
        :param eddy_namespace: uuid do beacon
        :return:
        """
        if eddy_namespace not in self.allowed_beacons:
            self.allowed_beacons.append(eddy_namespace)
        return self.allowed_beacons

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

    def create_beacon_rssis(self):
        """
        Itera sobre o o scanned_beacons para analisar quais beacons foram escaneados e quais sÃ£o os valores de rssis
        encontrados. Cria um dicionário onde a chave é o nome do beacon escaneado e o valor é uma lista com os rssis
        encontrados no escaneamento
        :return dict {'eddy_namespace': [rssi,],} or None
        """
        beacon_rssis = {}

        try:
            assert self.scanned_beacons, "scanned_beacons must be set for this operation"

            for eddy_namespace, rssi in self.scanned_beacons:
                if eddy_namespace in beacon_rssis:
                    beacon_rssis[eddy_namespace].append(rssi)
                else:
                    beacon_rssis[eddy_namespace] = [rssi]

            return beacon_rssis
        except Exception as e:
            print(e)
            return None

    def read_callback(self, bt_addr, rssi, packet, additional_info):
        """
        Função executada quando o BeaconScanner do read_ble encontra um dispositivo emitindo um sinal.
        analisa se o beacon lido está na lista de beacons permitidos e adiciona à lista de leitura
        """
        if packet.namespace in self.allowed_beacons:
            self.scanned_beacons.append((packet.namespace, rssi))

    def read_ble(self):
        """Lê os beacons por um determinado tempo. A lib inicia uma thread. O scanner stop faz o join das threads """

        scanner = BeaconScanner(
            self.read_callback,
            packet_filter=[EddystoneUIDFrame]
        )

        scanner.start()
        print("reading ble for %s s" % self.ble_read_time)
        time.sleep(self.ble_read_time)
        scanner.stop()

    def beacon_process(self):
        assert self.allowed_beacons, "allowed_beacons must be initialize to run this function"

        self.scanned_beacons.clear()
        self.read_ble()
        return self.create_beacon_rssis()
