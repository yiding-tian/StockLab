import tushare as ts
import os
import pandas as pd
import time
from datetime import datetime

ts.set_token("a0f92a002ca5f1a6983503e5d01174e482d1bfe0e875e0706dac4c1e")
pro = ts.pro_api()

indices = {
    "上证指数": "000001.SH",
    "深证成指": "399001.SZ",
    "创业板指": "399006.SZ"
}

OUTPUT_DIR = "index_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_RETRIES = 3

def fetch_index_data(index_name, index_code, start_date, end_date):

    file_path = os.path.join(OUTPUT_DIR, f"{index_name}_{index_code}.csv")
    update_needed = True

    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path, parse_dates=["trade_date"])
        if not existing_df.empty:
            last_date = existing_df["trade_date"].max().strftime("%Y%m%d")
            print(f"⏩ {index_name} 现有数据，最后日期: {last_date}，检查增量更新...")

            if last_date >= end_date:
                print(f"✅ {index_name} 数据已是最新，无需更新: {file_path}")
                return True
            else:
                start_date = (datetime.strptime(last_date, "%Y%m%d") + pd.Timedelta(days=1)).strftime("%Y%m%d")
                print(f"🔄 {index_name} 需要更新: {start_date} - {end_date}")
        else:
            print(f"⚠️ {index_name} 现有文件为空，将重新下载...")
    else:
        print(f"📥 {index_name} 无历史数据，下载完整数据...")
        update_needed = True

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"📊 [尝试 {attempt}/{MAX_RETRIES}] 获取 {index_name} ({index_code}) 数据, 时间范围: {start_date} - {end_date}...")

            df = pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date,
                                 fields="trade_date, open, high, low, close, vol, amount")

            if df.empty:
                print(f"⚠️ {index_name} 没有新数据，无需更新")
                return True

            df["trade_date"] = pd.to_datetime(df["trade_date"])
            df.set_index("trade_date", inplace=True)
            df = df.sort_index()
            df = df[["open", "high", "low", "close", "vol", "amount"]]

            if os.path.exists(file_path) and not existing_df.empty:
                df = pd.concat([existing_df, df]).drop_duplicates().sort_index()

            df.to_csv(file_path, encoding="utf-8-sig")
            print(f"✅ {index_name} 数据已更新: {file_path}")
            return True

        except Exception as e:
            print(f"❌ {index_name} 失败: {e}，等待 5 秒后重试...")
            time.sleep(5)

    print(f"🚨 {index_name} 更新失败，已达到最大重试次数！")
    return False


def download_all_indices(start_date=None, end_date=None):

    if start_date is None:
        start_date = "20000101"
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")

    print(f"🔄 开始获取所有指数数据, 时间范围: {start_date} - {end_date}")

    for name, code in indices.items():
        fetch_index_data(name, code, start_date, end_date)

    print("✅ 所有指数数据获取完成！")

# Example
# 1. download_all_indices("20200101", datetime.now().strftime("%Y%m%d"))
# 2. download_all_indices("20220101", "20231231")
# 3. Download all data since 2000.
download_all_indices()