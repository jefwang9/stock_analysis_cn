# A股股票分析智能体 - 历史数据获取模块

## 📊 模块功能

历史数据获取模块 (`historical_data.py`) 提供了完整的A股股票历史数据获取、存储和管理功能，是智能体进行技术分析和模型训练的数据基础。

### 🔥 核心功能

1. **股票历史数据获取**
   - 获取指定股票的历史OHLCV数据
   - 支持前复权、后复权、不复权数据
   - 自动计算技术指标（MA、RSI、MACD、KDJ、布林带、WR等）
   - 批量获取多只股票数据

2. **板块历史数据管理**
   - 获取板块内所有股票的历史数据
   - 板块股票映射关系管理
   - 板块整体表现分析
   - 支持概念板块和行业板块

3. **数据库存储和管理**
   - SQLite数据库持久化存储
   - 自动数据去重和更新
   - 数据缓存机制
   - 数据完整性检查

4. **数据导出功能**
   - 支持CSV格式导出
   - 批量数据导出
   - 自定义时间范围导出
   - 数据摘要统计

5. **技术指标计算**
   - 移动平均线（MA5、MA10、MA20、MA30、MA60）
   - 相对强弱指标（RSI）
   - MACD指标及其信号线
   - KDJ随机指标
   - 布林带指标
   - 威廉指标（WR）

## 🚀 快速开始

### 基础使用

```python
from historical_data import HistoricalDataCollector, get_stock_historical_data

# 创建数据收集器
collector = HistoricalDataCollector()

# 获取单只股票历史数据
stock_code = "000001"  # 平安银行
start_date = "2024-01-01"
end_date = "2024-01-31"

stock_data = get_stock_historical_data(stock_code, start_date, end_date)
print(stock_data.head())
```

### 板块数据获取

```python
from historical_data import get_sector_historical_data

# 获取板块历史数据
sector_name = "新能源"
sector_data = get_sector_historical_data(sector_name, start_date, end_date)

print(f"板块 {sector_name} 包含 {len(sector_data)} 只股票")
for stock_code, data in sector_data.items():
    print(f"{stock_code}: {len(data)} 个交易日数据")
```

### 批量数据收集

```python
from historical_data import get_all_sectors_historical_data

# 获取多个板块的历史数据
sectors = ["新能源", "白酒", "医药", "科技"]
all_data = get_all_sectors_historical_data(start_date, end_date, sectors)

print(f"成功获取 {len(all_data)} 个板块的数据")
```

## 📋 API 参考

### HistoricalDataCollector 类

#### 主要方法

- `get_stock_list(market="A股")` - 获取股票列表
- `get_sector_list()` - 获取板块列表
- `get_sector_stocks(sector_name)` - 获取板块股票列表
- `get_stock_historical_data(stock_code, start_date, end_date)` - 获取股票历史数据
- `get_multiple_stocks_data(stock_codes, start_date, end_date)` - 批量获取股票数据
- `get_sector_historical_data(sector_name, start_date, end_date)` - 获取板块历史数据
- `get_all_sectors_data(start_date, end_date, sectors)` - 获取所有板块数据
- `export_data_to_csv(data, output_dir)` - 导出数据到CSV
- `get_data_summary()` - 获取数据摘要

#### 数据字段说明

**股票历史数据字段：**
- `Date`: 交易日期
- `Open`: 开盘价
- `High`: 最高价
- `Low`: 最低价
- `Close`: 收盘价
- `Volume`: 成交量
- `Amount`: 成交额
- `Amplitude`: 振幅
- `Change_pct`: 涨跌幅(%)
- `Change_amount`: 涨跌额
- `Turnover`: 换手率

**技术指标字段：**
- `MA5`, `MA10`, `MA20`, `MA30`, `MA60`: 移动平均线
- `RSI`: 相对强弱指标
- `MACD`, `MACD_signal`, `MACD_histogram`: MACD指标
- `KDJ_K`, `KDJ_D`, `KDJ_J`: KDJ指标
- `BOLL_upper`, `BOLL_mid`, `BOLL_lower`: 布林带
- `WR`: 威廉指标

## 🔧 配置说明

### 数据库配置

在 `config.py` 中可以配置：

```python
class DatabaseConfig(BaseSettings):
    sqlite_path: str = "data/trading_agent.db"  # SQLite数据库路径
    redis_url: str = "redis://localhost:6379/0"  # Redis缓存连接
```

### 数据源配置

```python
class DataSourceConfig(BaseSettings):
    request_timeout: int = 30        # 请求超时时间
    request_delay: float = 1.0       # 请求间隔
    max_retries: int = 3            # 最大重试次数
```

## 📊 使用示例

### 示例1：获取股票历史数据

