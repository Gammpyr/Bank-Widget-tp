from datetime import datetime

import pandas as pd


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


if __name__ == '__main__':
    print(get_greetings_by_time())
    print(convert_time_to_datetime('2021-07-14 22:07:40'))
