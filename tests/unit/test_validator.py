"""
Unit-тесты для валидатора транзакций
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.services.validator import TransactionValidator
from app.core.exceptions import ValidationError, DuplicateIdError


class TestTransactionValidator:
    """Тесты для валидатора транзакций"""

    @pytest.fixture
    def validator(self):
        """Фикстура: создает чистый валидатор для каждого теста"""
        return TransactionValidator()

    # ========== ТЕСТЫ ДЛЯ СУММЫ ==========

    @pytest.mark.parametrize("amount, expected_valid", [
        (Decimal("0.01"), True),      # минимальная валидная сумма
        (Decimal("100.50"), True),     # обычная сумма
        (Decimal("999999.99"), True),  # большая сумма
        (Decimal("0"), False),         # ноль - невалидно
        (Decimal("-0.01"), False),     # отрицательная - невалидно
        (-100, False),                 # отрицательное число
        (0, False),                    # ноль
    ])
    def test_amount_validation(self, validator, amount, expected_valid):
        """Тест: проверка валидации суммы с разными значениями"""
        # Arrange (Подготовка)
        data = {
            'id': 'test_001',
            'amount': amount,
            'category': 'food',
            'date': '2024-01-15'
        }

        # Act (Действие)
        result = validator.validate_and_create_transaction(data, 'test.csv')

        # Assert (Проверка)
        if expected_valid:
            assert result is not None
            assert result.amount == Decimal(str(amount))
        else:
            assert result is None
            assert len(validator.errors) > 0

    # ========== ТЕСТЫ ДЛЯ ID ==========

    @pytest.mark.parametrize("transaction_id, should_pass", [
        ("valid_id_123", True),      # нормальный ID
        ("abc", True),               # короткий ID
        ("", False),                 # пустой ID
        (None, False),               # None ID
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

    # ========== ТЕСТЫ ДЛЯ ДАТЫ ==========

    @pytest.mark.parametrize("date_str, should_pass", [
        ("2024-01-15", True),        # стандартный формат
        ("2024-12-31", True),        # конец года
        ("2024-01-15T10:30:00", True),  # с временем
        ("15.01.2024", True),        # российский формат
        ("invalid-date", False),     # неверный формат
        ("", False),                 # пустая дата
        (None, False),               # None дата
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

    # ========== ТЕСТЫ ДЛЯ КАТЕГОРИЙ ==========

    @pytest.mark.parametrize("category, should_pass", [
        ("food", True),
        ("transport", True),
        ("utilities", True),
        ("entertainment", True),
        ("salary", True),
        ("other", True),
        ("unknown_category", True),  # логируем но не ошибка
        ("", False),                 # пустая категория - ошибка
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

    # ========== ТЕСТ НА ДУБЛИКАТЫ ==========

    def test_duplicate_id_error(self, validator):
        """Тест: проверка что дублирующийся ID вызывает ошибку"""
        data = {
            'id': 'duplicate_id',
            'amount': Decimal("100.50"),
            'category': 'food',
            'date': '2024-01-15'
        }

        # Первая транзакция - должна пройти
        result1 = validator.validate_and_create_transaction(data, 'test.csv')
        assert result1 is not None

        # Вторая транзакция с тем же ID - должна быть отклонена
        result2 = validator.validate_and_create_transaction(data, 'test.csv')
        assert result2 is None

        # Проверяем что ошибка записана
        duplicate_errors = [e for e in validator.errors
                           if e.error_type == 'DuplicateIdError']
        assert len(duplicate_errors) > 0

    # ========== ТЕСТ НА ОШИБКИ ==========

    def test_validation_error_raised_on_invalid_data(self, validator):
        """Тест: проверка что при невалидных данных выбрасывается ошибка"""
        data = {
            'id': 'test_001',
            'amount': "not_a_number",  # не число!
            'category': 'food',
            'date': '2024-01-15'
        }

        result = validator.validate_and_create_transaction(data, 'test.csv')

        # Должен вернуть None и добавить ошибку
        assert result is None
        assert len(validator.errors) > 0
        assert validator.errors[0].error_type == 'ValidationError'
