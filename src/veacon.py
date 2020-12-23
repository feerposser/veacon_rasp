import time

from core.manage_data import Core

sys_exit = 0  # inserir alguma regra para finalizar o processo

# teste

if __name__ == "__main__":
    print("...Iniciando...")
    core = Core()
    count = 1
    wait = 10
    while True:
        print("Iniciando sequencia #{}".format(count))
        core.execute()
        if sys_exit:
            break
        print("Encerrando sequencia#{}".format(count))
        print("sleep {}'s".format(wait))
        time.sleep(wait)
        count += 1
    print("...Encerrando...")
