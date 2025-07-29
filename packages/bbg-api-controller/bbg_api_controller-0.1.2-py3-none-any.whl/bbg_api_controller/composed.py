from functools import partial
from .basis.utils import insert_datum
from .basis.fetcher import recurse_bdh
from .connector import COLLECTION_PRICE
from .consts import FLD_LAST_PRICE
from .utils import load_bbg_data


load_bbg_price = partial(load_bbg_data, FLD_LAST_PRICE)
    
recurse_price = partial(recurse_bdh, fld=FLD_LAST_PRICE)    

insert_price = partial(insert_datum, COLLECTION_PRICE)

# recurse_and_insert_price = compose(insert_price, recurse_price)    
