"""
Realiza o mesmo teste que o teste_bluepy, porém, conitnuamente.
"""
from bluepy.btle import Scanner, DefaultDelegate


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr, "\n\tRSSI:", dev.rssi)


scanner = Scanner().withDelegate(ScanDelegate())

scanner.start()
while True:
    print("Still running...")
    scanner.process()
