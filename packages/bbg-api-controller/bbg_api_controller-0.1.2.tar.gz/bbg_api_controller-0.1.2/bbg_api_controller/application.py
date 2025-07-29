from string_date_controller import get_today
from .basis import generate_date_sequence
from .utils import recurse_and_insert_price


def fetch_and_insert_bbg_price(ticker_bbg, date_to=get_today(), n=100):
    for date in generate_date_sequence(date_to=date_to, n=n):
        try:
            recurse_and_insert_price(ticker_bbg, date)
            print(f'insert: {ticker_bbg}, {date}')
        except Exception as e:
            print(f'fail: {ticker_bbg}, {date}')
            print(e)
            pass

