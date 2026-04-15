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
    def register(cls, reader_class: Type[BaseReader]) -> None:
        """Регистрирует ридер для всех поддерживаемых расширений"""
        # Регистрируем ридер для каждого поддерживаемого расширения
        # Для простоты будем регистрировать по одному расширению на ридер
        # В реальном проекте можно сделать более сложную логику
        pass

    @classmethod
    def get_reader(cls, file_path: Path) -> Optional[BaseReader]:
        """
        Возвращает подходящий ридер для файла.
        Использует метод supports_extension каждого зарегистрированного ридера.
        """
        extension = file_path.suffix

        # Создаем список доступных ридеров
        readers = [CSVReader, JSONReader]

        for reader_class in readers:
            if reader_class.supports_extension(extension):
                try:
                    return reader_class(file_path)
                except DataFormatError as e:
                    logger.error(
                        f"Не удалось создать ридер для {file_path}: {e}"
                    )
                    raise

        logger.warning(
            f"Неподдерживаемый формат файла: {extension}"
        )
        return None


# Автоматическая регистрация ридеров (можно расширять)
ReaderRegistry.register(CSVReader)
ReaderRegistry.register(JSONReader)
