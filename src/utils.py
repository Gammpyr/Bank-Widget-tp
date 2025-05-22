import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path("./data")
SETTINGS_PATH = Path("./user_settings.json")
CBR_EXCHANGE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
AV_API_URL = "https://www.alphavantage.co/query"


def get_data_from_excel(file_name: str = "operations.xlsx") -> list[dict]:
    """Читает XLSX-файл и возвращает список словарей"""
    file_path = DATA_DIR / file_name
    try:
        excel_data = pd.read_excel(file_path, engine="openpyxl")
        return excel_data.to_dict(orient="records")
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return []


def get_greetings_by_time() -> str:
    """Возвращает приветствие, в зависимости от текущего времени"""
    datetime.now()
    current_date = datetime.now()
    current_hour = current_date.hour

    if 6 <= current_hour <= 11:
        greeting = "Доброе утро"
    elif 12 <= current_hour <= 17:
        greeting = "Добрый день"
    elif 18 <= current_hour <= 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    return greeting


# добавить обработку исключений
def convert_date_to_datetime(date: str) -> datetime:
    """Принимает дату в виде строки и возвращает эту строку в формате datetime"""

    result = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    return result


# придумать решение для повторной обработки запросов
def get_exchange_rate() -> list[dict] | str:
    """Возвращает список словарей, с курсом валют указанных в файле user_settings.json"""
    try:
        response = requests.get(CBR_EXCHANGE_URL).json()

        with open(SETTINGS_PATH, "r") as file:
            user_settings_data = json.load(file)

        result = []
        for value in user_settings_data["user_currencies"]:
            data = {"currency": value, "rate": response["Valute"][value]["Value"]}
            result.append(data)

        return result
    except Exception as e:
        return f"Ошибка обработки файла: {e}"


def get_stock_price() -> list[dict]:
    """Возвращает список словарей, с курсом акций указанных в файле user_settings.json"""
    api_key = os.getenv("AV_API_KEY")
    if not api_key:
        raise ValueError("API ключ не найден")

    try:
        with open(SETTINGS_PATH, "r") as file:
            user_settings_data = json.load(file)
    except FileNotFoundError as e:
        return []

    result = []
    try:
        for stock in user_settings_data["user_stocks"]:
            params = {"function": "TIME_SERIES_DAILY", "symbol": stock, "apikey": api_key}
            response = requests.get(AV_API_URL, params=params).json()
            date_list = list(response.get("Time Series (Daily)", {}).keys())
            data = response["Time Series (Daily)"][date_list[0]]["4. close"]
            result.append({"stock": stock, "price": float(data)})
    except requests.exceptions.RequestException as e:
        print(f"Ошибка: {e}")
    except KeyError as e:
        print(f"Ключ не найден: {e}")

    return result


def filter_transaction(df: pd.DataFrame) -> pd.DataFrame:
    """Фильтрует DF, оставляя только выполненные операции с расходами"""
    result = df[(df["Сумма платежа"] < 0) & (df["Статус"] == "OK")]
    return result


def get_cards_info(df: pd.DataFrame) -> list[dict]:
    """Принимает имя файла в папке ..data/ и возвращает список словарей с каждой картой в файле, суммой транзакций
    и кэшбэком по этой карте"""
    spending = filter_transaction(df)
    sum_info = spending.groupby("Номер карты")["Сумма платежа"].sum()

    result = []
    for key, value in sum_info.items():
        result.append({"last_digits": key[-4:],
                       "total_spent": abs(value),
                       "cashback": abs(round(value / 100, 2))})
    return result


def get_top5_transaction_info(df: pd.DataFrame) -> list[dict]:
    """Возвращает топ-5 транзакций по сумме платежа"""
    only_spending = filter_transaction(df)
    sorted_df = only_spending.nsmallest(5, "Сумма платежа")

    result = []
    for _, row in sorted_df.iterrows():
        result.append(
            {
                "date": row["Дата платежа"][:11],
                "amount": abs(row["Сумма платежа"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    return result


def get_df_data_from_file(file_name: str = "operations.xlsx") -> pd.DataFrame:
    """Принимает имя файла в папке /data и возвращает DataFrame объект"""
    return pd.read_excel(DATA_DIR / file_name, engine="openpyxl")


def cash_and_transfers_count(df: pd.DataFrame) -> list[dict]:
    """Считает расходы наличными и переводы"""
    spending = filter_transaction(df)

    cash_only = spending[spending["Категория"] == "Наличные"]
    transfers_only = spending[spending["Категория"] == "Переводы"]
    result = [
        {"category": "Наличные", "amount": round(abs(cash_only["Сумма платежа"].sum()))},
        {"category": "Переводы", "amount": round(abs(transfers_only["Сумма платежа"].sum()))},
    ]
    return result


def most_spending_filter(df: pd.DataFrame) -> list[dict]:
    """Принимает DF и возвращает список словарей с 7 самыми популярными категориями"""
    spending = filter_transaction(df)
    category_spending = spending.groupby("Категория")["Сумма платежа"].sum().abs()
    sorted_category = category_spending.sort_values(ascending=False)
    top7 = sorted_category.head(7)

    result = [{"category": category, "amount": amount} for category, amount in top7.items()]

    if len(sorted_category[7:]) != 0:
        other_categories = {"category": "Остальное", "amount": sorted_category[7:].sum()}
        result.append(other_categories)

    return result


def get_income_category(df: pd.DataFrame) -> list[dict]:
    """Принимает DF и возвращает список словарей с суммами поступлений"""
    income_df = df[(df["Сумма платежа"] > 0) & (df["Статус"] == "OK")]
    category_income = income_df.groupby("Категория")["Сумма платежа"].sum()
    sorted_category = category_income.sort_values(ascending=False)

    result = [{"category": category, "amount": amount} for category, amount in sorted_category.items()]

    return result


def filter_data_by_range(data: pd.DataFrame, date: str, data_range: str = "M") -> pd.DataFrame:
    """Фильтрует DF по указанной дате"""
    current_date = datetime.strptime(date, "%Y-%m-%d")
    data["Дата платежа"] = pd.to_datetime(data["Дата платежа"])

    if data_range == "W":
        start_date = current_date - timedelta(days=current_date.weekday())
    elif data_range == "M":
        start_date = current_date.replace(day=1)
    elif data_range == "Y":
        start_date = current_date.replace(month=1, day=1)
    else:
        result = data[(data["Дата платежа"] <= current_date)]
        result["Дата платежа"] = result["Дата платежа"].dt.strftime("%d-%m-%Y")
        return result

    result = data[(data["Дата платежа"] >= start_date) & (data["Дата платежа"] <= current_date)]
    result["Дата платежа"] = result["Дата платежа"].dt.strftime("%d-%m-%Y")
    return result



# if __name__ == "__main__":
#     data = get_df_data_from_file("operations.xlsx")
#     # print(get_cards_info(data))
#     # print(most_spending_filter(data))
#     # print(get_income_category(data))
#     # print(get_cards_info())
#     # get_top5_transaction_info()
#     print(filter_data_by_range(data, "2021-05-22", "ALL"))
#     print(get_greetings_by_time())
