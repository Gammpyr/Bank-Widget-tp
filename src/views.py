import json
from datetime import datetime

from pandas.core.interchange.dataframe_protocol import DataFrame

from src.utils import (
    get_greetings_by_time,
    get_exchange_rate,
    get_stock_price,
    get_cards_info,
    get_top5_transaction_info,
    get_df_data_from_file,
    cash_and_transfers_count
)


def main_web(date: str, data: DataFrame):
    """Главная функция для веб-интерфейса."""
    result = {
        "greeting": get_greetings_by_time(date),
        "cards": get_cards_info(data),
        "top_transactions": get_top5_transaction_info(data),
        "currency_rates": get_exchange_rate(),  # заменить
        "stock_prices": get_stock_price(),  # заменить
    }

    return result


def main_events(date, data: DataFrame, data_range: ['W', 'M', 'Y', 'ALL']='M') -> dict:
    """Главная функция для событий с возможностью фильтрации по периоду"""
    # W-неделя, M-месяц, Y-год, ALL-всё время
    spending = df[(df['Сумма операции'] < 0) & (df['Статус'] != 'FAILED')]
    income = df[(df['Сумма операции'] > 0) & (df['Статус'] != 'FAILED')]

    result = {
        "expenses":
            {
                "total_amount": str(int(abs(spending['Сумма операции'].sum()))),
                "main": [{None}],
                "transfers_and_cash": cash_and_transfers_count(df)
            },
        "income":
            {
                "total_amount": str(int(abs(income['Сумма операции'].sum()))),
                "main": [{None}]
            },
        "currency_rates": None,  # get_exchange_rate(), # заменить
        "stock_prices": None  # get_stock_price() # заменить
    }

    return result


def filter_data_by_range(data: DataFrame, date: str, data_range: str) -> DataFrame:
    #Написать функцию сортировки DF по указанной дате
    pass



if __name__ == '__main__':
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = get_df_data_from_file('operations.xlsx')

    main_web_data = main_web(current_date, df)
    main_events_data = main_events(current_date, df, 'M')

    # with open('returned_data.json', 'w', encoding='utf-8') as file:
    #     json.dump(main_web_data, file, ensure_ascii=False, indent=4 )

    # print(main_web_data)
    print(main_events_data)
