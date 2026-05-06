"""
Интеграционные тесты для агрегатора
"""

import pytest
import json
from decimal import Decimal
from datetime import datetime

from app.services.aggregator import TransactionAggregator
from app.core.models import Transaction


class TestTransactionAggregator:
    """Тесты для агрегатора транзакций"""

    @pytest.fixture
    def aggregator(self):
        """Фикстура: создает чистый агрегатор"""
        return TransactionAggregator()

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура: создает набор транзакций"""
        return [
            Transaction(
                id="tx001",
                amount=Decimal("100.50"),
                category="food",
                date=datetime(2024, 1, 15)
            ),
            Transaction(
                id="tx002",
                amount=Decimal("200.75"),
                category="food",
                date=datetime(2024, 1, 16)
            ),
            Transaction(
                id="tx003",
                amount=Decimal("50.00"),
                category="transport",
                date=datetime(2024, 1, 17)
            ),
        ]

    def test_add_transaction(self, aggregator, sample_transactions):
        """Тест: добавление транзакций"""
        for tx in sample_transactions:
            aggregator.add_transaction(tx)

        assert len(aggregator.transactions['food']) == 2
        assert len(aggregator.transactions['transport']) == 1

    def test_category_totals(self, aggregator, sample_transactions):
        """Тест: подсчет сумм по категориям"""
        for tx in sample_transactions:
            aggregator.add_transaction(tx)

        assert aggregator.category_totals['food'] == Decimal("301.25")
        assert aggregator.category_totals['transport'] == Decimal("50.00")

    def test_export_to_json(self, aggregator, sample_transactions, tmp_path):
        """Тест: экспорт в JSON файл"""
        for tx in sample_transactions:
            aggregator.add_transaction(tx)

        output_file = tmp_path / "result.json"
        aggregator.export_to_json(output_file, atomic_write=True)

        assert output_file.exists()

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['summary']['total_transactions'] == 3
        assert data['summary']['categories']['food'] == 301.25

    def test_clear_method(self, aggregator, sample_transactions):
        """Тест: очистка агрегатора"""
        for tx in sample_transactions:
            aggregator.add_transaction(tx)

        assert len(aggregator.transactions) > 0
        assert len(aggregator.category_totals) > 0

        aggregator.clear()

        assert len(aggregator.transactions) == 0
        assert len(aggregator.category_totals) == 0
