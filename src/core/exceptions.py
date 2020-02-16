

class WatchpostException(Exception):
    """Erros gerados na classe Watchpost"""
    pass


class AddWatchpostException(WatchpostException):
    """ Erro gerado ao adicionar um watchpost """
    pass


class RefreshMedianWatchpostException(Exception):
    """Erro gerado ao atualizar a mediana do watchpost"""
    pass


class MessageReceivedException(Exception):
    """ Erro gerado ao receber uma mensagem inválida do PubSub"""
    pass


class WatchpostAlreadyExistsException(Exception):
    """ Erro gerado ao tentar adicionar um monitoramento já existente """
    pass

class StatusNotAcceptable(Exception):
    """ Erro gerado quando um status não é válido """
    pass

class BeaconAlreadyInAllowedBeaconsException(Exception):
    """ Erro gerado quando um beacon já existente tenta ser inserido na lista allowed_beacons """
    pass