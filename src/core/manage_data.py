from watchposts.manage_data import WatchpostManager
from pubsub.pubsub import PubSubManager

import time


class Core(WatchpostManager, PubSubManager):

    def __init__(self):
        print("\t... Iniciando o Core da aplicação")
        WatchpostManager.__init__(self)
        print('watchposts ->', self.watchposts)
        PubSubManager.__init__(self)

    def process_messages(self):
        print('\t... Iniciando processamento de mensagem recebida')
        messages = self.messages_received.copy()
        self.messages_received.clear()

        for message in messages:
            print("\t... Processando mensagem {}".format(message))
            if message.operation == "add":
                if not self.exists(message.eddy_namespace):
                    add = self.add_watchpost(message)
                    if not add:
                        print("Warning: Problema ao adicionar os dados da mensagem {}".format(message.eddy_namespace))
            elif message.operation == "rm":
                self.beacon_manager.remove_allowed_beacons(message.eddy_namespace)
                self.set_remove_watchpost_status(message.eddy_namespace)

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
            print("\t... Iniciando processo de monitoramento")
            self.watchpost_manager_process()
