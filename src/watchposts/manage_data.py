import statistics

from core.exceptions import WatchpostException, RefreshMedianWatchpostException
from .watchpost_server_request import WatchpostServerRequest
from beacons.manage_data import BeaconManager


class Watchpost:

    def __init__(self, id, eddy_namespace, status, near=None, far=None):

        self.id = id
        self.eddy_namespace = eddy_namespace
        self.status = status
        self.rssi_median = None
        self._rssi_near = None
        self._rssi_far = None

        if near and far:
            self._rssi_near, self._rssi_far = near, far

    def __str__(self):
        return " ".join([str(self.id), self.eddy_namespace, self.status])

    def refresh_mediam_rssi(self, rssis_list):
        """
        atualiza o near e o far rssi do beacon
        :param rssis_list: list dados de rssi
        :return: mediana ou None
        """
        try:
            assert isinstance(rssis_list, list) or isinstance(rssis_list, tuple), \
                "rssis_list must be tuple or list instance. '%s' instead" % type(rssis_list)

            self.rssi_median = statistics.median(rssis_list)
            return self.rssi_median
        except RefreshMedianWatchpostException as r:
            print(r)
            return None

    def set_near_far_rssi(self, rssis_list):
        """
        Seta um valor para os rssis near e far. Estes valores não poderão ser alterados depois de serem setados.
        :param rssis_list: list inteiros negativos com rssis coletados
        :return: tuple (near, far) setados ou None
        """
        if self._rssi_near is None and self._rssi_far is None:
            self._rssi_near, self._rssi_far = max(rssis_list), min(rssis_list)
            return self._rssi_near, self._rssi_far
        return None

    def rssi_comparation(self):
        """
        Compara a rssi mediana com o near e far rssi. Verifica se a mediana não é maior que o mais próximo nem menor
        que o mais distante.
        O rssi é medido através de números negativos. Quanto mais próximo a 0 mais perto se está do beacon.
        Se a mediana for maior (mais positivo) do que o rssi mais próximo encontrado no scaneamento, ou, ainda,
        mais distante (mais negativo) que a medida mais distante, então o beacon foi movido de local junto com o carro
        :return: True ou False
        """
        if self.status == "A":
            if self._rssi_near < self.rssi_median or self.rssi_median > self._rssi_far:
                return True
            return False
        raise WatchpostException("state must be 'A' not '%s' for run this method" % self.status)


class WatchpostManager:

    def __init__(self):
        """
        Inicia buscando monitoramentos cadastrados no sistema e cria um dicionário que armazena as informações
        dos dados que o rasp está monitorando
        """
        self.watchposts = {}
        watchposts = WatchpostServerRequest().get_watchposts()
        for watchpost in watchposts:
            self.add_watchpost(watchpost)

        self.beacon_manager = BeaconManager(allowed_beacons=self.watchposts.keys())

    def add_watchpost(self, watchpost):
        """
        Adiciona um novo monitoramento no dicionário de monitoramentos
        :param watchpost: Estrutura vinda da API
        :return: Objeto Watchpost adicionado ou None
        """
        try:
            assert 'id' in watchpost, "'id' not found"
            assert 'status' in watchpost, "'status' not found"
            assert 'beacon' in watchpost and 'eddy_namespace' in watchpost['beacon'], \
                "'beacon' data or beacon.eddy_namespace data not found"

            id = watchpost['id']
            status = watchpost['status']
            eddy_namespace = watchpost['beacon']['eddy_namespace']

            assert eddy_namespace not in self.watchposts, "'%s' already in watchposts list" % eddy_namespace

            if 'rssi_near' in watchpost and 'rssi_far' in watchpost:
                rssi_near, rssi_far = watchpost['rssi_near'], watchpost['rssi_far']
                self.watchposts[eddy_namespace] = Watchpost(id, eddy_namespace, status, near=rssi_near, far=rssi_far)
            else:
                self.watchposts[eddy_namespace] = Watchpost(id, eddy_namespace, status)
            return self.watchposts[eddy_namespace]

        except AssertionError as a:
            print('add watchpost', a)
            return None
        except Exception as e:
            print(e)
            return None

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

    def refresh_watchpost(self, eddy_namespace, rssis_list):
        """
        atualiza os dados do watchpost (mediana do rssi)
        :param eddy_namespace: nome do beacon rastreado
        :param rssis_list: lista de rssis coletados
        :return: objeto Watchpost atualizado ou None
        """
        try:
            assert eddy_namespace in self.watchposts, "'%s' not in watchposts"

            print("...atualizando watchpost", eddy_namespace)

            watchpost = self.watchposts[eddy_namespace]
            watchpost.refresh_mediam_rssi(rssis_list)
            return watchpost

        except AssertionError as a:
            print("refresh watchpost", a)
            return None

    def process_refresh_watchpost(self, rssis_list):
        """
        Itera sobre um dicionário {'edy_namespace': [rssis,]} e envia os dados de rssi para serem atualizados no objeto
        watchpost.
        :param rssis_list: dict {'edy_namespace': [rssis,]}
        :return: None ou Exception
        """
        try:
            for key in rssis_list:
                if key in self.watchposts:
                    refresh = self.refresh_watchpost(key, rssis_list[key])
                    if refresh:
                        print("\tatualizado\n\t", refresh.__dict__)
                else:
                    raise Exception("'%s' not in watchposts" % key)
        except Exception as e:
            print('process refresh watchpost', e)

    def validate_read_beacon(self, eddy_namespace, send_warning=False):
        """
        Valida uma lista de beacons escaneados com mediana.
        :param eddy_namespace: str nome do beacon
        :param send_warning: bool se true envia um alerta para o VeaconSys através de API
        :return: int com id do watchpost ou None
        """
        try:
            assert eddy_namespace in self.watchposts, "'%s' not in watchposts" % eddy_namespace

            warning_item = None
            watchpost = self.watchposts[eddy_namespace]

            if watchpost.rssi_comparation():
                warning_item = watchpost.id

                if send_warning:
                    WatchpostServerRequest().post_alert(warning_item)

            return warning_item
        except AssertionError as a:
            print("validate read beacon", a)
            return None

        except Exception as e:
            print(e)
            return None

    def process_validate_read_beacon(self):
        for key in self.watchposts.keys():  # .items?
            validate = self.validate_read_beacon(key)
            if validate:
                # todo: o que fazer se foi enviado alerta? E se não for?
                pass

    def watchpost_manager_process(self):
        """
        Centraliza o processo de regra de negócio
        :return:
        """
        rssis_list = self.beacon_manager.beacon_process()

        print('---->\n', rssis_list)

        self.process_refresh_watchpost(rssis_list)

        self.process_validate_read_beacon()
