# CTrader

## Prerequisites
- Python 3 (https://wiki.python.org/moin/BeginnersGuide/Download)

## Installation
### Install dependencies
`pip install binance-connector`  
`pip install python-binance`  
`pip install pandas`  
`pip install sqlalchemy`  

### Configuration
1. Copy `config-example.py` to `config.py`.
2. Generate the API keys: https://www.binance.com/en-NG/support/faq/360002502072 .
3. Copy the key and secret key info `config.py`.
4. If you plan on running on the test net, you must create API keys for the test net and copy them into `config.py`.
5. Configure log level and strategy constants.

## Running the Client
To run the client enter the following command:  
`python3 ctrader.py -s <SYMBOL> [-t]`  
where <SYMBOL> is the trading pair symbol (ex. BTCUSTD) and `-t` is to run on the test net.  

## Strategy
The trading stategy uses the constants defined in `config.py`, and is as follows:
- Every second, analyse prices over the last `WINDOW` seconds
- If the price has increased by `BUY_ENTRY` over that period, then buy `QUANTITY`
- After buying, calculate the price difference since buying every second
- If the percent gained is more than `MAX_GAIN_PERCENT`, then sell `QUANTITY` 
- Or if the percent lost is more than `MAX_LOSS_PERCENT`, then sell `QUANTITY`

## References
- Python Connector: https://binance-connector.readthedocs.io/en/stable/  
- API Docs: https://binance-docs.github.io/apidocs/spot/en/#general-api-information  



