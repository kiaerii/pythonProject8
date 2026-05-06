"""
Модуль ввода/вывода
"""

from pathlib import Path
from typing import Optional
import logging

from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader

logger = logging.getLogger(__name__)


class ReaderRegistry:
    """Реестр ридеров для разных типов файлов"""

    @staticmethod
    def get_reader(file_path: Path) -> Optional:
        """Возвращает подходящий ридер для файла"""
        extension = file_path.suffix.lower()

        if extension == '.csv':
            return CSVReader(file_path)
        elif extension == '.json':
            return JSONReader(file_path)
        else:
            logger.warning(f"Неподдерживаемый формат: {extension}")
            return None


# Для удобства
get_reader = ReaderRegistry.get_reader
