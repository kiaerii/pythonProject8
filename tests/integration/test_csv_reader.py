"""
Интеграционные тесты для CSV Reader
"""

import pytest

from app.io.csv_reader import CSVReader
from app.core.exceptions import DataFormatError, EmptyFileError


class TestCSVReader:
    """Тесты для CSV Reader"""

    def test_read_valid_csv(self, temp_csv_file):
        """Тест: чтение валидного CSV файла"""
        reader = CSVReader(temp_csv_file)
        records = list(reader.read_records())

        assert len(records) >= 2
        assert records[0]['id'] == 'tx001'

    def test_csv_missing_columns(self, tmp_path):
        """Тест: CSV файл без обязательных колонок"""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("id,name,value\n1,test,100", encoding='utf-8')

        with pytest.raises(DataFormatError):
            reader = CSVReader(bad_csv)
            list(reader.read_records())

    def test_empty_csv_file(self, tmp_path):
        """Тест: пустой CSV файл вызывает EmptyFileError"""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("", encoding='utf-8')

        with pytest.raises(EmptyFileError):
            CSVReader(empty_csv)
