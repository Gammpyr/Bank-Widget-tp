import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import CBR_EXCHANGE_URL

load_dotenv()


def get_data_from_excel(file_name: str = 'operations.xlsx') -> list[dict]:
    """ Принимает имя XLSX-файла и возвращает список словарей с содержимым """

    try:
        excel_data = pd.read_excel(f'../data/{file_name}', engine='openpyxl')
        return excel_data.to_dict(orient='records')
    except FileNotFoundError:
        print("Файл не найден: ../data/{file_name}")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def get_greetings_by_time() -> str:
    """Возвращает приветствие, в зависимости отт текущего времени"""

    current_date = datetime.now()
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


def convert_time_to_datetime(date: str) -> datetime:
    """Принимает дату в виде строки и возвращает эту строку в формате datetime"""

    result = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    return result


def get_exchange_rate() -> list[dict]:
    """ Возвращает список словарей, с курсом валют указанных в файле user_settings.json """
    response = requests.get(CBR_EXCHANGE_URL).json()

    with open('../user_settings.json', 'r') as file:
        user_settings_data = json.load(file)

    result = []
    for value in user_settings_data["user_currencies"]:
        data = {
            'currency': value,
            'rate': response["Valute"][value]["Value"]
        }
        result.append(data)

    return result


def get_stock_price() -> list[dict]:
    """ Возвращает список словарей, с курсом акций указанных в файле user_settings.json """
    AV_API_KEY = os.getenv('AV_API_KEY')

    with open('../user_settings.json', 'r') as file:
        user_settings_data = json.load(file)

    result = []

    for stock in user_settings_data['user_stocks']:
        ticker_symbol = stock

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker_symbol}&apikey={AV_API_KEY}'
        response = requests.get(url).json()
        if 'Time Series (Daily)' in response:
            data = response['Time Series (Daily)'][list(response['Time Series (Daily)'].keys())[0]]["4. close"]
            result.append({"stock": ticker_symbol, "price": data})
        else:
            print("Ошибка запроса")
            break

    return result


def get_cards_info(file_name: str = 'operations.xlsx') -> list[dict]:
    """Принимает имя файла в папке ..data/ и возвращает список словарей с каждой картой в файле, суммой транзакций
    и кэшбэком по этой карте"""
    df = pd.read_excel(f'../data/{file_name}', engine='openpyxl')
    filtered_df = df[df['Сумма операции'] < 0]
    summ_info = filtered_df.groupby('Номер карты')['Сумма операции'].sum().to_dict()

    result = []
    for key, value in summ_info.items():
        result.append(
            {
                "last_digits": key[-4:],
                "total_spent": abs(value),
                "cashback": abs(round(value / 100, 2))
            }
        )
    return result


def get_top_transaction_info(file_name: str = 'operations.xlsx'):
    """Возвращает топ-5 транзакций, по сумме платежа, из указанного файла"""
    df = pd.read_excel(f'./data/{file_name}', engine='openpyxl')
    only_spending = df[df['Сумма операции'] < 0]
    sorted_df = only_spending.sort_values('Сумма операции')
    print(sorted_df.)
    # print(sorted_df['Дата'].head())
    # print(sorted_df['Сумма операции'].head())
    # print(sorted_df['Категория'].head())
    # print(sorted_df['Описание'].head())


    # students_df_with_nan.loc[2, 'Оценка'] = None



if __name__ == '__main__':
    # print(get_cards_info())
    get_top_transaction_info()