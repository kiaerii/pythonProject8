"""
Модуль ввода/вывода с регистрацией ридеров
"""

from pathlib import Path
from typing import Dict, Type, Optional
import logging

from app.io.base_reader import BaseReader
from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader
from app.core.exceptions import DataFormatError

logger = logging.getLogger(__name__)


class ReaderRegistry:
    """
    Реестр ридеров для разных типов файлов.
    Реализует паттерн Registry для расширяемости.
    """

    _readers: Dict[str, Type[BaseReader]] = {}

    @classmethod
    def register(cls, extension: str, reader_class: Type[BaseReader]) -> None:
        """Регистрирует ридер для определенного расширения"""
        cls._readers[extension.lower()] = reader_class

    @classmethod
    def get_reader(cls, file_path: Path) -> Optional[BaseReader]:
        """
        Возвращает подходящий ридер для файла.
        """
        extension = file_path.suffix.lower()

        reader_class = cls._readers.get(extension)
        if reader_class:
            try:
                return reader_class(file_path)
            except DataFormatError as e:
                logger.error(f"Не удалось создать ридер для {file_path}: {e}")
                raise

        logger.warning(f"Неподдерживаемый формат файла: {extension}")
        return None


# Регистрируем доступные ридеры
ReaderRegistry.register('.csv', CSVReader)
ReaderRegistry.register('.json', JSONReader)


# Для обратной совместимости (если используется get_reader)
def get_reader(file_path: Path) -> Optional[BaseReader]:
    """Функция для получения ридера (обертка над Registry)"""
    return ReaderRegistry.get_reader(file_path)
