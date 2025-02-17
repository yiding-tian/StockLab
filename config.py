import tushare as ts
import os

TS_TOKEN = "a0f92a002ca5f1a6983503e5d01174e482d1bfe0e875e0706dac4c1e"

ts.set_token(TS_TOKEN)
pro = ts.pro_api()

OUTPUT_DIR = "raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FAILED_STOCKS_FILE = "failed_stocks.txt"

MAX_WORKERS = 10