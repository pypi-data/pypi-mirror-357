class OzonAPIError(Exception):
    """Базовое исключение для ошибок Ozon API."""

    def __init__(self, code: int, message: str, details: list | None = None):
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(f"Ozon API Error {code}: {message}")


class OzonAPIClientError(OzonAPIError):
    """Ошибка 400: Неверный параметр."""

    pass


class OzonAPIForbiddenError(OzonAPIError):
    """Ошибка 403: Доступ запрещён."""

    pass


class OzonAPINotFoundError(OzonAPIError):
    """Ошибка 404: Ответ не найден."""

    pass


class OzonAPIConflictError(OzonAPIError):
    """Ошибка 409: Конфликт запроса."""

    pass


class OzonAPIServerError(OzonAPIError):
    """Ошибка 500: Внутренняя ошибка сервера."""

    pass
