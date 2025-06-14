from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
import requests

from src.utils import (
    cash_and_transfers_count,
    convert_date_to_datetime,
    filter_data_by_range,
    filter_transaction,
    get_cards_info,
    get_data_from_excel,
    get_df_data_from_file,
    get_exchange_rate,
    get_greetings_by_time,
    get_income_category,
    get_stock_price,
    get_top5_transaction_info,
    most_spending_filter
)


@patch("src.utils.pd.read_excel")
def test_get_data_from_excel(mock_read, mock_df_data, mock_dict_data):
    mock_read.return_value = mock_df_data
    assert get_data_from_excel() == mock_dict_data
    mock_read.assert_called()


def test_get_data_from_excel_exception_error():
    assert get_data_from_excel("no_file.xlsx") == []


@pytest.mark.parametrize(
    "test_time, expected_greeting",
    [
        ("2025-05-19 05", "Доброй ночи"),
        ("2025-05-19 06", "Доброе утро"),
        ("2025-05-19 12", "Добрый день"),
        ("2025-05-19 18", "Добрый вечер"),
    ],
)
@patch("src.utils.datetime")
def test_get_greetings_by_time(mock_datetime, test_time, expected_greeting):
    mock_datetime.now.return_value = datetime.strptime(test_time, "%Y-%m-%d %H")
    assert get_greetings_by_time() == expected_greeting


@pytest.mark.parametrize(
    "test_time",
    [
        ("2025-05-19 00:04:05"),
        ("2025-05-20 01:03:06"),
        ("2025-05-15 02:02:07"),
        ("2025-04-11 03:01:08"),
    ],
)
def test_convert_date_to_datetime(test_time):
    assert convert_date_to_datetime(test_time) == datetime.strptime(test_time, "%Y-%m-%d %H:%M:%S")


def test_convert_date_to_datetime_error():
    assert convert_date_to_datetime("Апвы") is None


@patch("builtins.open")
@patch("src.utils.requests.get")
def test_get_exchange_rate(mock_get, mock_open):
    mock_response = MagicMock()
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 100}}}
    mock_get.return_value = mock_response

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = '{"user_stocks": "AAPL", "user_currencies": ["USD"]}'
    mock_open.return_value = mock_file

    assert get_exchange_rate() == [{"currency": "USD", "rate": 100}]


@patch("builtins.open")
@patch("src.utils.requests.get")
def test_get_exchange_rate_error(mock_get, mock_open):
    mock_response = MagicMock()
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 100}}}
    mock_get.return_value = mock_response

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = {"user_currencies": ["USD"]}  # словарь
    mock_open.return_value = mock_file

    assert get_exchange_rate() == []


@patch("src.utils.requests.get")
@patch("builtins.open")
def test_get_stock_price(mock_open, mock_get):
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = '{"user_stocks": ["AAPL"]}'
    mock_open.return_value = mock_file

    mock_response = MagicMock()
    mock_response.json.return_value = {"Time Series (Daily)": {"2025-05-16": {"4. close": 100.00}}}
    mock_get.return_value = mock_response

    assert get_stock_price() == [{"stock": "AAPL", "price": 100.00}]


@patch("src.utils.requests.get")
@patch("builtins.open")
def test_get_stock_price_request_exception(mock_open, mock_get):
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = '{"user_stocks": ["AAPL"]}'
    mock_open.return_value = mock_file

    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    assert get_stock_price() == []


@patch("src.utils.requests.get")
@patch("builtins.open")
def test_get_stock_price_key_error_exception(mock_open, mock_get):
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = '{"stocks": ["AAPL"]}'
    mock_open.return_value = mock_file

    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    assert get_stock_price() == []


@patch("src.utils.os.getenv")
def test_get_stock_price_not_apikey_error(mock_getenv):
    mock_getenv.return_value = ""

    with pytest.raises(ValueError):
        get_stock_price()


@patch("builtins.open", side_effect=FileNotFoundError)
def test_get_stock_price_fnf_error(mock_open):
    assert get_stock_price() == []


@patch("requests.get", side_effect=requests.exceptions.RequestException("Неверный запрос"))
def test_get_exchange_rate_failure(mock_get):
    assert get_exchange_rate() == []


