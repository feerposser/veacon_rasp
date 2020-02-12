from beacons.manage_data import BeaconManager
from watchposts.manage_data import WatchpostManager
from pubsub.pubsub import PubSubManager

import time


class Core(WatchpostManager, PubSubManager):

    def __init__(self):
        WatchpostManager.__init__(self)
        print('watchposts ->', self.watchposts)
        PubSubManager.__init__(self)

    def process_messages(self):
        messages = self.messages_received.copy()
        self.messages_received.clear()
        print('pub sub messages --->', messages)

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
            self.process_messages()
            pass

        if self.watchposts:  # 2
            self.watchpost_manager_process()
            print("aguardando")
            time.sleep(100)
