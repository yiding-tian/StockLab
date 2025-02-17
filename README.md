 **批量数据获取A股数据**
 **自动增量更新**（避免重复下载）
 **支持 K 线 & 成交量可视化**
 **并行下载，加快速度**
 **指数数据单独管理（支持上证、深证、创业板）**
 **异常处理 & 自动重试机制**

## ***安装与配置***

#### **1. 配置 Conda 环境**

```
conda create -n stock_env python=3.10
conda activate stock_env
```

#### 2. 安装 Python 依赖

```python
pip install pandas matplotlib mplfinance tushare concurrent.futures
```

#### 3. 设置 Tushare API Token

在 `config.py` 文件中设置 `TUSHARE_TOKEN`：

```python
TS_TOKEN = "a0f92a002ca5f1a6983503e5d01174e482d1bfe0e875e0706dac4c1e"
```

#### 4. 运行数据下载

1. 直接运行 main.py 文件即可获取A股全部数据信息，若之前数据已经下载成功，则判断是否需要更新。
2. 运行 fetch_index_data.py 文件可以获取指数数据（上证指数，深证指数，创业板指）。

*注：*

1.  在文件 config.py 中,可以设置数据下载的文件夹地址

   ```python
   OUTPUT_DIR = "raw_data"
   ```

2.  在文件 main.py 中，函数的参数：起始时间 仅对K线图以及成交量图的绘制有关，任何股票的交易数据都是从上市第一天起开始记录

   ```python
   download_all_stocks("20230901", "20240214") # 针对k线图以及成交量图的绘制
   ```

   

## ***代码结构***

📂 project_stock
 ├── 📂 raw_data/                 # 存储下载的股票数据
 ├── 📂 index_data/           # 存储指数数据
 ├── 📜 config.py             # 配置文件（API Token、目录路径）
 ├── 📜 data_loader.py            # 股票数据获取模块
 ├── 📜 fetch_index_data.py      # 指数数据获取模块
 ├── 📜 plotter.py            # K 线图 & 成交量图绘制模块
 ├── 📜 utils.py              # 工具函数（数据处理、异常处理）
 ├── 📜 main.py               # 主程序入口
 ├── 📜 README.md             # 说明文档

 ├── 📜 failed_stocks.txt   #记录下载过程中失败的股票代码（自动生成）