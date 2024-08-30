

class AuthorizationBaseException(Exception):
    """Базовый класс для всех исключений, связанных с авторизацией."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DatabaseError(AuthorizationBaseException):
    """Исключение для ошибок, связанных с базой данных."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
