import json

from src.utils import get_greetings_by_time, get_exchange_rate, get_stock_price, get_cards_info, \
    get_top_transaction_info

def return_df_from_file():
    pass


def web_main(time: str):
    result = {"greeting": get_greetings_by_time(),
              "cards": get_cards_info(),
              "top_transactions": get_top_transaction_info(),
              "currency_rates": get_exchange_rate(),
              "stock_prices": get_stock_price(),
              }

    return result

with open('returned_data.json', 'w', encoding='utf-8') as file:
    json.dump(web_main('YYYY-MM-DD HH:MM:SS'), file, ensure_ascii=False, indent=4 )
# print(web_main())
