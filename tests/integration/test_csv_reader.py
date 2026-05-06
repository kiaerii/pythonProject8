"""
Интеграционные тесты для CSV Reader
"""

import pytest

from app.io.csv_reader import CSVReader
from app.services.validator import TransactionValidator
from app.services.aggregator import TransactionAggregator
from app.core.exceptions import DataFormatError, EmptyFileError


class TestCSVReader:
    """Тесты для CSV Reader"""

    def test_read_valid_csv(self, temp_csv_file):
        """Тест: чтение валидного CSV файла"""
        reader = CSVReader(temp_csv_file)
        records = list(reader.read_records())

        assert len(records) == 3
        assert records[0]['id'] == 'tx001'
        assert records[0]['amount'] == '1500.50'

    def test_csv_missing_columns(self, tmp_path):
        """Тест: CSV файл без обязательных колонок"""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("id,name,value\n1,test,100", encoding='utf-8')

        with pytest.raises(DataFormatError) as exc_info:
            CSVReader(bad_csv)

        assert "Отсутствуют обязательные колонки" in str(exc_info.value)

    def test_empty_csv_file(self, tmp_path):
        """Тест: пустой CSV файл вызывает EmptyFileError"""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("", encoding='utf-8')

        with pytest.raises(EmptyFileError) as exc_info:
            CSVReader(empty_csv)

        assert "пустой" in str(exc_info.value).lower()

    def test_csv_with_bom(self, tmp_path):
        """Тест: CSV файл с BOM-символами"""
        bom_csv = tmp_path / "bom.csv"
        bom_csv.write_bytes(
            b'\xef\xbb\xbfid,amount,category,date\n1,100,food,2024-01-15'
        )

        reader = CSVReader(bom_csv)
        records = list(reader.read_records())

        assert len(records) == 1
        assert records[0]['id'] == '1'

    def test_csv_mixed_valid_invalid_rows(self, tmp_path):
        """Тест: 1 хорошая и 2 плохие строки → в JSON только 1 запись"""
        content = (
            "id,amount,category,date\n"
            "good_001,100.50,food,2024-01-15\n"
            "bad_001,-50.00,transport,2024-01-16\n"
            "bad_002,200.00,invalid,2024-01-17\n"
        )
        mixed_csv = tmp_path / "mixed.csv"
        mixed_csv.write_text(content, encoding='utf-8')

        reader = CSVReader(mixed_csv)
        validator = TransactionValidator()
        aggregator = TransactionAggregator()

        valid_count = 0
        for record in reader.read_records():
            transaction = validator.validate_and_create_transaction(
                record, 'mixed.csv'
            )
            if transaction:
                aggregator.add_transaction(transaction)
                valid_count += 1

        assert valid_count == 1
        assert len(validator.errors) == 2
