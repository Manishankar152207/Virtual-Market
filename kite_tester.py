import os
try:
    import requests
except ImportError:
    os.system('python -m pip install requests')
try:
    import dateutil
except ImportError:
    os.system('python -m pip install python-dateutil')

import requests
import dateutil.parser
import random
import datetime

def get_enctoken(userid, password, twofa):
    session = requests.Session()
    response = session.post('https://kite.zerodha.com/api/login', data={
        "user_id": userid,
        "password": password
    })
    response = session.post('https://kite.zerodha.com/api/twofa', data={
        "request_id": response.json()['data']['request_id'],
        "twofa_value": twofa,
        "user_id": response.json()['data']['user_id']
    })
    enctoken = response.cookies.get('enctoken')
    if enctoken:
        return enctoken
    else:
        raise Exception("Enter valid details !!!!")


class KiteApp:
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"
    VARIETY_ICEBERG = "iceberg"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"

    # Option Type
    OPTION_TYPE_CE = 'CE'
    OPTION_TYPE_PE = 'PE'

    def __init__(self, enctoken):
        self.ORDERS_LIST = []
        self.Counter = 0
        self.headers = {"Authorization": f"enctoken {enctoken}"}
        self.session = requests.session()
        # self.root_url = "https://api.kite.trade"
        self.root_url = "https://kite.zerodha.com/oms"
        self.session.get(self.root_url, headers=self.headers)
        with open("price_history/2023-01-20_PC.txt", "r") as f:
            self.PRICE_HISTORY = f.read().split("\n")

    def quote(self, instruments):
        data = {"NSE:NIFTY BANK":{'timestamp':str(datetime.datetime.now().replace(microsecond=0)), "last_price":float(self.PRICE_HISTORY[self.Counter]), "ohlc":{"close":42000.45}}}
        self.Counter +=1
        return data

    def orders(self):
        return self.ORDERS_LIST

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, user_id=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        order_id = random.randint(99, 1000)
        params["order_id"] = order_id
        params["status"] = "COMPLETE"
        params["average_price"] = float(self.PRICE_HISTORY[self.Counter])
        params["order_timestamp"] = datetime.datetime.now()
        self.ORDERS_LIST.append(params)
        return order_id
