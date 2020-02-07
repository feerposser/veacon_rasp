from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from settings import PUBNUB_PUBLISH_KEY as PUBLISH_KEY, PUBNUB_SUBSCRIBE_KEY as SUBSCRIBE_KEY, BEACON_GATEWAY_ID

pnconfig = PNConfiguration()

pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.publish_key = PUBLISH_KEY
pnconfig.uuid = "gateway_01"

pubnub = PubNub(pnconfig)


class PubSubManager(SubscribeCallback):

    messages_received = []

    class Message:

        def __init__(self, message):
            self.sender = None
            self.content = None
            self.gateway_id = None

            assert "eddy_namespace" in message, "'eddy_namespace' not in message"
            assert "operation" in message, "'operation' not in message"
            assert message["operation"] == "add" or message["operation"] == "rm", "'add' or 'rm' not in message"

            if "sender" in message:
                self.sender = message["sender"]
            if "content" in message:
                self.content = message["content"]
            if "gateway_id" in message:
                self.gateway_id = message["gateway_id"]
            self.eddy_namespace = message["eddy_namespace"]
            self.operation = message["operation"]

        def __str__(self):
            return self.eddy_namespace + ": " + self.operation

    def presence(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        pass

    def message(self, pubnub, message):
        """
        Funcão executada quando uma mensagem é recebida no canal. Formato da mensagem padrão:
        {
            "eddy_namespace": int,
            "content": str,
            "operation": "add" ou "rm", / adicionar ou remover
            "gateway_id": int
        }
        """
        try:
            message = message.message
            self.messages_received.append(self.Message(message))
        except AssertionError as a:
            print(a)
        except Exception as e:
            print(e)


pubnub.add_listener(PubSubManager())
pubnub.subscribe().channels('veacon_channel_gateway_%s' % BEACON_GATEWAY_ID).execute()
