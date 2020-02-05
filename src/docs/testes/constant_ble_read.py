"""
faz uma leitura contínua de um tempo determinado pelo usuario e mostra na tela
"""
import time
from beacontools import BeaconScanner, EddystoneUIDFrame


def read_callback(bt_addr, rssi, packet, additional_info):
    print('namespace:', packet.namespace, 'rssi:', rssi)


def read_ble(tempo):
    scanner = BeaconScanner(read_callback, packet_filter=[EddystoneUIDFrame])
    scanner.start()
    time.sleep(tempo)
    scanner.stop()


loop_time = int(input("tempo: "))

read_ble(loop_time)
