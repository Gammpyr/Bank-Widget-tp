import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import CBR_EXCHANGE_URL

load_dotenv()


def get_data_from_excel(file_name: str) -> list[dict]:
    """ Принимает имя XLSX-файла и возвращает список словарей с содержимым """

    try:
        excel_data = pd.read_excel(f'../data/{file_name}', engine='openpyxl')
        json_str = excel_data.to_dict(orient='records')
    except FileNotFoundError:
        json_str = None
        print("Файл не найден")
    except Exception as e:
        json_str = None
        print(f"Произошла ошибка: {e}")

    return json_str


def get_greetings_by_time() -> str:
    """Возвращает приветствие, в зависимости отт текущего времени"""

    current_hour = datetime.now().hour

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
        data = response['Time Series (Daily)'][list(response['Time Series (Daily)'].keys())[0]]["4. close"]
        result.append({"stock": ticker_symbol, "price": data})

    return result


if __name__ == '__main__':
    print(get_greetings_by_time())
    print(convert_time_to_datetime('2021-07-14 22:07:40'))

