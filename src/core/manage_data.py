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

    def execute(self):
        if self.message_received:
            messages = self.message_received.copy()
            self.message_received.clear()
            print('pub sub messages --->', messages)

        if self.watchposts:
            self.beacon_process()

        for beacon in self.eddy_namespace_rrsi:
            print("Enviando rssi '%s'" % beacon, self.eddy_namespace_rrsi[beacon])
            v = self.validate_read_beacons(beacon, self.eddy_namespace_rrsi[beacon], set_warning=True)

            print("Esperando 100s para o teste.\nLista de warnings:", *v)
            time.sleep(100)
