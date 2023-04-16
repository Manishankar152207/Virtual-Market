from kite_tester import *
from time import sleep
from utility import *
from datetime import datetime


setting = read_settings()
try:
    kite = KiteApp(enctoken=setting["MY_TOKEN"])
    # kite_ob_check = kite.quote("NSE:NIFTY BANK")
    # if kite_ob_check == None:
    #     print("\nThe token is expired. Please provide your App code to authenticate!!!\n")
    #     twofa = int(input("Please provide your App code : "))
    #     MY_TOKEN = get_enctoken(setting["USERID"], setting["USERPASS"], twofa)
    #     kite = KiteApp(enctoken=MY_TOKEN)
except Exception as e:
    with open("Errlog.txt", "a") as f:
        f.write(f"{datetime.now()} - {e}\n")
    print(e)
    sleep(10)
else:
    TRANSACTION_TYPE = ''
    option_type = ''
    my_price = prev_close = premium_buy = premium_sell = prev_price = min_price = max_price = prev_diff = bounce_diff = float()
    symbol = ""
    my_timestamp = None
    strike_price = setting["STRIKE_PRICE"]
    sell_counter = 0
    first_order_sell = second_order_sell = third_order_sell = True
    flag_to_sell = False
    PC_File = ''
    Q1, Q2, Q3 = get_quantity()
    print(Q1, Q2, Q3)
    if not Q1:
        first_order_sell = False
    if not Q2:
        second_order_sell = False
    if not Q3:
        third_order_sell = False
    print(first_order_sell, second_order_sell, third_order_sell)
    while(True):
        if running_status() and datetime.now().weekday() != 5 and datetime.now().weekday() != 6:
            bank_nifty = kite.quote("NSE:NIFTY BANK")
            timestamp = formate_timestamp(bank_nifty['NSE:NIFTY BANK']['timestamp'])
            if not prev_close:
                prev_close = bank_nifty['NSE:NIFTY BANK']['ohlc']['close']
                print(f"Previous close : {prev_close}")
            market_price = bank_nifty['NSE:NIFTY BANK']['last_price']
            print(f"Market Price : {market_price}")
            if PC_File == '':
                PC_File = "pricelog/"+str(datetime.now().date())
            with open(f"{PC_File}.txt", "a") as f:
                f.write(f"{market_price}\n")
                    
            # Selling Process start    
            if (TRANSACTION_TYPE == kite.TRANSACTION_TYPE_BUY) and (first_order_sell or second_order_sell or third_order_sell):
                if option_type == kite.OPTION_TYPE_CE:
                    if market_price < my_price:
                        if (int(my_price - market_price) >= setting["LOSS_POINTS"]):
                            try:
                                # Api to sell option
                                unqty = uncertain_qty(first_order_sell, second_order_sell, third_order_sell)
                                orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, unqty) 
                                fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                if fo:
                                    # writing into file for records.
                                    my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)
                                    
                                    print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')                        
                                    TRANSACTION_TYPE = '-'
                                    first_order_sell = second_order_sell = third_order_sell = False
                                    sleep(10)
                                    break
                                else:
                                    TRANSACTION_TYPE = '-'
                                    first_order_sell = second_order_sell = third_order_sell = False
                                    print("Your order didn't SELL. Please check your Account.")
                                    sleep(10)
                                    break
                            except Exception as e:
                                TRANSACTION_TYPE = '-'
                                first_order_sell = second_order_sell = third_order_sell = False
                                with open("Errlog.txt", "a") as f:
                                    f.write(f"{datetime.now()} - {e}\n")
                                print("Something went wrong while selling.")
                                sleep(10)
                                break
                    else:
                        if int((timestamp - my_timestamp).total_seconds()) > 6:
                            if third_order_sell:
                                if max_price:
                                    if market_price < max_price:
                                        diff = max_price - market_price
                                        if diff > prev_diff:
                                            prev_diff = diff
                                            sell_counter+=1
                                            print(sell_counter)
                                            if sell_counter>3:
                                                try:
                                                    # Api to sell option
                                                    orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, Q3)    
                                                    fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                                    if fo:
                                                        # writing into file for records.
                                                        my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)                

                                                        print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                                        third_order_sell = False
                                                        if not first_order_sell and not second_order_sell and not third_order_sell:
                                                            with open("myaccount.txt", "a") as f:
                                                                f.write("******************************************************************\n")
                                                            print("All your order has been sold successfully.")
                                                            sleep(10)
                                                            break
                                                    else:
                                                        third_order_sell = False
                                                        print("Something went wrong while selling when third condition is satisfied. Please check your Account.\n")
                                                except Exception as e:
                                                    third_order_sell = False
                                                    with open("Errlog.txt", "a") as f:
                                                        f.write(f"{datetime.now()} - {e}\n")
                                                    print("Something went wrong while selling when third condition is satisfied. Please check your Account.\n")

                                        elif diff < prev_diff:
                                            if sell_counter>0:
                                                sell_counter-=1
                                            print(sell_counter)
                                    else:
                                        max_price = market_price  
                                        print("Maximum Price: ", max_price)
                                        sell_counter = prev_diff = 0                  
                                else:
                                    max_price = market_price
                                    print("Maximum Price: ", max_price)

                            if int((timestamp - my_timestamp).total_seconds()) >= setting["TIME_DIFF"]:
                                if first_order_sell:
                                    try:
                                        # Api to sell option
                                        orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, Q1)    
                                        fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                        if fo:
                                            # writing into file for records.
                                            my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)                

                                            print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                            first_order_sell = False
                                            if not first_order_sell and not second_order_sell and not third_order_sell:
                                                with open("myaccount.txt", "a") as f:
                                                    f.write("******************************************************************\n")
                                                print("All your order has been sold successfully.")
                                                sleep(10)
                                                break
                                        else:
                                            first_order_sell = False
                                            print("Something went wrong while selling when first condition is satisfied. Please check your Account.\n")

                                    except Exception as e:
                                        first_order_sell = False
                                        with open("Errlog.txt", "a") as f:
                                            f.write(f"{datetime.now()} - {e}\n")
                                        print("Something went wrong while selling when first condition is satisfied. Please check your Account.\n")

                                if second_order_sell:
                                    if market_price >= prev_price:
                                        prev_price = market_price
                                        if flag_to_sell:
                                            flag_to_sell = False
                                    else:
                                        if not flag_to_sell:
                                            bounce_diff = prev_price - market_price 
                                            print("bounce_diff ", bounce_diff)
                                            if bounce_diff > 1:
                                                flag_to_sell = True
                                        else:
                                            if prev_price - market_price > bounce_diff:
                                                try:
                                                    # Api to sell option
                                                    orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, Q2)    
                                                    fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                                    if fo:
                                                        # writing into file for records.
                                                        my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)                

                                                        print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                                        second_order_sell = False
                                                        flag_to_sell = False
                                                        if not first_order_sell and not second_order_sell and not third_order_sell:
                                                            with open("myaccount.txt", "a") as f:
                                                                f.write("******************************************************************\n")
                                                            print("All your order has been sold successfully.")
                                                            sleep(10)
                                                            break
                                                    else:
                                                        second_order_sell = False
                                                        flag_to_sell = False
                                                        print("Something went wrong while selling when second condition is satisfied. Please check your Account.\n")
                                                except Exception as e:
                                                    second_order_sell = False
                                                    flag_to_sell = False
                                                    with open("Errlog.txt", "a") as f:
                                                        f.write(f"{datetime.now()} - {e}\n")
                                                    print("Something went wrong while selling when second condition is satisfied. Please check your Account.\n")

                                            else:
                                                flag_to_sell = False
                                        prev_price = market_price   
                            else:
                                prev_price = market_price
                                

                elif option_type == kite.OPTION_TYPE_PE:
                    if market_price > my_price:
                        if (int(market_price - my_price) >= setting["LOSS_POINTS"]):
                            try:
                                # Api to sell option
                                unqty = uncertain_qty(first_order_sell, second_order_sell, third_order_sell)
                                orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, unqty)  

                                fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                if fo:
                                    # writing into file for records.
                                    my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)             

                                    print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                    TRANSACTION_TYPE = '-'
                                    first_order_sell = second_order_sell = third_order_sell = False
                                    sleep(10)
                                    break
                                else:
                                    TRANSACTION_TYPE = '-'
                                    first_order_sell = second_order_sell = third_order_sell = False
                                    print(f"Your order didn't SELL. Please check your Account.")
                                    sleep(10)
                                    break
                            except Exception as e:
                                TRANSACTION_TYPE = '-'
                                first_order_sell = second_order_sell = third_order_sell = False
                                with open("Errlog.txt", "a") as f:
                                    f.write(f"{datetime.now()} - {e}\n")
                                print("Something went wrong while selling.")
                                sleep(10)
                                break
                    else:
                        if int((timestamp - my_timestamp).total_seconds()) > 6: 
                            if third_order_sell:
                                # Third Condition start from here... 
                                if min_price:
                                    if market_price > min_price:
                                        diff = market_price-min_price
                                        if diff > prev_diff:
                                            prev_diff = diff
                                            sell_counter+=1
                                            print(sell_counter)
                                            if sell_counter>3:
                                                try:
                                                    # Api to sell option
                                                    orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, Q3)

                                                    fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                                    if fo:
                                                        # writing into file for records.
                                                        my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)
                                                        
                                                        print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                                        third_order_sell = False
                                                        if not first_order_sell and not second_order_sell and not third_order_sell:
                                                            with open("myaccount.txt", "a") as f:
                                                                f.write("******************************************************************\n")
                                                            print("All your order has been sold successfully.")
                                                            sleep(10)
                                                            break
                                                    else:
                                                        third_order_sell = False
                                                        print("Something went wrong while selling when third condition is satisfied. Please check your Account.\n")
                                                except Exception as e:
                                                    third_order_sell = False
                                                    with open("Errlog.txt", "a") as f:
                                                        f.write(f"{datetime.now()} - {e}\n")
                                                    print("Something went wrong while selling when third condition is satisfied. Please check your Account.\n")
                                        elif diff < prev_diff:
                                            if sell_counter>0:
                                                sell_counter-=1
                                            print(sell_counter)
                                    else:
                                        min_price = market_price  
                                        print("Minimum Price: ", min_price)
                                        sell_counter = prev_diff = 0                  
                                else:
                                    min_price = market_price
                                    print("Minimum Price: ", min_price)
                            
                            if int((timestamp - my_timestamp).total_seconds()) >= setting["TIME_DIFF"]: 
                                if first_order_sell:
                                    try:
                                        # Api to sell option
                                        orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, Q1)

                                        fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                        if fo:
                                            # writing into file for records.
                                            my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)
                                            
                                            print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                            first_order_sell = False
                                            if not first_order_sell and not second_order_sell and not third_order_sell:
                                                with open("myaccount.txt", "a") as f:
                                                    f.write("******************************************************************\n")
                                                print("All your order has been sold successfully.")
                                                sleep(10)
                                                break
                                        else:
                                            first_order_sell = False
                                            print("Something went wrong while selling when first condition is satisfied. Please check your Account.\n")

                                    except Exception as e:
                                        first_order_sell = False
                                        with open("Errlog.txt", "a") as f:
                                            f.write(f"{datetime.now()} - {e}\n")
                                        print("Something went wrong while selling when first condition is satisfied. Please check your Account.\n")

                                if second_order_sell:
                                    if market_price <= prev_price:
                                        prev_price = market_price
                                        if flag_to_sell:
                                            flag_to_sell = False
                                    else:
                                        if not flag_to_sell:
                                            bounce_diff = market_price - prev_price 
                                            print("bounce_diff ", bounce_diff)
                                            if bounce_diff > 1:
                                                flag_to_sell = True
                                        else:
                                            if market_price - prev_price > bounce_diff:
                                                try:
                                                    # Api to sell option
                                                    orderId = place_order(kite, symbol, kite.TRANSACTION_TYPE_SELL, Q2)    
                                                    fo, premium_sell, order_timestamp = find_order(kite, orderId)
                                                    if fo:
                                                        # writing into file for records.
                                                        my_records_sell(order_timestamp, symbol, premium_buy, premium_sell, orderId, option_type)                

                                                        print(f'{kite.TRANSACTION_TYPE_SELL} {symbol} {premium_sell}')
                                                        flag_to_sell = False
                                                        second_order_sell = False
                                                        if not first_order_sell and not second_order_sell and not third_order_sell:
                                                            with open("myaccount.txt", "a") as f:
                                                                f.write("******************************************************************\n")
                                                            print("All your order has been sold successfully.")
                                                            sleep(10)
                                                            break
                                                    else:
                                                        flag_to_sell = False
                                                        second_order_sell = False
                                                        print("Something went wrong while selling when second condition is satisfied. Please check your Account.\n")
                                                except Exception as e:
                                                    flag_to_sell = False
                                                    second_order_sell = False
                                                    with open("Errlog.txt", "a") as f:
                                                        f.write(f"{datetime.now()} - {e}\n")
                                                    print("Something went wrong while selling when second condition is satisfied. Please check your Account.\n")
                                            else:
                                                flag_to_sell = False
                                        prev_price = market_price
                            else:
                                prev_price = market_price
                            
                    
            # Buying process start
            if TRANSACTION_TYPE == '':            
                if market_price > prev_close:
                    option_type = kite.OPTION_TYPE_PE
                    TRANSACTION_TYPE = kite.TRANSACTION_TYPE_BUY
                    my_timestamp = timestamp
                    symbol = f"BANKNIFTY{get_expiry()}{strike_price if strike_price else find_strike_price(market_price)}{option_type}"
                    print(symbol)
                    try:
                        # Api to buy option
                        orderId = place_order(kite, symbol, TRANSACTION_TYPE)

                        # Checking whether our Order is placed or not.
                        fo, premium_buy, order_timestamp = find_order(kite, orderId)
                        if not fo:
                            sleep(10)
                            break
                        my_price = prev_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
                        print(f"You have bought {symbol} at {my_price} ")
                        # writing into file for records.
                        my_records_buy(order_timestamp, symbol, premium_buy, orderId)
                            
                        print(f'{TRANSACTION_TYPE} {symbol} {premium_buy}')
                    except Exception as e:
                        with open("Errlog.txt", "a") as f:
                            f.write(f"{datetime.now()} - {e}\n")
                        print("Something went wrong while buying.")
                        sleep(10)
                        break
                    

                elif market_price < prev_close:
                    option_type = kite.OPTION_TYPE_CE
                    TRANSACTION_TYPE = kite.TRANSACTION_TYPE_BUY
                    my_timestamp = timestamp
                    symbol = f"BANKNIFTY{get_expiry()}{strike_price if strike_price else find_strike_price(market_price)}{option_type}"
                    print(symbol)
                    try:
                        # Api to buy option
                        orderId = place_order(kite, symbol, TRANSACTION_TYPE)

                        # Checking whether our Order is placed or not.
                        fo, premium_buy, order_timestamp = find_order(kite, orderId)
                        if not fo:
                            sleep(10)
                            break
                        my_price = prev_price = kite.quote("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
                        print(f"You have bought {symbol} at {my_price} ")
                        # writing into file for records.
                        my_records_buy(order_timestamp, symbol, premium_buy, orderId)
                        
                        print(f'{TRANSACTION_TYPE} {symbol} {premium_buy}')
                    except Exception as e:
                        with open("Errlog.txt", "a") as f:
                            f.write(f"{datetime.now()} - {e}\n")
                        print("Something went wrong while buying.")
                        sleep(10)
                        break
        else:
            print("This is not market hour.")
        sleep(1)              
