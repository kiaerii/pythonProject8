"""
Кастомные исключения для приложения.
"""


class BaseAppError(Exception):
    """Базовое исключение для всего приложения."""
    pass


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
