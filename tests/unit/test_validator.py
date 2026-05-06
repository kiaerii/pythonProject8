"""
Unit-тесты для валидатора транзакций
"""

import pytest
from decimal import Decimal

from app.services.validator import TransactionValidator


class TestTransactionValidator:
    """Тесты для валидатора транзакций"""

    @pytest.fixture
    def validator(self):
        """Фикстура: создает чистый валидатор"""
        return TransactionValidator()

    @pytest.mark.parametrize("amount, expected_valid", [
        (Decimal("0.01"), True),
        (Decimal("100.50"), True),
        (Decimal("0"), False),
        (Decimal("-0.01"), False),
        (-100, False),
        (0, False),
    ])
    def test_amount_validation(self, validator, amount, expected_valid):
        """Тест: проверка валидации суммы"""
        data = {
            'id': 'test_001',
            'amount': amount,
            'category': 'food',
            'date': '2024-01-15'
        }

        result = validator.validate_and_create_transaction(data, 'test.csv')

        if expected_valid:
            assert result is not None
        else:
            assert result is None

    @pytest.mark.parametrize("date_str, should_pass", [
        ("2024-01-15", True),
        ("2024-12-31", True),
        ("15.01.2024", True),
        ("invalid-date", False),
        ("", False),
        (None, False),
    ])
    def test_date_validation(self, validator, date_str, should_pass):
        """Тест: проверка валидации даты"""
        data = {
            'id': 'test_001',
            'amount': Decimal("100.50"),
            'category': 'food',
            'date': date_str
        }

        result = validator.validate_and_create_transaction(data, 'test.csv')

        if should_pass:
            assert result is not None
        else:
            assert result is None

    def test_duplicate_id_error(self, validator):
        """Тест: проверка дублирующегося ID"""
        data = {
            'id': 'duplicate_id',
            'amount': Decimal("100.50"),
            'category': 'food',
            'date': '2024-01-15'
        }

        result1 = validator.validate_and_create_transaction(data, 'test.csv')
        assert result1 is not None

        result2 = validator.validate_and_create_transaction(data, 'test.csv')
        assert result2 is None

        duplicate_errors = [
            e for e in validator.errors
            if 'DuplicateIdError' in str(e.error_type)
        ]
        assert len(duplicate_errors) > 0
