"""
Чтение JSON файлов с финансовыми данными.
"""

import json
from typing import Iterator
import logging

from app.io.base_reader import BaseReader
from app.core.exceptions import DataFormatError

logger = logging.getLogger(__name__)


class JSONReader(BaseReader):
    """Ридер для JSON файлов."""

    def read_records(self) -> Iterator[dict]:
        """Читает JSON файл."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Поддерживаем разные структуры JSON
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict) and 'transactions' in data:
                records = data['transactions']
            elif isinstance(data, dict):
                records = [data]
            else:
                raise DataFormatError(
                    f"Неподдерживаемая структура JSON в файле "
                    f"{self.file_path.name}"
                )

            for record in records:
                if not isinstance(record, dict):
                    logger.warning(
                        f"Пропущен некорректный"
                        f"элемент в {self.file_path.name}"
                    )
                    continue

                required_fields = {'id', 'amount', 'category', 'date'}
                if not all(field in record for field in required_fields):
                    logger.warning(
                        f"Элемент {record.get('id', 'unknown')} в "
                        f"{self.file_path.name} пропущен"
                    )
                    continue

                yield record

        except json.JSONDecodeError as e:
            raise DataFormatError(
                f"Ошибка парсинга JSON в файле {self.file_path.name}",
                original_error=e
            )

    @staticmethod
    def supports_extension(extension: str) -> bool:
        """Проверяет поддержку расширения."""
        return extension.lower() == '.json'
