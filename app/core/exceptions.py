"""Кастомные исключения для приложения."""


class BaseAppError(Exception):
    """Базовое исключение для всего приложения."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class FatalError(BaseAppError):
    """Критическая ошибка, после которой программа не может работать."""
    pass


class DataFormatError(BaseAppError):
    """Ошибка структуры файла."""
    pass


class ValidationError(BaseAppError):
    """Ошибка бизнес-логики."""
    pass


class CurrencyMismatchError(ValidationError):
    """Ошибка несоответствия валют."""
    pass


class DuplicateIdError(ValidationError):
    """Ошибка дублирования идентификатора."""
    pass

class EmptyFileError(DataFormatError):
    """Ошибка: файл пустой (0 байт)"""
    pass

