from src.utils import get_greetings_by_time, get_exchange_rate, get_stock_price, get_cards_info, \
    get_top_transaction_info

def return_df_from_file():
    pass


def web_main():
    result = {"greeting": get_greetings_by_time(),
              "cards": get_cards_info(),
              "top_transactions": get_top_transaction_info(),
              "currency_rates": get_exchange_rate(),
              "stock_prices": get_stock_price(),
              }

    return result


print(web_main())
