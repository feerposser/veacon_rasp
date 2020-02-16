import statistics

from core.exceptions import WatchpostException, RefreshMedianWatchpostException, WatchpostAlreadyExistsException, \
    AddWatchpostException
from .watchpost_server_request import WatchpostServerRequest, AlertServerRequest
from beacons.manage_data import BeaconManager
from settings import BEACON_GATEWAY_ID

WATCHPOST_STATUS_ALLOWED = ("P", "A", "I")


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

    def change_status(self, status):
        try:
            assert status in WATCHPOST_STATUS_ALLOWED, \
                "Warning: status must be 'P' or 'A' or 'I'. {} instead".format(status)

            self.status = status
        except Exception as e:
            print(e)
            return None

    def get_rssi_near(self):
        return self._rssi_near

    def get_rssi_far(self):
        return self._rssi_far

    def rssi_comparation(self):
        """
        Compara a rssi mediana com o near e far rssi. Verifica se a mediana não é menor que o mais próximo nem menor
        que o mais distante.
        O rssi é medido através de números negativos. Quanto mais próximo a 0 mais perto se está do beacon.
        Se a mediana for maior (mais positivo) do que o rssi mais próximo encontrado no scaneamento, ou, ainda,
        mais distante (mais negativo) que a medida mais distante, então o beacon foi movido de local junto com o carro
        :return: True ou False
        """
        if self.status == "A":
            if self._rssi_near > self.rssi_median > self._rssi_far:
                return True
            return False
        raise WatchpostException("state must be 'A' not '%s' for run this method" % self.status)


