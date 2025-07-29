from functools import partial
from canonical_transformer import map_df_to_data
from .connector import BCON
from .functionals import pipe
from .utils import parse_bbg_data, generate_date_sequence

def fetch_bbg_data(ticker_bbg, date_ref, fld, bcon=BCON):
    df = bcon.bdh(
        tickers=[ticker_bbg], 
        flds=[fld], 
        start_date=date_ref.replace("-", ""), 
        end_date=date_ref.replace("-", "")
    )
    data = map_df_to_data(df)
    return data

def recurse_bbg_data(dates, fetch_kernel, ticker_bbg):
    for date in dates:
        try:
            result = fetch_kernel(ticker_bbg, date)
            if result:
                return result
        except:
            continue
    return None


def recurse_bdh(date_ref, fld, n=30, bcon=BCON):
    dates = generate_date_sequence(date_ref, n)
    fetch = partial(fetch_bbg_data, fld=fld, bcon=bcon)
    recurse = partial(recurse_bbg_data, dates)
    parse = partial(parse_bbg_data, date_ref)
    return pipe(
        fetch,
        recurse,
        parse
    )