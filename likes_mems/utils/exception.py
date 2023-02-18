class JSONError(Exception):
    """Ошибка обработки JSON."""
    pass


class RequestError(Exception):
    """Ошибка Request."""
    pass


class HTTPStatusNotOK(Exception):
    """API вернул код отличный от 200."""
    pass


class EnvironmentVar(Exception):
    """Отстутствуют обязательные переменные окружения."""
    pass
