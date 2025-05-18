import pandas as pd
import pytest

from src.services import get_high_cashback_categories, investment_bank


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными транзакций"""
    return pd.DataFrame({
        "Дата операции": ["01-01-2023", "15-01-2023", "01-01-2022", "15-01-2023", "01-01-2023", "15-02-2023"],
        "Описание": ["Почта России", "Магнит", "Анжи", "Магнит", "Копеечка", "Копеечка"],
        "Категория": ["Госуслуги", "Супермаркеты", "Такси", "Супермаркеты", "Супермаркеты", "Супермаркеты"],
        "Сумма платежа": [-1000, 1500, -500, -2000, -800, -300],
        "Статус": ["OK", "OK", "OK", "OK", "OK", "OK", ]
    })


@pytest.fixture
def sample_investment_data():
    """Фикстура с тестовыми данными для инвестиций"""
    return [
        {"date": "2025-05-14", "amount": -68},
        {"date": "2025-05-14", "amount": -44},
        {"date": "2025-04-13", "amount": -33},
        {"date": "2024-05-22", "amount": 112},
    ]


def test_get_high_cashback_categories(sample_transactions):
    """Тест работоспособности"""
    result = get_high_cashback_categories(sample_transactions, 2023, 1)

    assert result == {"Супермаркеты": 28, "Госуслуги": 10}


def test_get_high_cashback_categories_empty_result(sample_transactions):
    """нет подходящих транзакций"""
    result = get_high_cashback_categories(sample_transactions, 2023, 4)
    assert result == {}


def test_investment_bank(sample_investment_data):
    """Тест работоспособности"""
    result = investment_bank("2025-05", sample_investment_data, 50)
    assert result == 38


def test_investment_bank_no_remainders(sample_investment_data):
    """Тест с суммами, уже равными лимиту"""
    test_data = [{"date": "2025-01", "amount": -200},
                 {"date": "2025-01", "amount": -300}]
    result = investment_bank("2023-01", test_data, 100)
    assert result == 0


def test_investment_bank_empty_month(sample_investment_data):
    """Тест для месяца без транзакций"""
    result = investment_bank("2025-03", sample_investment_data, 100)
    assert result == 0


a =[
        {"date": "2025-05-14", "amount": -68},
        {"date": "2025-05-14", "amount": -44},
        {"date": "2025-04-13", "amount": -33},
        {"date": "2024-05-22", "amount": 112},
    ]