import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import filter_transaction

logging.basicConfig(
    level=logging.DEBUG,
    filename="./logs/reports.log",
    encoding="utf-8",
    filemode="w",
    format="%(asctime)s %(levelname)s %(funcName)s %(lineno)d: %(message)s",
    datefmt="%Y-%m-%d -%H:%M:%S",
)

logger = logging.getLogger()


def report_to_selected_file(filename: str = "report_file.txt") -> Any:
    """Записывает данные отчета в файл с указанным названием
    :rtype: Any
    """
    logger.info("Запускаем декоратор report_to_selected_file")

    def decorator(func: Callable) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"Запускаем функцию {func}")
            result = func(*args, **kwargs)
            filepath = os.path.join("reports", filename)

            logger.info(f"Записываем отчёт в файл {filename}")
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
            logger.info("Завершаем работу декоратора")
            return result

        return wrapper

    return decorator


def get_spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Any:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    Если дата не передана, то берется текущая дата."""
    logger.info("Запускаем функцию get_spending_by_category")
    if date is None:
        logger.info("Дата не указана, берём текущее время")
        end_date = datetime.now()
    else:
        logger.info("Переводим строку даты в формат DateTime")
        end_date = datetime.strptime(date, "%d-%m-%Y")

    start_date = end_date - timedelta(days=90)

    logger.info("Фильтруем DF по расходам")
    filtered_df = filter_transaction(transactions)
    filtered_df = filtered_df.copy()

    logger.info('Переводим "Дату операции" в DF в формат DateTime')
    filtered_df["Дата операции"] = pd.to_datetime(filtered_df["Дата операции"], dayfirst=True)

    logger.info("Фильтруем DF по категории и дате")
    category_df = filtered_df[
        (filtered_df["Категория"] == category)
        & (filtered_df["Дата операции"] >= start_date)
        & (filtered_df["Дата операции"] <= end_date)
    ]

    grouped_df = category_df.groupby("Описание")["Сумма платежа"].sum()
    result_df = grouped_df.sort_values().abs().round(2)
    logger.info("Функция get_spending_by_category завершает работу")
    return result_df.to_dict()