```python
from historical_data import get_stock_historical_data
from datetime import datetime, timedelta

# 获取最近30天的数据
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

stock_data = get_stock_historical_data("000001", start_date, end_date)

if not stock_data.empty:
    print(f"数据行数: {len(stock_data)}")
    print(f"最新收盘价: {stock_data['Close'].iloc[-1]:.2f}")
    print(f"期间涨跌幅: {((stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0]) - 1) * 100:.2f}%")
```

### 示例2：板块分析

```python
from historical_data import HistoricalDataCollector

collector = HistoricalDataCollector()

# 获取板块股票列表
sector_stocks = collector.get_sector_stocks("新能源")
print(f"新能源板块包含 {len(sector_stocks)} 只股票")

# 获取板块历史数据
sector_data = collector.get_sector_historical_data("新能源", start_date, end_date)

# 分析板块表现
if sector_data:
    sector_performance = []
    
    for stock_code, data in sector_data.items():
        if len(data) > 0:
            change_pct = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            sector_performance.append({
                'stock_code': stock_code,
                'change_pct': change_pct
            })
    
    # 计算板块平均表现
    avg_change = sum(p['change_pct'] for p in sector_performance) / len(sector_performance)
    print(f"新能源板块平均涨跌幅: {avg_change:.2f}%")
```

### 示例3：技术分析

```python
from historical_data import get_stock_historical_data

# 获取90天数据用于技术分析
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
stock_data = get_stock_historical_data("000858", start_date, end_date)

if not stock_data.empty:
    latest = stock_data.iloc[-1]
    
    # 趋势分析
    current_price = latest['Close']
    ma5 = latest['MA5']
    ma20 = latest['MA20']
    
    if current_price > ma5 > ma20:
        trend = "强势上涨"
    elif current_price > ma5:
        trend = "温和上涨"
    elif current_price < ma5 < ma20:
        trend = "强势下跌"
    elif current_price < ma5:
        trend = "温和下跌"
    else:
        trend = "震荡整理"
    
    print(f"趋势分析: {trend}")
    print(f"RSI: {latest['RSI']:.1f}")
    print(f"MACD: {latest['MACD']:.4f}")
```

### 示例4：数据导出

```python
from historical_data import HistoricalDataCollector

collector = HistoricalDataCollector()

# 准备导出数据
export_data = {
    "000001": stock_data,  # 平安银行数据
    "000858": another_stock_data  # 五粮液数据
}

# 导出到CSV
exported_files = collector.export_data_to_csv(export_data)
print(f"数据已导出到 {len(exported_files)} 个文件")
```

## 🗄️ 数据库结构

### 主要数据表

1. **stock_info** - 股票基本信息
   - stock_code: 股票代码
   - stock_name: 股票名称
   - industry: 行业
   - market: 市场

2. **stock_daily** - 股票日线数据
   - stock_code: 股票代码
   - trade_date: 交易日期
   - OHLCV数据和技术指标

3. **sector_info** - 板块信息
   - sector_name: 板块名称
   - sector_code: 板块代码
   - description: 描述

4. **sector_stocks** - 板块股票映射
   - sector_name: 板块名称
   - stock_code: 股票代码

5. **sector_daily** - 板块日线数据
   - sector_name: 板块名称
   - trade_date: 交易日期
   - 板块统计指标

## ⚠️ 注意事项

1. **数据源限制**
   - 使用AKShare免费接口，有请求频率限制
   - 建议设置合理的请求间隔（默认1秒）
   - 大量数据获取时建议分批处理

2. **存储空间**
   - 历史数据会持续增长，建议定期清理
   - 数据库文件可能变得很大，注意磁盘空间

3. **数据质量**
   - 复权数据可能影响技术指标计算
   - 建议使用前复权数据进行技术分析
   - 注意处理停牌股票的数据缺失

4. **性能优化**
   - 使用数据库缓存避免重复请求
   - 批量操作比单个操作更高效
   - 合理设置批处理大小

## 🧪 测试

运行测试脚本：

```bash
python test_historical.py
```

运行使用示例：

```bash
python example_historical.py
```

## 📈 性能优化

1. **缓存策略**
   - 数据库缓存避免重复请求
   - 内存缓存热点数据
   - 智能数据更新机制

2. **批处理优化**
   - 批量获取股票数据
   - 并行处理多个板块
   - 合理的请求间隔控制

3. **存储优化**
   - 数据压缩存储
   - 索引优化查询性能
   - 定期数据清理

## 🔄 更新日志

- **v1.0.0** - 初始版本，基础历史数据获取功能
- 支持股票和板块历史数据获取
- 集成技术指标计算
- 提供数据库存储和CSV导出功能
- 完整的API接口和使用示例
