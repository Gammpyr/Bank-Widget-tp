from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.reports import get_spending_by_category, report_to_selected_file


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными транзакций"""
    return pd.DataFrame(
        {
            "Дата операции": ["01-01-2021", "15-01-2023", "01-02-2023", "15-02-2021", "01-03-2021", "15-03-2021"],
            "Описание": ["Почта России", "Магнит", "Анжи", "Магнит", "Копеечка", "Копеечка"],
            "Категория": ["Госуслуги", "Супермаркеты", "Такси", "Супермаркеты", "Супермаркеты", "Супермаркеты"],
            "Сумма платежа": [-1000, -1500, -500, -2000, -800, -300],
            "Статус": [
                "OK",
                "OK",
                "OK",
                "OK",
                "OK",
                "OK",
            ],
        }
    )


@patch("builtins.open")
def test_report_to_selected_file(mock_open):
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = "{}"
    mock_open.return_value = mock_file

    @report_to_selected_file("fake_file.txt")
    def fake_func():
        return []

    assert fake_func() == []


def test_get_spending_by_category_current_date(sample_transactions):
    """Тестируем последние 3 месяца с указанной даты"""
    test_date = datetime(2021, 4, 17)

    result = get_spending_by_category(sample_transactions, "Супермаркеты", test_date.strftime("%d-%m-%Y"))

    expected = {
        "Копеечка": 1100,
        "Магнит": 2000,
    }

    assert result == expected


def test_get_spending_by_category_no_data(sample_transactions):
    """Нет подходящих категорий"""
    result = get_spending_by_category(sample_transactions, "Каршеринг", "15-03-2023")

    assert result == {}


def test_get_spending_by_category_empty_input():
    """пустой DataFrame"""
    empty_df = pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Категория", "Описание", "Статус"])
    result = get_spending_by_category(empty_df, "Категория")

    assert result == {}
