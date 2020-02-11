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

        for message in messages:
            if message.operation == "proc":
                # teste = self.proc_allowed_beacon(message.eddy_namespace)
                # print("near: %s\nfar: %s\n" % teste)
                pass
            elif message.operation == "rm":
                self.remove_allowed_beacons(message.eddy_namespace)
            elif message.operation == "add":
                pass
            else:
                pass

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

            for beacon in self.beacon_state:  # 3
                print("Analisando:", self.beacon_state[beacon])

                print(self.beacon_state[beacon].rssi_comparation())

                # warning_items = self.validate_read_beacon(self.beacon_state[beacon], send_warning=True)
                #
                # if warning_items:
                #     self.remove_watchpost(beacon)
                #     self.remove_allowed_beacons(beacon)
                #
                # print("Esperando 100s para o teste.\nLista de warnings:", warning_items)
                print("aguardando")
                time.sleep(100)
