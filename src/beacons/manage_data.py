import time
import statistics
from beacontools import BeaconScanner, EddystoneUIDFrame, EddystoneFilter

from beacons.beacons_server_request import BeaconServerRequest
from pubsub.pubsub import Message


class Beacon:

    """
    state: responsável por identificar o estado atual do beacon.
    A: ativo. Está sendo monitorado
    I: inativo. O monitoramento deste beacon foi finalizado
    P: processamento: estão sendo recolhidos dados para identificar as distâncias do beacon para o gateway
    """

    def __init__(self, eddy_namespace, rssis_list, state=None):
        """
        :param eddy_namespace: str nome do beacon
        :param rssis_list: list ou tuple dos dados de rssi
        :param state: char estado do beacon
        """
        self.eddy_namespace = eddy_namespace
        self.median_rssi = statistics.median(rssis_list)
        self.near_rssi = max(rssis_list)
        self.far_rssi = min(rssis_list)
        self.state = state

    def __str__(self):
        return self.eddy_namespace + " state: " + self.state + " median: " + str(self.median_rssi)

    def rssi_comparation(self):
        """
        Compara a rssi mediana com o near e far rssi. Verifica se a mediana não é maior que o mais próximo nem menor
        que o mais distante.
        O rssi é medido através de números negativos. Quanto mais próximo a 0 mais perto se está do beacon.
        Se a mediana for maior (mais positivo) do que o rssi mais próximo encontrado no scaneamento, ou, ainda,
        mais distante (mais negativo) que a medida mais distante, então o beacon foi movido de local junto com o carro
        :return:
        """
        if self.state == "A":
            if self.near_rssi < self.median_rssi or self.median_rssi > self.far_rssi:
                return True
            return False
        raise Exception("state must be 'A' not '%s' for run this method" % self.state)

    def set_near_far_rssi(self, rssi_list):
        """
        atualiza o near e o far rssi do beacon
        :param rssi_list: list dados de rssi
        :return:
        """
        self.near_rssi = max(rssi_list)
        self.far_rssi = min(rssi_list)


class BeaconManager:

    def __init__(self, set_ble_read_time=15.0, set_allowed_beacons=False, allowed_beacons=None):
        """
        beacon_state = {'eddy_namespace': Beacon,}
        scanned_beacons = list [('eddy_namespace', rssi)] beacons escaneados pelo read_ble. Ã‰ reiniciado a cada leitura
        allowed_beacons = ['eddy_namespace'] beacons que podem ser monitorados. Apenas os beacons cadastrados no sistema
        :param set_allowed_beacons: Bool. Inicializa os allowed beacons com os dados do sistema atravÃ©s da API.
        :param set_ble_read_time: Double. Seta o tempo que serÃ¡ usado para ler os bles em segundos
        Se for setado como False ou None o allowed_beacons serÃ¡ [] e nenhum beacon serÃ¡ lido.
        :param allowed_beacons: [] Se estiver preenchido irá setar a lista enviada à propriedade allowed beacons
        """
        self.ble_read_time = set_ble_read_time
        self.beacon_state = {}
        self.scanned_beacons = []
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

    def insert_beacon(self, eddy_namespace):
        self.allowed_beacons.append(eddy_namespace)

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

    def create_beacon_state(self, eddy_namespace, rssis):
        """
        cria uma nova instancia de Beacon em beacon_state
        :param eddy_namespace: str nome do beacon
        :param rssis: list ou tuple com dados de rssi
        :return: Instancia do beacon cadastrado ou None
        """
        assert isinstance(rssis, list) or isinstance(rssis, tuple), "rssis must be a list or tuple instante"

        if eddy_namespace not in self.beacon_state:
            self.beacon_state[eddy_namespace] = Beacon(eddy_namespace, rssis)
            return self.beacon_state[eddy_namespace]

    def refresh_beacon_state(self, eddy_namespace, rssis):
        """
        Atualiza os dados de near e far da instancia do beacon em beacon_status
        :param eddy_namespace: str nome do beacon
        :param rssis: list ou tuple com dados de rssis coletados
        :return:
        """
        assert isinstance(rssis, list) or isinstance(rssis, tuple), "rssis must be a list or tuple instance"

        if eddy_namespace in self.beacon_state:
            self.beacon_state[eddy_namespace].set_near_far_rssi(rssis)

            return self.beacon_state[eddy_namespace]
        return None

    def do_beacon_state(self):
        """
        Itera sobre o o scanned_beacons para analisar quais beacons foram escaneados e quais sÃ£o os valores de rssis
        encontrados. Cria um dicionÃ¡rio com o nome do beacon escaneado e usa os rssis para criar a mediana que serÃ¡
        atribuida ao beacon no dicionÃ¡rio. {'eddy_namespace': Beacon}
        """
        try:
            for eddy_namespace, rssis in self.scanned_beacons:
                if eddy_namespace in self.beacon_state:
                    refresh = self.refresh_beacon_state(eddy_namespace, rssis)
                    if not refresh:
                        raise Exception("Erro ao atualizar o estado do beacon '%s'" % eddy_namespace)
                else:
                    create = self.create_beacon_state(eddy_namespace, rssis)
                    if not create:
                        raise Exception("Erro ao criar estado do beacon '%s'" % eddy_namespace)
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
        """Lê os beacons por um determinado tempo Aqui a lib inicia uma thread.
        O scanner stop faz o join das threads """

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
        self.do_beacon_state()

        print('final--->', self.beacon_state)

