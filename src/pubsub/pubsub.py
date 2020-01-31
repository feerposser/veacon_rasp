from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from settings import PUBNUB_PUBLISH_KEY as PUBLISH_KEY, PUBNUB_SUBSCRIBE_KEY as SUBSCRIBE_KEY, BEACON_GATEWAY_ID

pnconfig = PNConfiguration()

pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.publish_key = PUBLISH_KEY
pnconfig.uuid = "gateway_01"

pubnub = PubNub(pnconfig)


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class PubSubManager(SubscribeCallback):

    message_received = {}

    def presence(self, pubnub, presence):
        print("presence->", pubnub, presence)

    def status(self, pubnub, status):
        pass

    def message(self, pubnub, message):
        print("PubSub message ->", message.message)
        self.message_received['teste'] = message.message
        print(self.message_received)



pubnub.add_listener(PubSubManager())
pubnub.subscribe().channels('veacon_channel_gateway_%s' % BEACON_GATEWAY_ID).execute()
