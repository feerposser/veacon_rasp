from beacons.manage_data import BeaconManager
from watchposts.manage_data import WatchpostManager
from pubsub.pubsub import PubSubManager

import time


class Core(BeaconManager, WatchpostManager, PubSubManager):

    def __init__(self):
        WatchpostManager.__init__(self)
        print('watchposts ->', self.watchposts)
        BeaconManager.__init__(self, allowed_beacons=self.watchposts.keys())
        PubSubManager.__init__(self)

    def process_messages(self):
        messages = self.messages_received.copy()
        self.messages_received.clear()
        print('pub sub messages --->', messages)
        self.add_allowed_beacon(messages)

    def execute(self):
        """
        Executa as funções centralizadas de regra de negócio do projeto.
        1   - Verifica se o pub sub recebeu alguma mensagem de adição de monitoramento e executa o que for necessário
        2   - Verifica se existem monitoramentos ativos. Se existirem, inicia a leitura dos beacons
        2.1 - Para cada beacon lido existe um valor de mediana de seu rssi. É executado o processo para identificar
        possíveis mudanças de estado do local do beacon.
        :return: None
        """
        if self.messages_received:  # 1
            # todo: beacon add + usar o add watchpost
            self.process_messages()
            pass

        if self.watchposts:  # 2
            self.beacon_process()

            for beacon in self.eddy_namespace_rrsi:  # 3
                print("Enviando rssi '%s'" % beacon, self.eddy_namespace_rrsi[beacon])
                warning_item = self.validate_read_beacons(beacon, self.eddy_namespace_rrsi[beacon], send_warning=True)

                if warning_item:
                    self.remove_watchpost(beacon)
                    self.remove_allowed_beacons(beacon)

                print("Esperando 100s para o teste.\nLista de warnings:", warning_item)
                time.sleep(100)
