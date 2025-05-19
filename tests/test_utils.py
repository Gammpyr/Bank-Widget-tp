import json
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock

import pandas as pd
import pytest

from src.utils import get_data_from_excel, get_greetings_by_time, convert_date_to_datetime, get_exchange_rate


@pytest.fixture
def mock_df_data():
    """Фикстура с тестовыми данными DataFrame"""
    return (pd.DataFrame({
        "Сумма платежа": [-1000, -2000, 3000, -500],
        "Статус": ["OK", "OK", "OK", "FAILED"],
        "Категория": ["Супермаркеты", "Транспорт", "Каршеринг", "Переводы"],
        "Дата платежа": ["01-01-2023", "15-01-2023", "01-01-2023", "20-01-2023"],
        "Номер карты": ["1234", "5678", "1234", "5678"],
        "Описание": ["Магнит", "Такси", "Яндекс-Драйв", "Олег"]
    }))


@pytest.fixture
def mock_dict_data():
    """Фикстура с тестовыми данными Dict"""
    return [{'Дата платежа': '01-01-2023',
             'Категория': 'Супермаркеты',
             'Номер карты': '1234',
             'Описание': 'Магнит',
             'Статус': 'OK',
             'Сумма платежа': -1000},
            {'Дата платежа': '15-01-2023',
             'Категория': 'Транспорт',
             'Номер карты': '5678',
             'Описание': 'Такси',
             'Статус': 'OK',
             'Сумма платежа': -2000},
            {'Дата платежа': '01-01-2023',
             'Категория': 'Каршеринг',
             'Номер карты': '1234',
             'Описание': 'Яндекс-Драйв',
             'Статус': 'OK',
             'Сумма платежа': 3000},
            {'Дата платежа': '20-01-2023',
             'Категория': 'Переводы',
             'Номер карты': '5678',
             'Описание': 'Олег',
             'Статус': 'FAILED',
             'Сумма платежа': -500}]


@patch('src.utils.pd.read_excel')
def test_get_data_from_excel(mock_read, mock_df_data, mock_dict_data):
    mock_read.return_value = mock_df_data
    assert get_data_from_excel() == mock_dict_data
    mock_read.assert_called()


def test_get_data_from_excel_exception_error():
    assert get_data_from_excel('no_file.xlsx') == []


@pytest.mark.parametrize("test_time, expected_greeting", [
    ("2025-05-19 05", "Доброй ночи"),
    ("2025-05-19 06", "Доброе утро"),
    ("2025-05-19 12", "Добрый день"),
    ("2025-05-19 18", "Добрый вечер"),
])
@patch('src.utils.datetime')
def test_get_greetings_by_time(mock_datetime, test_time, expected_greeting):
    mock_datetime.now.return_value = datetime.strptime(test_time, '%Y-%m-%d %H')
    assert get_greetings_by_time() == expected_greeting


@pytest.mark.parametrize("test_time", [
    ("2025-05-19 00:04:05"),
    ("2025-05-20 01:03:06"),
    ("2025-05-15 02:02:07"),
    ("2025-04-11 03:01:08"),
])
def test_convert_date_to_datetime(test_time):
    assert convert_date_to_datetime(test_time) == datetime.strptime(test_time, "%Y-%m-%d %H:%M:%S")

@patch('src.utils.requests.get')
@patch('builtins.open')
def test_get_exchange_rate(mock_open, mock_get):
    mock_get.return_value.json.return_value = json.dumps({"Valute": {"USD": {"Value": 500}}})
    mock_open.read.return_value = {'user_stocks': 'AAPL', 'user_currencies': 'USD'}

    assert get_exchange_rate() == {"currency": 'USD', "rate": 5}


