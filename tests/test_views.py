import pytest
from unittest.mock import patch, Mock
from datetime import datetime
import pandas as pd

from src import views
from src.views import main_web, main_events




expected = {
        "greeting": 'Доброй ночи (мок успешен)',
        "cards": ['Карты и суммы расходов (мок успешен)'],
        "top_transactions": ['Топ 5 транзакций (мок успешен)'],
        "currency_rates": ['Курс валюты (мок успешен)'],
        "stock_prices": ['Курс акций (мок успешен)']
    }



@patch.object(views, 'stock_price', ['Курс акций (мок успешен)'])
@patch.object(views, 'exchange_rate', ['Курс валюты (мок успешен)'])
@patch('src.views.get_stock_price')
@patch('src.views.get_exchange_rate')
@patch('src.views.get_top5_transaction_info')
@patch('src.views.get_cards_info')
@patch('src.views.get_greetings_by_time')
def test_main_web(mock_greeting, mock_cards, mock_top5, mock_exchange, mock_stock):
    """Тест работоспособности"""
    mock_greeting.return_value = 'Доброй ночи (мок успешен)'
    mock_cards.return_value = ['Карты и суммы расходов (мок успешен)']
    mock_top5.return_value = ['Топ 5 транзакций (мок успешен)']
    mock_exchange.return_value = ['Курс валюты (мок успешен)']
    mock_stock.return_value = ['Курс акций (мок успешен)']

    assert main_web('YY-mm', 'df') == expected


