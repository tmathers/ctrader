import logging
import json
import sys, getopt, os
import io
import config
import asyncio

import pandas as pd
import sqlalchemy

from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.error import ClientError
from binance.websocket.spot.websocket_client import SpotWebsocketClient as WebsocketClient

# Setup our configuration
config_logging(logging, logging.INFO)


SQLITE_URL = 'sqlite:///stream.db'
HTTPS_PROTOCOL = 'https://'
WEBSOCKET_PROTOCOL = 'wss://'
TEST_API_ENDPOINT = 'testnet.binance.vision'
API_ENDPOINT = ''
apiEndpoint = API_ENDPOINT
client = None
sqlEngine = None
key = config.API_KEY
secret = config.API_SECRET


# Main function
def main(argv):

    global client, apiEndpoint, key, secret, sqlEngine

    symbol = ''
    try:
        opts, args = getopt.getopt(argv,'hts:',['symbol='])
    except getopt.GetoptError:
        print(os.path.basename(__file__) + ' -s <symbol>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(os.path.basename(__file__) + ' -s <symbol>')
            sys.exit()
        elif opt in ('-t', '--test'):
            apiEndpoint = TEST_API_ENDPOINT
            key = config.TEST_API_KEY
            secret = config.TEST_API_SECRET

        elif opt in ('-s', '--symbol'):
            symbol = arg
            

    print('Using API: ' + apiEndpoint)

    client = Client(key, secret, base_url = HTTPS_PROTOCOL + apiEndpoint)
    #printExchangeInfo(symbol=symbol)
    #trade(symbol)
    
    sqlEngine = sqlalchemy.create_engine(SQLITE_URL)
    wsClient = WebsocketClient(stream_url = WEBSOCKET_PROTOCOL + apiEndpoint)
    wsClient.start()

    wsClient.ticker(
        symbol=symbol,
        id=1,
        callback=createFrame,
    )

    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(socket.__aenter__())
    #msg = loop.run_until_complete(socket.recv())


    #loop.close()


# Print the current exchange info for the symbol
def printExchangeInfo(symbol):
    global client
    logging.info(json.dumps(client.exchange_info(symbol=symbol), indent=4))


# Execute a trade
def trade(symbol):

    global client

    # Get the current price
    price = float(client.ticker_price(symbol)['price'])
    logging.info('Current price=' + str(price))

    # Get the multiplier Up and Down from PERCENT_PRICE
    info = client.exchange_info(symbol=symbol)
    multiplierUp = 0
    multiplierDown = 0
    precision = info['symbols'][0]['baseAssetPrecision']    # number of decimal places for the price

    for filter in info['symbols'][0]['filters']:
        if filter['filterType'] == 'PERCENT_PRICE':
            multiplierUp = float(filter['multiplierUp'])
            multiplierDown = float(filter['multiplierDown'])
            break

    # Calculate an order price
    minPrice = multiplierDown * price
    maxPrice = multiplierUp * price
    orderPrice = round((maxPrice - minPrice) / 2 + minPrice, precision)

    logging.info('Current price=' + str(price) + ' min=' + str(minPrice) + ', max=' + str(maxPrice))
    logging.info('Placing order: price=' + str(orderPrice))

    params = {
        'symbol': 'BTCUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': 0.002,
        'price': orderPrice,
    }
    try:
        response = client.new_order(**params)
        logging.info(json.dumps(response))
    except ClientError as error:
        logging.error(
            'Found error. status: {}, error code: {}, error message: {}'.format(
                error.status_code, error.error_code, error.error_message
            )
        )





def createFrame(msg):

    global sqlEngine

    print(msg)

    if 'result' in msg and msg['result'] == None:
        return
    df = pd.DataFrame([msg])
    df = df.loc[:,['s','E','p']]
    df.columns = ['symbol','time','price']
    df.price = df.price.astype(float)
    df.time = pd.to_datetime(df.time, unit='ms')

    print(df)
    df.to_sql(str(df.symbol), sqlEngine, if_exists='append', index=False)
    print(df)



# STRATEGY Part

import sqlalchemy
import pandas as pd

def runTradingStrategy():

    get_ipython().run_line_magic('run', './Binance_Keys.ipynb')
    sqlEngine = sqlalchemy.create_engine(SQLITE_URL)
    strategy(0.001, 60, 0.001)



# Trendfollowing
# if the crypto was rising by x % -> Buy
# exit when profit is above 0.15% or loss is crossing -0.15%
# Adapted from https://www.youtube.com/watch?v=rc_Y6rdBqXM

def strategy(entry, lookback, qty, open_position=False):
    while True:
        df = pd.read_sql(pair, sqlEngine)
        lookbackperiod = df.iloc[-lookback:]
        cumret = (lookbackperiod.price.pct_change() +1).cumprod() - 1
        if not open_position:
            if cumret[cumret.last_valid_index()] > entry:
                order = client.create_order(symbol=pair,
                                           side='BUY',
                                           type='MARKET',
                                           quantity=qty)
                print(order)
                open_position = True
                break
    if open_position:
        while True:
            df = pd.read_sql('BTCUSDT', sqlEngine)
            sincebuy = df.loc[df.time > 
                              pd.to_datetime(order['transactTime'],
                                            unit='ms')]
            if len(sincebuy) > 1:
                sincebuyret = (sincebuy.time.pct_change() +1).cumprod() - 1
                last_entry = sincebuyret[sincebuyret.last_valid_index()]
                if last_entry > 0.0015 or last_entry < -0.0015:
                    order = client.create_order(symbol=pair,
                                           side='SELL',
                                           type='MARKET',
                                           quantity=qty)
                    print(order)
                    break





if __name__ == '__main__':
   main(sys.argv[1:])