import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas.core.interchange.dataframe_protocol import DataFrame

load_dotenv()

DATA_DIR = Path('./data')
SETTINGS_PATH = Path('./user_settings.json')
CBR_EXCHANGE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
AV_API_URL = "https://www.alphavantage.co/query"


def get_data_from_excel(file_name: str = 'operations.xlsx') -> list[dict]:
    """ Читает XLSX-файл и возвращает список словарей """
    file_path = DATA_DIR / file_name
    try:
        excel_data = pd.read_excel(file_path, engine='openpyxl')
        return excel_data.to_dict(orient='records')
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def get_greetings_by_time(current_date: datetime) -> str:
    """Возвращает приветствие, в зависимости от текущего времени"""

    current_hour = current_date.hour

    if 6 <= current_hour <= 11:
        greeting = 'Доброе утро'
    elif 12 <= current_hour <= 17:
        greeting = 'Добрый день'
    elif 18 <= current_hour <= 23:
        greeting = 'Добрый вечер'
    else:
        greeting = 'Доброй ночи'

    return greeting


# добавить обработку исключений
def convert_date_to_datetime(date: str) -> datetime:
    """Принимает дату в виде строки и возвращает эту строку в формате datetime"""

    result = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    return result


# придумать решение для повторной обработки запросов
def get_exchange_rate() -> list[dict]:
    """ Возвращает список словарей, с курсом валют указанных в файле user_settings.json """
    try:
        response = requests.get(CBR_EXCHANGE_URL).json()

        with open(SETTINGS_PATH, 'r') as file:
            user_settings_data = json.load(file)

        result = []
        for value in user_settings_data["user_currencies"]:
            data = {
                'currency': value,
                'rate': response["Valute"][value]["Value"]
            }
            result.append(data)

        return result
    except Exception as e:
        print(f"Ошибка получения курсов валют: {e}")
        return []


def get_stock_price() -> list[dict]:
    """ Возвращает список словарей, с курсом акций указанных в файле user_settings.json """
    api_key = os.getenv('AV_API_KEY')
    if not api_key:
        raise ValueError('API ключ не найден')

    try:
        with open(SETTINGS_PATH, 'r') as file:
            user_settings_data = json.load(file)
    except Exception as e:
        print(f'Ошибка чтения файла: {e}')
        return []

    result = []
    try:
        for stock in user_settings_data['user_stocks']:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': stock,
                'apikey': api_key
            }
            response = requests.get(AV_API_URL, params=params).json()
            date_list = list(response.get('Time Series (Daily)', {}).keys())
            data = response['Time Series (Daily)'][date_list[0]]["4. close"]
            result.append({"stock": stock, "price": data})
    except Exception as e:
        print(f'Ошибка: {e}]')

    return result


def filter_transaction(df: pd.DataFrame) -> DataFrame:
    result = df[(df['Сумма операции'] < 0) & (df['Статус'] != 'FAILED')]
    return result


def get_cards_info(df: pd.DataFrame) -> list[dict]:
    """Принимает имя файла в папке ..data/ и возвращает список словарей с каждой картой в файле, суммой транзакций
    и кэшбэком по этой карте"""
    spending = filter_transaction(df)
    sum_info = spending.groupby('Номер карты')['Сумма операции'].sum()

    result = []
    for key, value in sum_info.items():
        result.append(
            {
                "last_digits": key[-4:],
                "total_spent": abs(value),
                "cashback": abs(round(value / 100, 2))
            }
        )
    return result


def get_top5_transaction_info(df):
    """Возвращает топ-5 транзакций по сумме платежа"""
    only_spending = filter_transaction(df)
    sorted_df = only_spending.nsmallest(5, 'Сумма операции')

    result = []
    for _, row in sorted_df.iterrows():
        result.append({
            "date": row['Дата платежа'][:11],
            "amount": abs(row['Сумма операции']),
            "category": row['Категория'],
            "description": row['Описание']
        })

    return result


def get_df_data_from_file(file_name: str = 'operations.xlsx') -> DataFrame:
    """Принимает имя файла в папке /data и возвращает DataFrame объект"""
    return pd.read_excel(DATA_DIR / file_name, engine='openpyxl')


def cash_and_transfers_count(df: pd.DataFrame) -> list[dict]:
    """Считает расходы наличными и переводы"""
    spending = filter_transaction(df)

    cash_only = spending[spending['Категория'] == 'Наличные']
    transfers_only = spending[spending['Категория'] == 'Переводы']
    result = [
        {
            "category": "Наличные",
            "amount": round(abs(cash_only['Сумма операции'].sum()))
        },
        {
            "category": "Переводы",
            "amount": round(abs(transfers_only['Сумма операции'].sum()))
        }
    ]
    return result


def most_spending_filter(df):
    spending = filter_transaction(df)
    category_spending = spending.groupby('Категория')['Сумма операции'].sum().abs()
    sorted_category = category_spending.sort_values(ascending=False)
    top7 = sorted_category.head(7)

    result = [{"category": category, "amount": amount} for category, amount in top7.items()]

    if len(sorted_category[7:]) != 0:
        other_categories = {"category": "Остальное", "amount": str(sorted_category[7:].sum())}
        result.append(other_categories)

    return result

if __name__ == '__main__':
    # print(get_cards_info(get_df_data_from_file('operations.xlsx')))
    print(most_spending_filter(get_df_data_from_file('operations.xlsx')))
    # print(get_cards_info())
    # get_top5_transaction_info()
