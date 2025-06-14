from unittest.mock import patch

import pandas as pd

from src import views
from src.views import main_events, main_web


@patch.object(views, "stock_price", ["Курс акций (мок успешен)"])
@patch.object(views, "exchange_rate", ["Курс валюты (мок успешен)"])
@patch("src.views.get_stock_price")
@patch("src.views.get_exchange_rate")
@patch("src.views.get_top5_transaction_info")
@patch("src.views.get_cards_info")
@patch("src.views.get_greetings_by_time")
def test_main_web(mock_greeting, mock_cards, mock_top5, mock_exchange, mock_stock):
    """Тест работоспособности"""
    expected = {
        "greeting": "Доброй ночи (мок успешен)",
        "cards": ["Карты и суммы расходов (мок успешен)"],
        "top_transactions": ["Топ 5 транзакций (мок успешен)"],
        "currency_rates": ["Курс валюты (мок успешен)"],
        "stock_prices": ["Курс акций (мок успешен)"],
    }
    mock_greeting.return_value = "Доброй ночи (мок успешен)"
    mock_cards.return_value = ["Карты и суммы расходов (мок успешен)"]
    mock_top5.return_value = ["Топ 5 транзакций (мок успешен)"]
    mock_exchange.return_value = ["Курс валюты (мок успешен)"]
    mock_stock.return_value = ["Курс акций (мок успешен)"]

    assert main_web("YY-mm", "df") == expected


@patch.object(views, "stock_price", ["Курс акций (мок успешен)"])
@patch.object(views, "exchange_rate", ["Курс валюты (мок успешен)"])
@patch("src.views.get_stock_price")
@patch("src.views.get_exchange_rate")
@patch("src.views.most_spending_filter")
@patch("src.views.filter_transaction")
@patch("src.views.filter_data_by_range")
def test_main_events(mock_range, mock_transactions, mock_spending, mock_exchange, mock_stock, mock_df_data):
    mock_range.return_value = mock_df_data
    mock_transactions.return_value = pd.DataFrame(
        {
            "Сумма платежа": [
                -1000,
                -2000,
            ],
            "Статус": [
                "OK",
                "OK",
            ],
            "Категория": [
                "Наличные",
                "Транспорт",
            ],
            "Дата платежа": [
                "01-01-2023",
                "15-02-2023",
            ],
            "Номер карты": [
                "1234",
                "5678",
            ],
            "Описание": [
                "Магнит",
                "Такси",
            ],
        }
    )
    mock_spending.return_value = [{"category": "Транспорт", "amount": 2000}, {"category": "Наличные", "amount": 1000}]
    mock_exchange.return_value = ["Курс валюты (мок успешен)"]
    mock_stock.return_value = ["Курс акций (мок успешен)"]

    main_test = [{"category": "Транспорт", "amount": 2000}, {"category": "Наличные", "amount": 1000}]
    transfers_and_cash = [
        {"category": "Наличные", "amount": 1000},
        {"category": "Переводы", "amount": 0},
    ]
    expected = {
        "expenses": {
            "total_amount": "3000",
            "main": main_test,
            "transfers_and_cash": transfers_and_cash,
        },
        "income": {"total_amount": "3000", "main": [{"category": "Каршеринг", "amount": 3000}]},
        "currency_rates": ["Курс валюты (мок успешен)"],  # заменить
        "stock_prices": ["Курс акций (мок успешен)"],  # заменить
    }
    assert main_events("YYYY", "df") == expected
