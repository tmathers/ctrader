# ==================================================================================
# CTrader Configuration
# ==================================================================================
import logging

# API Keys
API_KEY = ""
API_SECRET = ""
TEST_API_KEY = ""
TEST_API_SECRET = ""

# Log Level - INFO -> less, DEBUG -> more
LOG_LEVEL = logging.DEBUG

# Strategy constants
MAX_LOSS_PERCENT = 0.15 # Sell if the LOSS goes above this percent since buying
MAX_GAIN_PERCENT = 0.15 # Sell if the GAIN goes above this percent since buying
BUY_ENTRY = 0.1         # The minimum percentage return over the window period to BUY
WINDOW = 60             # The number of seconds in which to consider entries
QUANTITY = 0.001        # The amount of coin to buy each trade
