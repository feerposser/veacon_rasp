import sys

from core.manage_data import Core

sys_exit = 0  # inserir alguma regra para finalizar o processo

if __name__ == "__main__":
    print("...Iniciando...")
    core = Core()
    count = 1
    while True:
        print("Iniciando sequencia #{}".format(count))
        core.execute()
        if sys_exit:
            break
        print("Encerrando sequencia#{}".format(count))
        count += 1
    print("...Encerrando...")
