from typing import Literal

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

exchange_rate = get_exchange_rate()
stock_price = get_stock_price()


def main_web(date: str, data: pd.DataFrame) -> dict:
    """Главная функция для веб-интерфейса."""
    result = {
        "greeting": get_greetings_by_time(),
        "cards": get_cards_info(data),
        "top_transactions": get_top5_transaction_info(data),
        "currency_rates": exchange_rate,  # заменить
        "stock_prices": stock_price,  # заменить
    }

    return result


def main_events(date: str, data: pd.DataFrame, data_range: Literal["W", "M", "Y", "ALL"] = "M") -> dict:
    """Главная функция для событий с возможностью фильтрации по периоду"""
    """W-неделя, M-месяц, Y-год, ALL-всё время"""
    df_by_time = filter_data_by_range(data, date, data_range)
    spending = filter_transaction(df_by_time)
    income = df_by_time[(df_by_time["Сумма платежа"] > 0) & (df_by_time["Статус"] != "FAILED")]

    result = {
        "expenses": {
            "total_amount": str(int(abs(spending["Сумма платежа"].sum()))),
            "main": most_spending_filter(spending),
            "transfers_and_cash": cash_and_transfers_count(spending),
        },
        "income": {"total_amount": str(int(abs(income["Сумма платежа"].sum()))), "main": get_income_category(income)},
        "currency_rates": exchange_rate,  # заменить
        "stock_prices": stock_price,  # заменить
    }

    return result


