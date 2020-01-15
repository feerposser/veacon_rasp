"""
Teste utilizando a ferramenta Beacontools para Python
https://pypi.org/project/beacontools/

iBeacon ficou preciso, porém, devagar.
Eddystone ficou rápido, porém, impreciso.
"""


import time
from beacontools import BeaconScanner, IBeaconFilter, EddystoneTLMFrame, EddystoneFilter, EddystoneUIDFrame, \
    EddystoneURLFrame


def callback(bt_addr, rssi, packet, additional_info):
    print('----------------------------------------------------')
    # print("%s - %d - %s - %s\n-" % (bt_addr, rssi, packet, additional_info))
    print(packet.namespace)

beacon_type = input("iBeacon / Eddystone - (i/e)")

if beacon_type == 'i':
    # scan for all iBeacon advertisements from beacons with the specified uuid
    scanner = BeaconScanner(callback,
        device_filter=IBeaconFilter(uuid="b9407f30-f5f8-466e-aff9-25556b57fe6d")
    )

    scanner.start()

    while True:
        pass

    scanner.stop()

elif beacon_type == 'e':

    try:

        if input("all/one (a/o): ") == 'o':

            # scan for all TLM frames of beacons in the namespace
            scanner = BeaconScanner(callback,
                                    device_filter=EddystoneFilter(namespace="edd1ebeac04e5defa017"),
                                    packet_filter=EddystoneTLMFrame
                                    )

            scanner.start()

            time.sleep(10)

        else:
            scanner = BeaconScanner(callback, packet_filter=[EddystoneUIDFrame])

            scanner.start()

            time.sleep(10)

            scanner.stop()

    except Exception as e:
        print(e.args)
