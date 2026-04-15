"""
Валидация данных финансовых транзакций.
"""

from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Set, Optional
import logging

from app.core.models import Transaction, ProcessingError
from app.core.exceptions import (
    ValidationError,
    DuplicateIdError,
    CurrencyMismatchError
)

logger = logging.getLogger(__name__)


class TransactionValidator:
    """Валидатор транзакций."""

    ALLOWED_CATEGORIES = {
        'food', 'transport', 'utilities', 'entertainment', 'salary', 'other'
    }
    ALLOWED_CURRENCIES = {'RUB', 'USD', 'EUR'}

    def __init__(self):
        self.processed_ids: Set[str] = set()
        self.errors: list[ProcessingError] = []

    def validate_and_create_transaction(
        self,
        raw_data: dict,
        file_name: str,
        strict_duplicates: bool = True
    ) -> Optional[Transaction]:
        """Валидирует сырые данные и создает объект Transaction."""
        transaction_id = raw_data.get('id', 'unknown')

        try:
            # Валидация ID
            if not transaction_id or not isinstance(transaction_id, str):
                raise ValidationError(f"Некорректный ID: {transaction_id}")

            # Проверка дубликатов
            if strict_duplicates and transaction_id in self.processed_ids:
                raise DuplicateIdError(f"Дублирующийся ID: {transaction_id}")

            # Валидация amount
            try:
                amount = Decimal(str(raw_data.get('amount', 0)))
                if amount <= 0:
                    raise ValidationError(
                        f"Amount должен быть положительным: {amount}"
                    )
            except (InvalidOperation, ValueError, TypeError):
                raise ValidationError(
                    f"Некорректный amount: {raw_data.get('amount')}"
                )

            # Валидация category
            category = raw_data.get('category', '').lower().strip()
            if not category:
                raise ValidationError("Category не может быть пустым")
            if category not in self.ALLOWED_CATEGORIES:
                logger.warning(
                    f"Неизвестная категория '{category}' в транзакции "
                    f"{transaction_id}"
                )

            # Валидация date
            date_str = raw_data.get('date')
            if not date_str:
                raise ValidationError("Date не может быть пустым")

            try:
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d.%m.%Y']:
                    try:
                        date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValidationError(
                        f"Некорректный формат даты: {date_str}"
                    )
            except (ValueError, TypeError):
                raise ValidationError(f"Некорректная дата: {date_str}")

            # Валидация currency (опционально)
            currency = raw_data.get('currency', 'RUB').upper()
            if currency not in self.ALLOWED_CURRENCIES:
                logger.warning(
                    f"Неизвестная валюта '{currency}' в транзакции "
                    f"{transaction_id}, используем RUB"
                )
                currency = 'RUB'

            # Создаем транзакцию
            transaction = Transaction(
                id=transaction_id,
                amount=amount,
                category=category,
                date=date,
                currency=currency,
                description=raw_data.get('description')
            )

            self.processed_ids.add(transaction_id)
            return transaction

        except ValidationError as e:
            self.errors.append(ProcessingError(
                file_name=file_name,
                record_id=transaction_id if transaction_id != 'unknown'
                else None,
                error_type=e.__class__.__name__,
                error_message=str(e),
                original_data=raw_data
            ))
            return None

    def check_currency_consistency(self, transactions: list) -> None:
        """Проверяет, что все транзакции имеют одинаковую валюту."""
        if not transactions:
            return

        currencies = set(t.currency for t in transactions)
        if len(currencies) > 1:
            raise CurrencyMismatchError(
                f"Обнаружены транзакции в разных валютах: {currencies}"
            )

    def clear(self) -> None:
        """Очищает состояние валидатора."""
        self.processed_ids.clear()
        self.errors.clear()
