# CTrader

## Prerequisites
- Python 3 (https://wiki.python.org/moin/BeginnersGuide/Download)
- Pip (https://pip.pypa.io/en/stable/installation/)

### Windows Users
- Add python scripts directory (ie. `%USERPROFILE%\AppData\Local\Programs\Python\Python310\Scripts` depending on setup) to PATH: https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/

## Installation
### Install dependencies
`pip install binance-connector`  
`pip install pandas`  
`pip install sqlalchemy`  

### Configuration
1. Copy `config-example.py` to `config.py`.
2. Generate the API keys: https://www.binance.com/en-NG/support/faq/360002502072.
3. Copy the key and secret key info `config.py`.
4. If you plan on running on the test net, you must create API keys for the test net and copy them into `config.py`: https://dev.binance.vision/t/binance-testnet-environments/99.
5. Configure log level and strategy constants.

## Running the Client
To run the client enter the following command:  
``python3 ctrader.py -s <SYMBOL> [-t]``  
where <SYMBOL> is the trading pair symbol (ex. BTCUSTD) and `-t` is to run on the test net.  
  
## Stopping the Client
To stop the client press `CTRL` + `C` or close the terminal window.

## Strategy
The trading stategy uses the constants defined in `config.py`, and is as follows:
- Every second, analyse prices over the last `WINDOW` seconds
- If the price has increased by `BUY_ENTRY` over that period, then buy `QUANTITY` coins
- After buying, calculate the price difference since buying every second
- If the percent gained is more than `MAX_GAIN_PERCENT`, then sell `QUANTITY` coins
- Or if the percent lost is more than `MAX_LOSS_PERCENT`, then sell `QUANTITY` coins
  
## Limitations
- The script writes to a file called `stream.db` which keeps track of the price data. At present, it does not get cleaned out, so if you keep running the script it will eventually consume all your disk space. So just delete the file every so often if you are running the script for a while.
- The script will only sell after it buys, and it will only sell the same amount of coin as it buys, as defined by `QUANTITY` in `config.py`. 
- The script doesn't keep track of buys and sells between runs - this is a future development
- The script does not check that you have enough money in your wallet before buying - it will fail in this case.
  
## Word of Warning
This strategy works better when the coin you are trading is trending up, otherwise you will probably just lose money. It is reccommended that you start on the test net (pass the `-t` option) until you get used to the strategy and adjust the constants appropriately. You should probably not let this run unsupervised because it will keep trading until it is killed or you run out of money.

## References
- Python Connector: https://binance-connector.readthedocs.io/en/stable/  
- API Docs: https://binance-docs.github.io/apidocs/spot/en/#general-api-information  



