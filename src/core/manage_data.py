from watchposts.manage_data import WatchpostManager
from pubsub.pubsub import PubSubManager

from .exceptions import WatchpostAlreadyExistsException, StatusNotAcceptable, BeaconAlreadyInAllowedBeaconsException, \
    AddWatchpostException


class Core(WatchpostManager, PubSubManager):

    def __init__(self):
        print("\t... Iniciando o Core da aplicação")
        WatchpostManager.__init__(self)
        print('watchposts ->', self.watchposts)
        PubSubManager.__init__(self)

    def process_messages(self):
        try:
            print('\t... Iniciando processamento de mensagem recebida')
            messages = self.messages_received.copy()
            self.messages_received.clear()

            for message in messages:
                print("\t... Mensagem de {}. Status {}".format(message.eddy_namespace, message.status))

                if message.status == "P":
                    if not self.exists(message.eddy_namespace):
                        self.beacon_manager.insert_allowed_beacon(message.eddy_namespace)
                        add = self.add_watchpost(message.__dict__)
                        print('add:', add)
                    else:
                        raise WatchpostAlreadyExistsException(
                            "{} já está sendo monitorado".format(message.eddy_namespace))
                elif message.status == "I":
                    if self.exists(message.eddy_namespace):
                        print("setando remoção de {}".format(message.eddy_namespace))
                        self.beacon_manager.remove_allowed_beacons(message.eddy_namespace)
                        self.set_remove_watchpost_status(message.eddy_namespace)
                else:
                    raise StatusNotAcceptable("status must be 'I' or 'P'. {} instead.".format(message.status))

        except AddWatchpostException as a:
            print('process messages', a)
        except WatchpostAlreadyExistsException as w:
            print('process messages', w)
        except StatusNotAcceptable as s:
            print('process messages', s)
        except BeaconAlreadyInAllowedBeaconsException as b:
            print('process messages', b)

    def execute(self):
        """ Executa as funções centralizadas de regra de negócio do projeto.
        1   - Verifica se o pub sub recebeu alguma mensagem de adição de monitoramento e executa o que for necessário
        2   - Verifica se existem monitoramentos ativos. Se existirem, inicia os processos do monitoramento """

        if self.messages_received:  # 1
            self.process_messages()

        if self.watchposts:  # 2
            print("\t... Iniciando processo de monitoramento")
            self.watchpost_manager_process()
