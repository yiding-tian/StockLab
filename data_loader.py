import os
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from config import pro, OUTPUT_DIR, FAILED_STOCKS_FILE, MAX_WORKERS
from utils import sanitize_filename, safe_round
from plotter import plot_stock_charts


def load_all_stock_info():
    df_all_info = pro.stock_basic(fields="ts_code, list_date, name, market, industry")
    return df_all_info.set_index("ts_code").to_dict("index")


STOCK_INFO_CACHE = load_all_stock_info()


def fetch_stock_data(stock_code, start_date, end_date):
    try:
        if stock_code not in STOCK_INFO_CACHE:
            print(f"❌ 无法找到 {stock_code} 的基础信息")
            return False

        stock_info = STOCK_INFO_CACHE[stock_code]
        list_date = stock_info["list_date"]
        stock_name = sanitize_filename(stock_info["name"])
        industry = stock_info.get("industry", "N/A")

        if not stock_name:
            return False

        stock_dir = os.path.join(OUTPUT_DIR, f"{stock_name}_{stock_code.replace('.', '_')}")
        os.makedirs(stock_dir, exist_ok=True)

        info_file_path = os.path.join(stock_dir, "info.csv")
        trade_file_path = os.path.join(stock_dir, f"{stock_name}_{stock_code.replace('.', '_')}.csv")
        kline_chart_path = os.path.join(stock_dir, "draw_trade_data.png")
        volume_chart_path = os.path.join(stock_dir, "draw_trade_vol.png")

        need_info_update = not os.path.exists(info_file_path)
        need_trade_update = not os.path.exists(trade_file_path) or os.path.getsize(trade_file_path) == 0
        need_chart_update = not (os.path.exists(kline_chart_path) and os.path.exists(volume_chart_path))

        # 检查 trade_file.csv 是否需要增量更新
        last_trade_date = None
        if os.path.exists(trade_file_path) and not need_trade_update:
            df_existing = pd.read_csv(trade_file_path, parse_dates=["trade_date"])
            if not df_existing.empty:
                last_trade_date = df_existing["trade_date"].max().strftime("%Y%m%d")
                if last_trade_date >= end_date:
                    need_trade_update = False
                else:
                    need_trade_update = True
                    need_info_update = True

        if not need_info_update and not need_trade_update and not need_chart_update:
            print(f"⏩ 已完整: {stock_code}（跳过）")
            return True

        if need_info_update:
            df_company = pro.stock_company(ts_code=stock_code)
            df_daily_basic = pro.daily_basic(ts_code=stock_code, fields="ts_code,total_mv,circ_mv,pe_ttm,pb,eps")
            df_balance = pro.balancesheet(ts_code=stock_code, fields="ts_code,total_assets", report_type=1)

            market_map = {"主板": "上海", "科创板": "上海", "创业板": "深圳", "中小企业板": "深圳", "北交所": "北京"}
            listing_location = market_map.get(stock_info["market"], "未知")

            province, city, reg_capital = "N/A", "N/A", "N/A"
            if not df_company.empty:
                province = df_company.iloc[0].get("province", "N/A")
                city = df_company.iloc[0].get("city", "N/A")
                reg_capital = df_company.iloc[0].get("reg_capital", "N/A")

            total_mv = safe_round(df_daily_basic.iloc[0].get("total_mv", None) / 10000, 2) if not df_daily_basic.empty else "N/A"
            circ_mv = safe_round(df_daily_basic.iloc[0].get("circ_mv", None) / 10000, 2) if not df_daily_basic.empty else "N/A"
            pe_ttm = safe_round(df_daily_basic.iloc[0].get("pe_ttm", None), 2) if not df_daily_basic.empty else "N/A"
            pb = safe_round(df_daily_basic.iloc[0].get("pb", None), 2) if not df_daily_basic.empty else "N/A"
            total_assets = safe_round(df_balance.iloc[0].get("total_assets", None) / 10000, 2) if not df_balance.empty else "N/A"

            company_info = {
                "公司名称": stock_name,
                "公司代号": stock_code,
                "上市地点": listing_location,
                "主要板块": industry,
                "公司位置": f"{province} {city}",
                "注册资本（万元）": reg_capital,
                "总市值（亿元）": total_mv,
                "流通市值（亿元）": circ_mv,
                "总资产（亿元）": total_assets,
                "PE（市盈率）": pe_ttm,
                "PB（市净率）": pb,
            }

            pd.DataFrame([company_info]).to_csv(info_file_path, index=False, encoding="utf-8-sig")
            print(f"📄 已更新 info.csv: {stock_code}")

        # 增量更新 trade_file.csv
        if need_trade_update:
            actual_start_date = list_date if last_trade_date is None else (datetime.strptime(last_trade_date, "%Y%m%d") + pd.Timedelta(days=1)).strftime("%Y%m%d")

            df_daily = pro.daily(
                ts_code=stock_code,
                start_date=actual_start_date,
                end_date=datetime.now().strftime("%Y%m%d"),
                fields="trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount,turnover_rate"
            )

            if df_daily.empty:
                print(f"⚠️ {stock_code} 无可用交易数据，跳过存储和绘图")
                return False

            df_daily = df_daily.sort_values("trade_date")

            if os.path.exists(trade_file_path) and last_trade_date:
                df_existing = pd.read_csv(trade_file_path, parse_dates=["trade_date"])
                df_daily = pd.concat([df_existing, df_daily]).drop_duplicates().sort_values("trade_date")

            df_daily.to_csv(trade_file_path, index=False, encoding="utf-8-sig")
            print(f"📊 已更新交易数据: {stock_code}")

        print(f"✅ 成功下载: {stock_code}")

        if need_chart_update:
            plot_stock_charts(stock_code, stock_name, trade_file_path, stock_dir, start_date, end_date)

        time.sleep(0.5)
        return True

    except Exception as e:
        print(f"❌ 下载失败: {stock_code}, 错误: {e}")
        return False


def download_all_stocks(start_date, end_date):
    stock_codes = list(STOCK_INFO_CACHE.keys())
    print(f"🔄 开始处理 {len(stock_codes)} 只 A 股股票数据...")

    while stock_codes:
        failed_stocks = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(lambda sc: fetch_stock_data(sc, start_date, end_date), stock_codes)

        for stock_code, success in zip(stock_codes, results):
            if not success:
                failed_stocks.append(stock_code)

        if failed_stocks:
            with open(FAILED_STOCKS_FILE, "w", encoding="utf-8") as f:
                for stock in failed_stocks:
                    f.write(stock + "\n")
            print(f"⚠️ {len(failed_stocks)} 只股票下载失败，将重试...")
            stock_codes = failed_stocks
            time.sleep(5)
        else:
            print("✅ 所有股票数据下载成功！")
            break