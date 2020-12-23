import sys
import csv
import time

from constant_ble_read import ReadBLE

sys.path.append('testes/')

while True:
    try:
        start = input("Iniciar teste [s] - sim / [n] - não: ")
        if start != "s":
            break

        name = input("Nome do teste: ")
        distance = int(input("Distância: "))
        read_time_sec = int(input("Tempo de leitura (segundos - mínimo 10): "))
        if read_time_sec < 10:
            read_time_sec = 10

        csv_file = open(name +
                        "_distance_{}_".format(distance) +
                        time.strftime("%d-%m-%y|%H-%M") +
                        ".csv", "w")

        rssi_list = ReadBLE(read_time_sec, "edd1ebeac04e5defa017").read_ble()

        if not rssi_list:
            raise Exception("LIsta de rssi vazia.\nVerifique se o beacon está próximo")

        with csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(rssi_list)
    except Exception as e:
        print("Erro:\n", e)
