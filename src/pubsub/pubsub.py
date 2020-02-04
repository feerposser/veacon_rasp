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

    message_received = []

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
        :param pubnub:
        :param message:
        :return:
        """
        try:
            assert "operation" in message.message, "'operation' not in message"
            assert "add" or "rm" in message.message["operation"], "'add' or 'rm' not in message"
            assert "beacon_id" in message.message, "'beacon_id' not in message"

            self.message_received.append(message.message)
        except Exception as e:
            print(e)


pubnub.add_listener(PubSubManager())
pubnub.subscribe().channels('veacon_channel_gateway_%s' % BEACON_GATEWAY_ID).execute()
