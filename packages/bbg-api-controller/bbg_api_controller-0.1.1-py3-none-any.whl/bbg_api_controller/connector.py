import pdblp
import os
from dotenv import load_dotenv
from mongodb_controller import client
from .consts import DATABASE_NAME_BBG, COLLECTION_NAME_PRICE

load_dotenv()
BCON = pdblp.BCon(debug=False, port=os.getenv('BBG_PORT'), timeout=5000)
BCON.start()

COLLECTION_PRICE = client[DATABASE_NAME_BBG][COLLECTION_NAME_PRICE]
