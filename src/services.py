from datetime import datetime
from typing import Any

import pandas as pd

from src.utils import filter_transaction


def get_high_cashback_categories(data: pd.DataFrame, year: int, month: int) -> Any:
    """Функция позволяет проанализировать, какие категории были наиболее выгодными для выбора
    в качестве категорий повышенного кэшбэка."""
    """
        Входные параметры:
        data — данные с транзакциями;
        year — год, за который проводится анализ;
        month — месяц, за который проводится анализ.
        На выходе — JSON с анализом, сколько на каждой категории можно заработать кэшбэка в указанном месяце года.
    """
    filtered_data = filter_transaction(data)
    df = filtered_data.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    filtered_by_time = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]

    grouped_data = filtered_by_time.groupby("Категория")["Сумма платежа"].sum().abs()
    sorted_data = grouped_data.sort_values(ascending=False)
    cashback_data = (sorted_data / 100).astype(int)
    result = cashback_data[(cashback_data > 0) & (~cashback_data.index.isin(["Переводы", "Наличные"]))]
    return result.to_dict()


def investment_bank(month: str, transactions: list[dict], limit: int) -> Any:
    """Возвращает сумму, которую удалось бы отложить в «Инвесткопилку»"""
    """
    month — месяц, для которого рассчитывается отложенная сумма (строка в формате 'YYYY-MM').
    transactions — список словарей, содержащий информацию о транзакциях, в которых содержатся следующие поля:
        Дата операции — дата, когда произошла транзакция (строка в формате 'YYYY-MM-DD').
        Сумма операции — сумма транзакции в оригинальной валюте (число).
    limit — предел, до которого нужно округлять суммы операций (целое число).
    """
    target_month = datetime.strptime(month, "%Y-%m")

    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])
    filtered_df = df[(df["date"].dt.month == target_month.month) & (df["date"].dt.year == target_month.year)]

    remainder = abs(filtered_df["amount"]) % limit
    result = remainder[remainder != 0].apply(lambda x: limit - x).sum()
    return int(result)
