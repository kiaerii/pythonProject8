"""Модели данных для финансовых транзакций."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Transaction:
    """Модель финансовой транзакции."""

    id: str
    amount: Decimal
    category: str
    date: datetime
    currency: str = "RUB"
    description: str = None

    def __post_init__(self):
        """Дополнительная валидация после инициализации."""
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    def to_dict(self) -> dict:
        """Преобразование в словарь для экспорта."""
        return {
            "id": self.id,
            "amount": float(self.amount),
            "category": self.category,
            "date": self.date.isoformat(),
            "currency": self.currency,
            "description": self.description
        }


@dataclass
class ProcessingError:
    """Модель ошибки обработки."""

    file_name: str
    record_id: str
    error_type: str
    error_message: str
    original_data: dict = None
