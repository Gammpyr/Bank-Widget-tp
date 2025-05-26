import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.reports import get_spending_by_category
from src.services import get_high_cashback_categories, investment_bank
from src.utils import get_df_data_from_file
from src.views import main_events, main_web

logging.basicConfig(
    level=logging.DEBUG,
    filename="./logs/main.log",
    encoding="utf-8",
    filemode="w",
    format="%(asctime)s %(levelname)s %(funcName)s %(lineno)d: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


def main(df: pd.DataFrame, current_date: str, transactions: list[dict]) -> None:
    """Главная функция, сохраняет в BankWidget.json"""
    logger.info("Функция main начинает работу")

    # Главная функция для веб-интерфейса.
    logger.info("Получаем информацию из main_web")
    main_web_data = main_web(current_date, df)

    # Главная функция для событий с возможностью фильтрации по периоду
    logger.info("Получаем информацию из main_events")
    main_events_data = main_events("2021-12-31", df, "M")

    # Наиболее выгодные для кэшбэка категории
    logger.info("Получаем информацию из high_cashback_categories")
    high_cashback_categories = get_high_cashback_categories(data=df, year=2018, month=2)

    # Возвращает сумму, которую удалось бы отложить в «Инвесткопилку» -> int
    logger.info("Получаем информацию из investment_bank")
    cashback = investment_bank("2025-05", transactions=transactions, limit=20)

    # Возвращает траты по заданной категории за последние три месяца (от переданной даты)
    logger.info("Получаем информацию из get_spending_by_category")
    spending_by_category = get_spending_by_category(df, "Супермаркеты", "19-11-2021")

    result = {
        "web_pages": {"main_web_data": main_web_data, "main_events_data": main_events_data},
        "services": {"high_cashback_categories": high_cashback_categories, "investment_bank": cashback},
        "reports": {"spending_by_category": spending_by_category},
    }

    filename = Path("./BankWidget.json")
    data_dir = Path("./data")
    path_to_file = data_dir / filename

    logger.info(f"Сохраняем результат в файл {path_to_file}")
    with open(path_to_file, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
    logger.info("Функция main завершает работу")


if __name__ == "__main__":
    transactions_list = [
        {"date": "2025-05-14", "amount": -68},
        {"date": "2025-05-14", "amount": -44},
        {"date": "2025-04-13", "amount": 3300},
        {"date": "2025-03-22", "amount": 4400},
    ]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = get_df_data_from_file("operations.xlsx")

    main(data, date, transactions_list)
