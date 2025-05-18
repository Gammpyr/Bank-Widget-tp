import json
from datetime import datetime

import pandas as pd

from utils import get_df_data_from_file
from reports import get_spending_by_category
from services import get_high_cashback_categories, investment_bank
from views import main_events, main_web


def main(df: pd.DataFrame, current_date: str, transactions: list[dict]) -> None:
    """Главная функция, сохраняет в BankWidget.json"""
    # Главная функция для веб-интерфейса.
    main_web_data = main_web(current_date, df)

    # Главная функция для событий с возможностью фильтрации по периоду
    main_events_data = main_events("2021-12-31", df, "M")

    # Наиболее выгодные для кэшбэка категории
    high_cashback_categories = get_high_cashback_categories(data=df, year=2018, month=2)

    # Возвращает сумму, которую удалось бы отложить в «Инвесткопилку» -> int
    cashback = investment_bank("2025-05", transactions=transactions, limit=20)

    # Возвращает траты по заданной категории за последние три месяца (от переданной даты)
    spending_by_category = get_spending_by_category(df, "Супермаркеты", "19-11-2021")

    result = {
        "web_pages": {"main_web_data": main_web_data, "main_events_data": main_events_data},
        "services": {"high_cashback_categories": high_cashback_categories, "investment_bank": cashback},
        "reports": {"spending_by_category": spending_by_category}
    }

    with open("BankWidget.json", "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    transactions_list = [
        {"date": "2025-05-14", "amount": -68},
        {"date": "2025-05-14", "amount": -44},
        {"date": "2025-04-13", "amount": 3300},
        {"date": "2025-03-22", "amount": 4400},
    ]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = get_df_data_from_file("operations.xlsx")

    main(data, date, transactions_list)
