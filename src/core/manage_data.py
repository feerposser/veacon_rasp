from beacons.manage_data import BeaconManager
from watchposts.manage_data import WatchpostManager
from pubsub.pubsub import PubSubManager


class Core(BeaconManager, WatchpostManager, PubSubManager):

    def __init__(self):
        WatchpostManager.__init__(self)
        print('watchposts ->', self.watchposts)
        allowed_beacons = self.get_all_listening_watchposts_beacons()
        BeaconManager.__init__(self, allowed_beacons=allowed_beacons)
        PubSubManager.__init__(self)

    def execute(self):
        if self.watchposts:
            self.beacon_process()
