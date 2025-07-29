import os
import pandas as pd
from tqdm import tqdm
from functools import partial
from shining_pebbles import get_date_range, get_today, load_json_in_file_folder_by_regex
from string_date_controller import get_date_n_days_after
from .basis.utils import parse_datetime
from .composed import recurse_price, insert_price
from .consts import TICKER_BBG_MSCI_KR, TICKER_BBG_MSCI_KR_USD, FILE_FOLDER_BBG


format_file_name = lambda ticker_bbg, fld: f'data-bbg-ticker_bbg{ticker_bbg}-fld{fld}.csv'

def save_data_as_json(data, file_folder, file_name):
    df = pd.DataFrame(data)
    df.to_json(
        os.path.join(file_folder, file_name),
        orient='records',
        date_format='iso',
        indent=4
    )
    print(f"| Saved json to {os.path.join(file_folder, file_name)}")

def save_bbg_data(data, ticker_bbg, fld):
    save_data_as_json(data=data, file_folder=FILE_FOLDER_BBG, file_name=format_file_name(ticker_bbg, fld))

def load_bbg_data(fld, ticker_bbg):
    regex = format_file_name(ticker_bbg=ticker_bbg, fld=fld)
    data = load_json_in_file_folder_by_regex(file_folder=FILE_FOLDER_BBG, regex=regex)
    return list(map(parse_datetime, data))

def recurse_and_parse_and_insert_bbg_price(ticker_bbg, date_from):
    dates = get_date_range(start_date_str=date_from, end_date_str=get_today())
    for date in tqdm(dates):
        datum = recurse_price(ticker_bbg=ticker_bbg, date_ref=date)
        insert_price(datum)

def recurse_and_insert_price(ticker_bbg, date_ref):
    datum = recurse_price(ticker_bbg, date_ref)
    insert_price(datum)
    print('inserted.')

recurse_and_insert_mxkr = partial(recurse_and_insert_price, ticker_bbg=TICKER_BBG_MSCI_KR)
recurse_and_insert_m1kr = partial(recurse_and_insert_price, ticker_bbg=TICKER_BBG_MSCI_KR_USD)


def recurese_squared(ticker_bbg, date_ref, i=0):
    try:
        date_ref = get_date_n_days_after(date_ref, i)
        print('|- process:', ticker_bbg, date_ref)
        recurse_and_parse_and_insert_bbg_price(ticker_bbg=ticker_bbg, date_from=date_ref)
    except:
        recurese_squared(ticker_bbg, date_ref, i=i+1)
    
