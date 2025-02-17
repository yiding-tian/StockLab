import os
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf


def plot_stock_charts(stock_code, stock_name, file_path, save_dir, start_date, end_date):

    df = pd.read_csv(file_path, parse_dates=['trade_date'])
    if df.empty:
        print(f"⚠️ 无法绘图，交易数据为空: {stock_code}")
        return

    df.set_index('trade_date', inplace=True)
    df = df.sort_index()

    df = df[(df.index >= start_date) & (df.index <= end_date)]
    if df.empty:
        print(f"⚠️ 所设区间内无交易数据，不绘制图表: {stock_code}")
        return

    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA30'] = df['close'].rolling(window=30).mean()

    mc = mpf.make_marketcolors(up='#C0392B', down='#27AE60', edge='black', wick='black', volume='gray')
    s = mpf.make_mpf_style(marketcolors=mc, facecolor='#F8F9F9', gridcolor='#D0D3D4')

    ma_colors = ['black', 'yellow', 'red', 'green']

    fig, ax = mpf.plot(
        df,
        type='candle',
        style=s,
        mav=(5, 10, 20, 30),
        mavcolors=ma_colors,
        figsize=(14, 7),
        returnfig=True
    )

    lines = ax[0].lines[-4:]
    legend_labels = ["MA5", "MA10", "MA20", "MA30"]

    ax[0].legend(lines, legend_labels, loc="upper left", fontsize=14, frameon=True,
                 bbox_to_anchor=(1.02, 1), borderaxespad=0, edgecolor='black')

    ax[0].set_title(f"K Line Chart for {stock_code}", fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
    ax[0].set_ylabel("Price", fontsize=16, fontweight='bold', color='#2C3E50', labelpad=15)
    ax[0].tick_params(axis='y', labelsize=14, width=1.2)

    kline_path = os.path.join(save_dir, "draw_trade_data.png")
    fig.savefig(kline_path, dpi=400, bbox_inches='tight')
    plt.close(fig)

    print(f"✅ K 线图已保存: {kline_path}")

    fig, ax = plt.subplots(figsize=(14, 5), facecolor='#F8F9F9')

    if "vol" not in df.columns or df['vol'].isna().all():
        print(f"⚠️ {stock_code} 无成交量数据，跳过成交量图")
        return

    bar_colors = ['#C0392B' if close_ >= open_ else '#27AE60' for close_, open_ in zip(df['close'], df['open'])]
    ax.bar(df.index, df['vol'], color=bar_colors, alpha=0.8, width=0.6)

    ax.set_title(f"Trading Volume for {stock_code}", fontsize=18, fontweight='bold', color='#2C3E50', pad=20)
    ax.set_ylabel("Volume", fontsize=14, fontweight='bold', color='#2C3E50')

    volume_chart_path = os.path.join(save_dir, "draw_trade_vol.png")
    plt.savefig(volume_chart_path, dpi=400, bbox_inches='tight')
    plt.close(fig)

    print(f"✅ 成交量图已保存: {volume_chart_path}")