def test_filter_transaction(mock_df_data):
    expected = {
        "Сумма платежа": [-1000, -2000],
        "Статус": ["OK", "OK"],
        "Категория": ["Супермаркеты", "Транспорт"],
        "Дата платежа": ["2023-01-01", "2023-02-15"],
        "Номер карты": ["1234", "5678"],
        "Описание": ["Магнит", "Такси"],
    }
    result = filter_transaction(mock_df_data).to_dict(orient="list")
    assert result == expected


def test_get_cards_info(mock_df_data):
    expected = [
        {"last_digits": "1234", "total_spent": 1000, "cashback": 10},
        {"last_digits": "5678", "total_spent": 2000, "cashback": 20},
    ]
    result = get_cards_info(mock_df_data)

    assert result == expected


def test_get_top5_transaction_info(mock_df_data):
    result = get_top5_transaction_info(mock_df_data)
    expected = [
        {
            "date": "2023-02-15",
            "amount": 2000,
            "category": "Транспорт",
            "description": "Такси",
        },
        {
            "date": "2023-01-01",
            "amount": 1000,
            "category": "Супермаркеты",
            "description": "Магнит",
        },
    ]
    assert result == expected


@patch("src.utils.pd.read_excel")
def test_get_df_data_from_file(mock_read):
    mock_read.return_value = {"test1": "test11"}
    result = get_df_data_from_file()
    assert result == {"test1": "test11"}


def test_get_df_data_from_file_error():
    assert get_df_data_from_file("incorrect_way.xlsx").to_dict() == pd.DataFrame().to_dict()


def test_cash_and_transfers_count():
    df_test = pd.DataFrame(
        {
            "Сумма платежа": [-1000, -2000, 3000, -500],
            "Статус": ["OK", "OK", "OK", "OK"],
            "Категория": ["Наличные", "Наличные", "Переводы", "Переводы"],
        }
    )
    expected = [
        {"category": "Наличные", "amount": 3000},
        {"category": "Переводы", "amount": 500},
    ]
    result = cash_and_transfers_count(df_test)
    assert result == expected


def test_most_spending_filter(mock_df_data):
    result = most_spending_filter(mock_df_data)
    expected = [{"category": "Транспорт", "amount": 2000}, {"category": "Супермаркеты", "amount": 1000}]
    assert result == expected


def test_get_income_category(mock_df_data):
    result = get_income_category(mock_df_data)
    expected = [{"category": "Каршеринг", "amount": 3000}]
    assert result == expected


@pytest.mark.parametrize(
    "date, data_range, expected",
    [
        (
            "2023-02-17",
            "W",
            {
                "Сумма платежа": [-2000],
                "Статус": [
                    "OK",
                ],
                "Категория": ["Транспорт"],
                "Дата платежа": ["15-02-2023"],
                "Номер карты": ["5678"],
                "Описание": ["Такси"],
            },
        ),
        (
            "2023-02-17",
            "M",
            {
                "Сумма платежа": [-2000],
                "Статус": [
                    "OK",
                ],
                "Категория": ["Транспорт"],
                "Дата платежа": ["15-02-2023"],
                "Номер карты": ["5678"],
                "Описание": ["Такси"],
            },
        ),
        (
            "2023-12-31",
            "Y",
            {
                "Сумма платежа": [-1000, -2000, 3000, -500],
                "Статус": ["OK", "OK", "OK", "FAILED"],
                "Категория": ["Супермаркеты", "Транспорт", "Каршеринг", "Переводы"],
                "Дата платежа": ["01-01-2023", "15-02-2023", "01-03-2023", "20-01-2023"],
                "Номер карты": ["1234", "5678", "1234", "5678"],
                "Описание": ["Магнит", "Такси", "Яндекс-Драйв", "Олег"],
            },
        ),
        (
            "2023-12-31",
            "ALL",
            {
                "Сумма платежа": [-1000, -2000, 3000, -500],
                "Статус": ["OK", "OK", "OK", "FAILED"],
                "Категория": ["Супермаркеты", "Транспорт", "Каршеринг", "Переводы"],
                "Дата платежа": ["01-01-2023", "15-02-2023", "01-03-2023", "20-01-2023"],
                "Номер карты": ["1234", "5678", "1234", "5678"],
                "Описание": ["Магнит", "Такси", "Яндекс-Драйв", "Олег"],
            },
        ),
    ],
)
def test_filter_data_by_range(date, data_range, expected, mock_df_data):
    result = filter_data_by_range(mock_df_data, date, data_range).to_dict(orient="list")
    assert result == expected
