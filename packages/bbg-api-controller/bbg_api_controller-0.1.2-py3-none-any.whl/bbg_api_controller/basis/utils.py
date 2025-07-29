from datetime import datetime
from typing import Dict, Any
from string_date_controller import get_date_n_days_ago

generate_date_sequence = lambda date_to, n: [get_date_n_days_ago(date_to, i) for i in range(n)]

def parse_bbg_data(date_ref, data):
    ticker_bbg, fld = list(data[0].keys())[-1]
    datetime, value = list(data[0].values())
    dct = {
        'date_ref': date_ref,
        'ticker_bbg': ticker_bbg,
        'fld': fld,
        'datetime': datetime,
        'value': value
    }
    return dct

def parse_datetime(datum: Dict[str, Any], field: str = 'datetime') -> Dict[str, Any]:
    return {
        **datum,
        field: datetime.fromisoformat(datum[field]) if field in datum else datum.get(field)
    }

def insert_datum(collection, datum):
    collection.insert_one(datum)
