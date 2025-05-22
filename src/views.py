from typing import Literal
import logging

import pandas as pd

from src.utils import (
    cash_and_transfers_count,
    filter_data_by_range,
    filter_transaction,
    get_cards_info,
    get_exchange_rate,
    get_greetings_by_time,
    get_income_category,
    get_stock_price,
    get_top5_transaction_info,
    most_spending_filter
)

logging.basicConfig(level=logging.DEBUG,
                    filename='./logs/views.log',
                    filemode='w',
                    format='%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d -%H:%M:%S'
                    )
logger_web = logging.getLogger('main_web')
logger_events = logging.getLogger('main_events')

# logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler('./logs/views.log')
# logger.addHandler(file_handler)
# file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d: %(message)s')
# file_handler.setFormatter(file_formatter)

exchange_rate = get_exchange_rate()
stock_price = get_stock_price()


def main_web(date: str, data: pd.DataFrame) -> dict:
    """Главная функция для веб-интерфейса."""
    logger_web.info('Функция начинает работу')
    result = {
        "greeting": get_greetings_by_time(),
        "cards": get_cards_info(data),
        "top_transactions": get_top5_transaction_info(data),
        "currency_rates": exchange_rate,  # заменить
        "stock_prices": stock_price,  # заменить
    }
    logger_web.info('Функция завершила работу')
    return result


def main_events(date: str, data: pd.DataFrame, data_range: Literal["W", "M", "Y", "ALL"] = "M") -> dict:
    """Главная функция для событий с возможностью фильтрации по периоду"""
    """W-неделя, M-месяц, Y-год, ALL-всё время"""
    logger_events.info('Начало работы функции')
    logger_events.info('Отфильтровываем DF')
    df_by_time = filter_data_by_range(data, date, data_range)
    spending = filter_transaction(df_by_time)
    income = df_by_time[(df_by_time["Сумма платежа"] > 0) & (df_by_time["Статус"] != "FAILED")]

    logger_events.info('Получаем информацию')
    expenses_total_amount = str(int(abs(spending["Сумма платежа"].sum())))
    main_spending = most_spending_filter(spending)
    transfers_and_cash = cash_and_transfers_count(spending)
    income_total_amount = str(int(abs(income["Сумма платежа"].sum())))
    main_income = get_income_category(income)

    logger_events.info('Сохраняем в словарь')
    result = {
        "expenses": {
            "total_amount": expenses_total_amount,
            "main": main_spending,
            "transfers_and_cash": transfers_and_cash,
        },
        "income": {
            "total_amount": income_total_amount,
            "main": main_income
        },
        "currency_rates": exchange_rate,  # заменить
        "stock_prices": stock_price,  # заменить
    }

    logger_web.info('Функция завершила работу')
    return result
