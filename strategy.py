



import sqlalchemy
import pandas as pd
import ctrader
import config
import logging 
import time

from colorama import Fore, Back, Style

sqlEngine = None
client = None


def runTradingStrategy(symbol, _sqlEngine, _client):
    global sqlEngine, client
    sqlEngine = _sqlEngine
    client = _client

    while True:
        strategy(config.BUY_ENTRY / 100.0, config.WINDOW, config.QUANTITY, symbol)




# Trendfollowing
# if the crypto was rising by x % -> Buy
# exit when profit is above 0.15% or loss is crossing -0.15%
# Adapted from https://www.youtube.com/watch?v=rc_Y6rdBqXM

def strategy(entry, lookback, qty, symbol, open_position=False):


    # BUY
    while True:

        time.sleep(1)

        df = pd.read_sql('SELECT time, price FROM ' + symbol, sqlEngine)
        lookbackperiod = df.iloc[-lookback:]

        # Calculate cumulative return
        cumret = (lookbackperiod.price.pct_change() +1).cumprod() - 1
        if not open_position:

            cumReturn = cumret[cumret.last_valid_index()]
            logging.info('Current trend: %f%%, buy entry: %f%%', cumReturn * 100, entry * 100 )

            # Is the cum. return >= buy entry?
            if cumReturn >= entry:
                
                params = {
                    'symbol': symbol,
                    'side': 'BUY',
                    'type': 'MARKET',
                    'quantity': qty
                }

                order = client.new_order(**params)

                logging.info(Fore.GREEN + 'BOUGHT %f %s, return over window was %f%%', qty, symbol, cumReturn * 100.0)
                print(Style.RESET_ALL)

                logging.info(order)
                open_position = True
                break
    
    # SELL
    if open_position:
        while True:

            time.sleep(1)
            df = pd.read_sql(symbol, sqlEngine)

            # get rows since we bought
            sincebuy = df.loc[df.time > 
                              pd.to_datetime(order['transactTime'],
                                            unit='ms')]
            if len(sincebuy) > 1:


                # Get the pecentage of return since the last buy
                change = sincebuy.price.pct_change()    # note: this actually returns % / 100
                returnSinceBuyArr = (change +1).cumprod() - 1
                returnSinceBuy = returnSinceBuyArr[returnSinceBuyArr.last_valid_index()]

                logging.info('Return since buy: %f%%', returnSinceBuy * 100.0)
                
                # Sell?
                if returnSinceBuy > config.MAX_GAIN_PERCENT / 100.0 or returnSinceBuy < - config.MAX_LOSS_PERCENT / 100.0:

                    params = {
                        'symbol': symbol,
                        'side': 'SELL',
                        'type': 'MARKET',
                        'quantity': qty
                    }

                    order = client.new_order(**params)

                    gainOrLoss = 'GAIN' if returnSinceBuy > 0  else 'LOSS'
                    color = Fore.GREEN if returnSinceBuy > 0  else Fore.RED

                    logging.info(color + 'SOLD %f %s for %f%% %s' , qty, symbol, returnSinceBuy * 100.0, gainOrLoss)
                    print(Style.RESET_ALL)
                    
                    logging.info(order)
                    break