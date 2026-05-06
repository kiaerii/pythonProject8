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
        (Decimal("999999.99"), True),
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
            assert result.amount == Decimal(str(amount))
        else:
            assert result is None
            assert len(validator.errors) > 0

    @pytest.mark.parametrize("transaction_id, should_pass", [
        ("valid_id_123", True),
        ("abc", True),
        ("", False),
        (None, False),
    ])
    def test_id_validation(self, validator, transaction_id, should_pass):
        """Тест: проверка валидации ID"""
        data = {
            'id': transaction_id,
            'amount': Decimal("100.50"),
            'category': 'food',
            'date': '2024-01-15'
        }

        result = validator.validate_and_create_transaction(data, 'test.csv')

        if should_pass:
            assert result is not None
            assert result.id == transaction_id
        else:
            assert result is None

    @pytest.mark.parametrize("date_str, should_pass", [
        ("2024-01-15", True),
        ("2024-12-31", True),
        ("2024-01-15T10:30:00", True),
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

    @pytest.mark.parametrize("category, should_pass", [
        ("food", True),
        ("transport", True),
        ("utilities", True),
        ("entertainment", True),
        ("salary", True),
        ("other", True),
        ("unknown_category", True),
        ("", False),
    ])
    def test_category_validation(self, validator, category, should_pass):
        """Тест: проверка валидации категории"""
        data = {
            'id': 'test_001',
            'amount': Decimal("100.50"),
            'category': category,
            'date': '2024-01-15'
        }

        result = validator.validate_and_create_transaction(data, 'test.csv')

        if should_pass:
            assert result is not None
            if category:
                assert result.category == category.lower()
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
            if e.error_type == 'DuplicateIdError'
        ]
        assert len(duplicate_errors) > 0

    def test_validation_error_on_invalid_data(self, validator):
        """Тест: проверка что при невалидных данных добавляется ошибка"""
        data = {
            'id': 'test_001',
            'amount': "not_a_number",
            'category': 'food',
            'date': '2024-01-15'
        }

        result = validator.validate_and_create_transaction(data, 'test.csv')

        assert result is None
        assert len(validator.errors) > 0
        assert validator.errors[0].error_type == 'ValidationError'
