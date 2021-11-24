import logging
import json
import sys, getopt, os
import io
import asyncio
import threading
import time

import config
import strategy

import pandas as pd
import sqlalchemy

from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.error import ClientError
from binance.websocket.spot.websocket_client import SpotWebsocketClient as WebsocketClient

# Setup our configuration
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=config.LOG_LEVEL, datefmt='%d-%b-%y %H:%M:%S')


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
symbol = ''


# Main function
def main(argv):

    global client, apiEndpoint, key, secret, sqlEngine, symbol

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
    
    sqlEngine = sqlalchemy.create_engine(SQLITE_URL)
    wsClient = WebsocketClient(stream_url = WEBSOCKET_PROTOCOL + apiEndpoint)
    wsClient.start()

    wsClient.trade(
        symbol=symbol,
        id=1,
        interval='1s',
        callback=writePriceInfoToDb,
    )

    strategyThread = threading.Thread(target=strategy.runTradingStrategy, args=(symbol, sqlEngine, client, ))
    strategyThread.start()



# Write the symbol, price, and timestamp to the SQLite db
def writePriceInfoToDb(msg):

    global sqlEngine
    if 'result' in msg and msg['result'] == None:
        return
    df = pd.DataFrame([msg])
    df = df.loc[:,['s','E','p']]
    df.columns = ['symbol','time','price']
    df.price = df.price.astype(float)
    df.time = pd.to_datetime(df.time, unit='ms')

    df.to_sql(symbol, sqlEngine, if_exists='append', index=False)
    logging.debug('Current %s price: %f', symbol, df.price)



# Print the current exchange info for the symbol
def printExchangeInfo(symbol):
    global client
    logging.info(json.dumps(client.exchange_info(symbol=symbol), indent=4))


# Don't use
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


if __name__ == '__main__':
   main(sys.argv[1:])