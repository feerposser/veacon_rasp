from beacons.manage_data import BeaconManager
from watchposts.manage_data import WatchpostManager
from pubsub.pubsub import PubSubManager


class Core(BeaconManager, WatchpostManager, PubSubManager):

    def __init__(self):
        WatchpostManager.__init__(self)
        allowed_beacons = WatchpostManager.get_all_listening_watchposts_beacons()
        BeaconManager.__init__(self, allowed_beacons=allowed_beacons)

    def execute(self):
        self.beacon_process()
