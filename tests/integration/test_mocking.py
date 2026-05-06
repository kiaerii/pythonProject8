"""
Тесты с использованием Mocking
"""

import pytest
from unittest.mock import patch, mock_open
from decimal import Decimal
from datetime import datetime

from app.services.aggregator import TransactionAggregator
from app.core.exceptions import FatalError
from app.core.models import Transaction


class TestMocking:
    """Тесты с имитацией системных ошибок"""

    @pytest.fixture
    def aggregator_with_data(self):
        """Создает агрегатор с данными"""
        agg = TransactionAggregator()

        tx = Transaction(
            id="test_001",
            amount=Decimal("100.50"),
            category="food",
            date=datetime(2024, 1, 15)
        )
        agg.add_transaction(tx)
        return agg

    def test_export_handles_write_error(self, aggregator_with_data, tmp_path):
        """Тест: проверка обработки ошибки при записи файла"""
        output_file = tmp_path / "result.json"

        with patch('builtins.open', mock_open()) as mocked_open:
            mocked_open.side_effect = PermissionError(
                "Disk is write-protected"
            )

            with pytest.raises(FatalError):
                aggregator_with_data.export_to_json(
                    output_file, atomic_write=True
                )

    def test_atomic_write_creates_temp_file(
        self, aggregator_with_data, tmp_path
    ):
        """Тест: проверка атомарной записи (временный файл)"""
        output_file = tmp_path / "result.json"

        aggregator_with_data.export_to_json(
            output_file, atomic_write=True
        )

        temp_file = tmp_path / "result.json.tmp"
        assert not temp_file.exists()
        assert output_file.exists()
