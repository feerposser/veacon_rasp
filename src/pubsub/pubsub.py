from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from settings import PUBNUB_PUBLISH_KEY as PUBLISH_KEY, PUBNUB_SUBSCRIBE_KEY as SUBSCRIBE_KEY, BEACON_GATEWAY_ID
from core.exceptions import MessageReceivedException

pnconfig = PNConfiguration()

pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.publish_key = PUBLISH_KEY
pnconfig.uuid = "gateway_01"

pubnub = PubNub(pnconfig)


class Message:

    def __init__(self, message):

        if self.is_valid(message):
            self.id = message["id"]
            self.eddy_namespace = message["eddy_namespace"]
            self.operation = message["operation"]

            self.sender = None
            self.content = None
            self.gateway_id = None

            if "sender" in message:
                self.sender = message["sender"]
            if "content" in message:
                self.content = message["content"]
            if "gateway_id" in message:
                self.gateway_id = message["gateway_id"]

            print(self.__str__())
        print("Errrrooooo")
        raise MessageReceivedException("Mensagem inválida")

    @staticmethod
    def is_valid(message):
        try:
            assert "id" in message, "'id' not in message"
            assert "eddy_namespace" in message, "'eddy_namespace' not in message"
            assert "operation" in message, "'operation' not in message"
            assert message["operation"] == "add" or \
                   message["operation"] == "rm" or \
                   message["operation"] == "proc", \
                "'add' 'rm' or 'proc' not in message. {} instead".format(message["operation"])

            return True
        except AssertionError as a:
            print('Warning: Message is not valid.', a)
            return False
        except Exception as e:
            print("Warning:", e)

    def __str__(self):
        return self.eddy_namespace + ": " + self.operation


class PubSubManager(SubscribeCallback):

    messages_received = []

    def presence(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        pass

    def message(self, pubnub, message):
        """ Funcão executada quando uma mensagem é recebida no canal """

        try:
            message = message.message
            self.messages_received.append(Message(message))
            print("mensagem recebida!")
            import time
            time.sleep(10)
        except MessageReceivedException as m:
            print(m)
        except AssertionError as a:
            print(a)
        except Exception as e:
            print(e)


pubnub.add_listener(PubSubManager())
pubnub.subscribe().channels('veacon_channel_gateway_%s' % BEACON_GATEWAY_ID).execute()
