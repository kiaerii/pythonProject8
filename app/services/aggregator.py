"""
Агрегация данных и экспорт результатов.
"""

from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import json
import shutil
import logging

from app.core.exceptions import FatalError

logger = logging.getLogger(__name__)


class TransactionAggregator:
    """Агрегатор транзакций по категориям."""

    def __init__(self):
        self.transactions = defaultdict(list)
        self.category_totals = defaultdict(Decimal)

    def add_transaction(self, transaction) -> None:
        """Добавляет транзакцию в агрегатор."""
        self.transactions[transaction.category].append(transaction)
        self.category_totals[transaction.category] += transaction.amount

    def export_to_json(
            self, output_path: Path, atomic_write: bool = True
    ) -> None:
        """Экспортирует агрегированные данные в JSON."""
        result = {
            "summary": {
                "total_transactions": sum(
                    len(txs) for txs in self.transactions.values()
                ),
                "total_categories": len(self.category_totals),
                "categories": {
                    category: float(total)
                    for category, total in self.category_totals.items()
                }
            },
            "details": {
                category: [t.to_dict() for t in transactions]
                for category, transactions in self.transactions.items()
            }
        }

        # Атомарная запись с использованием временного файла
        if atomic_write:
            temp_path = output_path.parent / f"{output_path.name}.tmp"

            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                shutil.move(str(temp_path), str(output_path))
                logger.info(f"Данные успешно экспортированы в {output_path}")

            except (IOError, OSError) as e:
                if temp_path.exists():
                    temp_path.unlink()
                raise FatalError(
                    f"Ошибка при записи результата: {e}",
                    original_error=e
                )
        else:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except (IOError, OSError) as e:
                raise FatalError(
                    f"Ошибка при записи результата: {e}",
                    original_error=e
                )

    def get_summary(self) -> dict:
        """Возвращает сводку по агрегированным данным."""
        return {
            "category_totals": {
                category: float(total)
                for category, total in self.category_totals.items()
            },
            "transaction_count": sum(
                len(txs) for txs in self.transactions.values()
            )
        }

    def clear(self) -> None:
        """Очищает агрегатор."""
        self.transactions.clear()
        self.category_totals.clear()
