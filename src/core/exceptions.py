

class WatchpostException(Exception):
    """Erros gerados na classe Watchpost"""
    pass


class RefreshMedianWatchpostException(Exception):
    """Erro gerado ao atualizar a mediana do watchpost"""
    pass


class MessageReceivedException(Exception):
    """ Erro gerado ao receber uma mensagem inválida do PubSub"""
    pass