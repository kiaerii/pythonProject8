"""
Базовый класс для всех ридеров файлов.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator
import logging

from app.core.exceptions import DataFormatError

logger = logging.getLogger(__name__)


class BaseReader(ABC):
    """Абстрактный класс для чтения файлов разных форматов."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._validate_file()

    def _validate_file(self) -> None:
        """Проверка существования и доступности файла."""
        if not self.file_path.exists():
            raise DataFormatError(f"Файл не существует: {self.file_path}")

        if not self.file_path.is_file():
            raise DataFormatError(f"Путь не является файлом: {self.file_path}")

        try:
            # Проверка доступности для чтения
            self.file_path.read_bytes()[:1]
        except (PermissionError, OSError) as e:
            raise DataFormatError(
                f"Файл недоступен для чтения: {self.file_path}",
                original_error=e
            )

    @abstractmethod
    def read_records(self) -> Iterator[dict]:
        """
        Чтение записей из файла.
        Возвращает итератор словарей (сырые данные).
        """
        pass

    @staticmethod
    def supports_extension(extension: str) -> bool:
        """Проверяет, поддерживает ли ридер данное расширение."""
        return False
