from kite_tester import *
from time import sleep
from datetime import datetime
import ast

# setting = MySetting()
f = open('settings.txt','r')
d = f.read()
setting = ast.literal_eval(d)
def read_settings():
    return setting 
    
# kite = KiteApp(enctoken=setting.MY_TOKEN)

my_cal = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6', 'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'O', 'Nov':'N', 'Dec':'D'}

def running_status():
    start_now = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
    end_now = datetime.now().replace(hour=15, minute=20, second=0, microsecond=0)
    return start_now<datetime.now()<end_now

def replace_token(token):
    setting["MY_TOKEN"] = token
    with open("settings.txt", "w") as f:
        f.write(f"{setting}")

def get_expiry():
    return setting['EXPIRY_DATE']
        
def formate_timestamp(data):
    return datetime.strptime(data, "%Y-%m-%d %H:%M:%S")

def find_strike_price(price):
    price = int(price)
    q = price // 100
    rem = price % 100
    if rem > 50:
        return (q+1)*100
    else:
        return q*100

def get_quantity():
    qty = (setting['MIN_QTY']//75)*25
    q1, q2, q3 = qty, setting['MIN_QTY'] - 2*qty, qty
    return q1, q2, q3


def uncertain_qty(f1, f2, f3):
    if not f1 and not f2 and not f3:
        return 0
    else:
        qty = setting['MIN_QTY']
        q1, q2, q3 = get_quantity()
        if not f1:
            qty = qty - q1
        if not f2:
            qty = qty - q2
        if not f3:
            qty = qty - q3
        return qty

def place_order(kite, symbol, tran_type, qty=setting['MIN_QTY']):
    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NFO,
                         tradingsymbol=symbol,
                         transaction_type=tran_type,
                         quantity=qty,
                         product=kite.PRODUCT_MIS,
                         order_type=kite.ORDER_TYPE_MARKET,
                         price=None,
                         validity=kite.VALIDITY_DAY,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=None,
                         stoploss=None,
                         trailing_stoploss=None,
                         user_id=setting['USERID'])
    return order

def find_order(kite, orderId):
    start = datetime.now()
    while(True):
        if int((datetime.now()-start).total_seconds()) < 6:
            orders = kite.orders()
            if orders:
                for order in orders:
                    if order['order_id'] == orderId and order['status'] == 'COMPLETE':                        
                        print(f"Your order placed successfully.")
                        return True, order['average_price'], order['order_timestamp']

                    elif order['order_id'] == orderId and order['status'] == 'REJECTED':
                        print(f"Your order get {order['status']} due to {order['status_message']}.")
                        return False, 0.0, ""
        else:
            print(f"Your order didn't place. Please check your Account.")
            return False, 0.0, ""
        sleep(0.5)

def my_records_buy(order_timestamp, symbol, premium_buy, orderId):
    with open('myaccount.txt','a') as f:
        f.write(f"**********************BOUGHT AT {order_timestamp}************************\n")
        f.write(f"Option Type {symbol} bought at Rs. {premium_buy} with orderId {orderId}\n")

def my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type):
    with open('myaccount.txt','a') as f:
        f.write(f"**********************SELL AT {order_timestamp}************************\n")
        f.write(f"Option Type {symbol} sell at Rs. {premium_sell} with orderId {orderId}\n")
        f.write("Points: "+str(premium_sell - premium_buy)+"\n")

def my_records_buy_unfavour(order_timestamp, symbol, premium_buy, orderId):
    with open('myaccount_unfavour.txt','a') as f:
        f.write(f"**********************BOUGHT AT {order_timestamp}************************\n")
        f.write(f"Option Type {symbol} bought at Rs. {premium_buy} with orderId {orderId}\n")

def my_records_sell_unfavour(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type):
    with open('myaccount_unfavour.txt','a') as f:
        f.write(f"**********************SELL AT {order_timestamp}************************\n")
        f.write(f"Option Type {symbol} sell at Rs. {premium_sell} with orderId {orderId}\n")
        f.write("Points: "+str(premium_sell - premium_buy)+"\n")
