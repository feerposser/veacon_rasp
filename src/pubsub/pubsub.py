from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub


pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'demo'
pnconfig.publish_key = 'demo'

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

    def __init__(self):
        self.status = {}

    def presence(self, pubnub, presence):
        print("presence->", pubnub, presence)

    def status(self, pubnub, status):
        pass

    def message(self, pubnub, message):
        print("PubSub message ->", message.message)

    @staticmethod
    def send_message(self, message):
        try:
            pubnub.publish().channel("veaconChannel").message(message).pn_async(my_publish_callback)
        except Exception as e:
            print(e)


pubnub.add_listener(PubSubManager())
pubnub.subscribe().channels('veaconChannel').execute()
