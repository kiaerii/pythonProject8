"""
Общие фикстуры для всех тестов
"""

import pytest
import json
from decimal import Decimal
from datetime import datetime

from app.core.models import Transaction


@pytest.fixture
def sample_valid_transaction():
    """Фикстура: создает валидную транзакцию"""
    return Transaction(
        id="test_001",
        amount=Decimal("100.50"),
        category="food",
        date=datetime(2024, 1, 15),
        currency="RUB"
    )


@pytest.fixture
def sample_csv_content():
    """Фикстура: возвращает содержимое CSV файла"""
    return """id,amount,category,date,currency,description
tx001,1500.50,food,2024-01-15,RUB,Покупка продуктов
tx002,3200.00,utilities,2024-01-16,RUB,Коммунальные платежи
tx003,-500.00,transport,2024-01-17,RUB,Отрицательная сумма
"""


@pytest.fixture
def sample_json_content():
    """Фикстура: возвращает содержимое JSON файла"""
    return {
        "transactions": [
            {
                "id": "tx006",
                "amount": 4500.75,
                "category": "food",
                "date": "2024-01-21",
                "currency": "RUB"
            },
            {
                "id": "tx007",
                "amount": -100.00,
                "category": "other",
                "date": "2024-01-23",
                "currency": "RUB"
            }
        ]
    }


@pytest.fixture
def temp_csv_file(tmp_path, sample_csv_content):
    """Фикстура: создает временный CSV файл"""
    file_path = tmp_path / "test_data.csv"
    file_path.write_text(sample_csv_content, encoding='utf-8')
    return file_path


@pytest.fixture
def temp_json_file(tmp_path, sample_json_content):
    """Фикстура: создает временный JSON файл"""
    file_path = tmp_path / "test_data.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_json_content, f)
    return file_path
