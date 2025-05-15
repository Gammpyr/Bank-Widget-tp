from datetime import datetime
from typing import Any

import pandas as pd

from utils import get_df_data_from_file, filter_transaction


def get_high_cashback_categories(data: pd.DataFrame, year: int, month: int) -> dict:
    """Функция позволяет проанализировать, какие категории были наиболее выгодными для выбора
    в качестве категорий повышенного кешбэка."""
    """
        Входные параметры:
        data — данные с транзакциями;
        year — год, за который проводится анализ;
        month — месяц, за который проводится анализ.
        На выходе — JSON с анализом, сколько на каждой категории можно заработать кешбэка в указанном месяце года.
    """
    filtered_data = filter_transaction(data)

    filtered_data['Дата операции'] = pd.to_datetime(filtered_data['Дата операции'])
    filtered_by_time = filtered_data[
        (filtered_data['Дата операции'].dt.year == year) & (filtered_data['Дата операции'].dt.month == month)
        ]

    grouped_data = filtered_by_time.groupby('Категория')['Сумма платежа'].sum().abs()
    sorted_data = grouped_data.sort_values(ascending=False)
    cashback_data = (sorted_data / 100).astype(int)
    result = cashback_data[(cashback_data > 0) & (~cashback_data.index.isin(['Переводы', 'Наличные']))]
    return result.to_dict()



def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    pass


if __name__ == '__main__':
    print(get_high_cashback_categories(data=get_df_data_from_file(), year=2021, month=5))