class WatchpostManager:

    def __init__(self):
        """ Inicia buscando monitoramentos cadastrados no sistema e cria um dicionário que armazena as informações
        dos dados que o rasp está monitorando """
        print("\t... Iniciando Watchpost Manager")
        self.watchposts = {}
        watchposts = WatchpostServerRequest().get_watchposts(add_watchpost_format=True,
                                                             gateway_id=BEACON_GATEWAY_ID,
                                                             status="A")
        for watchpost in watchposts:
            self.add_watchpost(watchpost)

        self.beacon_manager = BeaconManager(allowed_beacons=[*self.watchposts.keys()])  # * para descompactar em lista

    def exists(self, eddy_namespace):
        if eddy_namespace in self.watchposts.keys():
            return True
        return False

    def add_watchpost(self, watchpost):
        """
        Adiciona um novo monitoramento no dicionário de monitoramentos
        :param watchpost: dict
        :return: Watchpost ou None
        """
        try:
            assert 'id' in watchpost, "'id' not found"
            assert 'status' in watchpost, "'status' not found"
            assert watchpost['status'] in WATCHPOST_STATUS_ALLOWED, \
                "'status must be {}. {} instead".format(WATCHPOST_STATUS_ALLOWED, watchpost['status'])
            assert 'eddy_namespace' in watchpost, "eddy_namespace not fount in watchpost"

            id = watchpost['id']
            status = watchpost['status']
            eddy_namespace = watchpost['eddy_namespace']

            if not self.exists(eddy_namespace):
                raise WatchpostAlreadyExistsException("'%s' already in watchposts list" % eddy_namespace)

            if 'rssi_near' in watchpost and 'rssi_far' in watchpost:
                rssi_near, rssi_far = watchpost['rssi_near'], watchpost['rssi_far']
                self.watchposts[eddy_namespace] = Watchpost(id, eddy_namespace, status, near=rssi_near, far=rssi_far)
            else:
                self.watchposts[eddy_namespace] = Watchpost(id, eddy_namespace, status)

            print("Monitoramento adicionado:", self.watchposts[eddy_namespace])
            return self.watchposts[eddy_namespace]

        except WatchpostAlreadyExistsException as w:
            print('add watchpost', w)
            raise AddWatchpostException(w.__str__())
        except AssertionError as a:
            print('add watchpost', a)
            raise AddWatchpostException(a.__str__())
        except Exception as e:
            print('add watchpost', e)
            raise AddWatchpostException(e.__str__())

    def remove_watchpost(self, eddy_namespace):
        """
        remove um item do dicionario de monitoramento
        :param eddy_namespace: nome do beacon que está sendo monitorado
        :return: valor do item monitorado ou None
        """
        try:
            assert self.exists(eddy_namespace), "'eddy_namespace' not in watchposts"

            removed = self.watchposts.pop(eddy_namespace)
            return removed
        except AssertionError as a:
            print(a)
            return None
        except Exception as e:
            print(e)
            return None

    def set_remove_watchpost_status(self, eddy_namespace):
        """
        Seta o status do objeto Watchpost referente ao beacon (eddy_namespace) como 'I' para ser removido no
        proximo refresh watchpost
        :param eddy_namespace: str
        :return: obj Watchpost removido ou None
        """
        try:
            assert eddy_namespace in self.watchposts, "{} not in watchposts".format(eddy_namespace)

            watchpost = self.watchposts[eddy_namespace]
            watchpost.change_status("I")
            return watchpost
        except AssertionError as a:
            print("set remove status", a)
            return None
        except Exception as e:
            print("set remove status", e)
            return None

    def refresh_watchpost(self, eddy_namespace, rssis_list):
        """
        Atualiza o objeto Watchpost através de seu status.
        A: Ativo. Atualiza a mediana com o rssis list
        P: Processando. Foi adicionado recentemente e ainda nao foi completamente setado calibrado.
        Ira buscar os dados de rssis para setar o near, far e mediam. Depois envia um patch ao Sys
        I: Invativo. Significa que
        :param eddy_namespace: nome do beacon rastreado
        :param rssis_list: lista de rssis coletados
        :return: objeto Watchpost atualizado ou None
        """
        try:
            assert self.exists(eddy_namespace), "'{}' not in watchposts".format(eddy_namespace)

            print("...atualizando watchpost", eddy_namespace)

            watchpost = self.watchposts[eddy_namespace]

            if watchpost.status == "A":
                watchpost.refresh_mediam_rssi(rssis_list)
            elif watchpost.status == "P":
                watchpost.set_near_far_rssi(rssis_list)
                watchpost.refresh_mediam_rssi(rssis_list)
                watchpost.status = "A"
                WatchpostServerRequest().patch_watchpost(id=watchpost.id,
                                                         rssi_near=watchpost.get_rssi_near(),
                                                         rssi_far=watchpost.get_rssi_far(),
                                                         status=watchpost.status)
            elif watchpost.status == "I":
                removed = self.remove_watchpost(watchpost.eddy_namespace)
                if removed:
                    WatchpostServerRequest().patch_watchpost(id=removed.id, status=removed.status)

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
                if self.exists(key):
                    refresh = self.refresh_watchpost(key, rssis_list[key])
                    if refresh:
                        print("\tatualizado\n\t{}\n\tstatus {}".format(refresh.eddy_namespace, refresh.status))
                else:
                    raise Exception("Warning: '%s' not in watchposts" % key)
        except Exception as e:
            print('process refresh watchpost', e)

    def validate_read_beacon(self, eddy_namespace, send_warning=False):
        """
        Processo de validação de um monitoramento (rssi_comparation)
        :param eddy_namespace: str nome do beacon
        :param send_warning: bool se true envia um alerta para o VeaconSys através de API
        :return: int com id do watchpost ou None
        """
        try:
            assert self.exists(eddy_namespace), "'{}' not in watchposts".format(eddy_namespace)

            warning_item = None
            watchpost = self.watchposts[eddy_namespace]

            if not watchpost.rssi_comparation():
                print("\t...Alerta de monitoramento para '%s'" % watchpost.eddy_namespace)
                warning_item = watchpost.id

                if send_warning:
                    AlertServerRequest().post_alert(warning_item)
            else:
                print("\t...Sem alerta de monitoramento para '%s'" % watchpost.eddy_namespace)
            return warning_item
        except AssertionError as a:
            print("validate read beacon", a)
            return None

        except Exception as e:
            print("validate read beacon", e)
            return None

    def process_validate_read_beacon(self):
        """ Itera sobre o dicionário de objetos Watchpost e aciona o método que processa a validação do objeto """
        for key in self.watchposts.keys():  # .items?
            validate = self.validate_read_beacon(key, send_warning=True)
            if validate:
                # todo: o que fazer se foi enviado alerta? E se não for?
                pass

    def watchpost_manager_process(self):
        """ Centraliza o processo de regra de negócio"""

        if self.watchposts and self.beacon_manager.allowed_beacons:
            rssis_list = self.beacon_manager.beacon_process()

            print('---->\n', rssis_list)

            self.process_refresh_watchpost(rssis_list)

            self.process_validate_read_beacon()
        else:
            print("\t... Nenhum monitoramento para analisar")
