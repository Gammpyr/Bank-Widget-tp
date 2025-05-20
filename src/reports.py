import json
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import filter_transaction, get_df_data_from_file


def report_to_selected_file(filename: str = "report_file.txt") -> Any:
    """Записывает данные отчета в файл с указанным названием"""

    def decorator(func: Callable) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            filepath = os.path.join("reports", filename)

            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
            return result

        return wrapper

    return decorator


def get_spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Any:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    Если дата не передана, то берется текущая дата."""
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%d-%m-%Y")

    start_date = end_date - timedelta(days=90)

    filtered_df = filter_transaction(transactions)
    filtered_df = filtered_df.copy()

    filtered_df["Дата операции"] = pd.to_datetime(filtered_df["Дата операции"], dayfirst=True)

    category_df = filtered_df[
        (filtered_df["Категория"] == category)
        & (filtered_df["Дата операции"] >= start_date)
        & (filtered_df["Дата операции"] <= end_date)
        ]

    grouped_df = category_df.groupby("Описание")["Сумма платежа"].sum()
    result_df = grouped_df.sort_values().abs()

    return result_df.to_dict()
