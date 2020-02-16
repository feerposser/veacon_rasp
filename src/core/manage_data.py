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
            print("\t... Mensagem para {}. Status {}".format(message.eddy_namespace, message.status))

            if message.status == "P":
                if not self.exists(message.eddy_namespace):
                    self.beacon_manager.insert_allowed_beacon(message.eddy_namespace)
                    add = self.add_watchpost(message.__dict__)
                    if add is None:
                        print("Warning: Problema ao adicionar os dados da mensagem {}".format(message.eddy_namespace))
                        self.beacon_manager.remove_allowed_beacons(message.eddy_namespace)
                    else:
                        print('add:', add)

            elif message.status == "I":
                if self.exists(message.eddy_namespace):
                    print("setando remoção de {}".format(message.eddy_namespace))
                    self.beacon_manager.remove_allowed_beacons(message.eddy_namespace)
                    self.set_remove_watchpost_status(message.eddy_namespace)

    def execute(self):
        """ Executa as funções centralizadas de regra de negócio do projeto.
        1   - Verifica se o pub sub recebeu alguma mensagem de adição de monitoramento e executa o que for necessário
        2   - Verifica se existem monitoramentos ativos. Se existirem, inicia os processos do monitoramento """

        if self.messages_received:  # 1
            self.process_messages()

        if self.watchposts:  # 2
            print("\t... Iniciando processo de monitoramento")
            self.watchpost_manager_process()
