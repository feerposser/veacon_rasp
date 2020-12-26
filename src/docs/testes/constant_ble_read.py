"""
faz uma leitura contínua de um tempo determinado pelo usuario e mostra na tela
"""
import time
from beacontools import BeaconScanner, EddystoneUIDFrame, EddystoneFilter


class ReadBLE:

    def __init__(self, read_time, uuid):
        self.read_time = read_time
        self.uuid = uuid
        self.rssi_list = []

    def read_callback(self, bt_addr, rssi, packet, additional_info):
        self.rssi_list.append(rssi)

    def read_ble(self):
        scanner = BeaconScanner(self.read_callback,
                                packet_filter=[EddystoneUIDFrame],
                                device_filter=EddystoneFilter(namespace=self.uuid))
        scanner.start()
        print("Lendo beacon por {}'s".format(self.read_time))
        time.sleep(self.read_time)
        scanner.stop()
        return self.rssi_list


if __name__ == "__main__":
    loop_time = int(input("tempo: "))
    uuid = input("uuid: ")
    rssi_list = ReadBLE(loop_time, uuid).read_ble()
    print(uuid, "\n", *rssi_list)
