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
