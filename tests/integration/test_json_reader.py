"""
Интеграционные тесты для JSON Reader
"""

import pytest

from app.io.json_reader import JSONReader
from app.core.exceptions import DataFormatError


class TestJSONReader:
    """Тесты для JSON Reader"""

    def test_read_valid_json(self, temp_json_file):
        """Тест: чтение валидного JSON файла"""
        reader = JSONReader(temp_json_file)
        records = list(reader.read_records())

        assert len(records) >= 2
        assert records[0]['id'] == 'tx006'

    def test_json_wrong_format_no_transactions_key(self, tmp_path):
        """Тест: JSON файл без ключа 'transactions'"""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text('{"wrong": "format"}', encoding='utf-8')

        reader = JSONReader(bad_json)
        records = list(reader.read_records())

        assert len(records) == 0

    def test_json_invalid_format(self, tmp_path):
        """Тест: невалидный JSON (синтаксическая ошибка)"""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text(
            '{"id": "1", "amount": 100', encoding='utf-8'
        )

        with pytest.raises(DataFormatError):
            reader = JSONReader(invalid_json)
            list(reader.read_records())

    def test_empty_json_file(self, tmp_path):
        """Тест: пустой JSON файл"""
        empty_json = tmp_path / "empty.json"
        empty_json.write_text("", encoding='utf-8')

        with pytest.raises(DataFormatError):
            reader = JSONReader(empty_json)
            list(reader.read_records())

    def test_json_empty_array(self, tmp_path):
        """Тест: JSON с пустым массивом"""
        empty_array = tmp_path / "empty_array.json"
        empty_array.write_text('[]', encoding='utf-8')

        reader = JSONReader(empty_array)
        records = list(reader.read_records())

        assert len(records) == 0

    def test_json_without_required_fields(self, tmp_path):
        """Тест: JSON с записями без обязательных полей"""
        bad_data = tmp_path / "bad_data.json"
        bad_data.write_text(
            '[{"id": "1", "name": "test"}, {"id": "2", "amount": 100}]',
            encoding='utf-8'
        )

        reader = JSONReader(bad_data)
        records = list(reader.read_records())

        assert len(records) == 0
