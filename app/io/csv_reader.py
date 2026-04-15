"""
Чтение CSV файлов с финансовыми данными.
"""

import csv
from typing import Iterator
import logging

from app.io.base_reader import BaseReader
from app.core.exceptions import DataFormatError, EmptyFileError

logger = logging.getLogger(__name__)


class CSVReader(BaseReader):
    """Ридер для CSV файлов."""

    REQUIRED_FIELDS = {'id', 'amount', 'category', 'date'}

    def _validate_file(self) -> None:
        """Проверка существования и доступности файла."""
        super()._validate_file()

        # Проверка на пустой файл
        if self.file_path.stat().st_size == 0:
            raise EmptyFileError(f"Файл {self.file_path.name} пустой")

    def read_records(self) -> Iterator[dict]:
        """Читает CSV файл построчно."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Проверяем наличие обязательных колонок
                if reader.fieldnames:
                    missing_fields = self.REQUIRED_FIELDS - set(
                        reader.fieldnames
                    )
                    if missing_fields:
                        raise DataFormatError(
                            f"Отсутствуют обязательные колонки: {missing_fields}"
                        )

                for row_num, row in enumerate(reader, start=2):
                    if not any(row.values()):
                        continue

                    # Проверяем наличие всех полей
                    if not all(field in row for field in self.REQUIRED_FIELDS):
                        logger.warning(
                            f"Строка {row_num} в {self.file_path.name} "
                            f"пропущена"
                        )
                        continue

                    yield row

        except UnicodeDecodeError as e:
            raise DataFormatError(
                f"Ошибка кодировки в файле {self.file_path.name}",
                original_error=e
            )
        except csv.Error as e:
            raise DataFormatError(
                f"Ошибка парсинга CSV в файле {self.file_path.name}",
                original_error=e
            )

    @staticmethod
    def supports_extension(extension: str) -> bool:
        """Проверяет поддержку расширения."""
        return extension.lower() == '.csv'