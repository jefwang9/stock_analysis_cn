# A股股票分析智能体 - 实时数据获取模块

## 📊 模块功能

实时数据获取模块 (`realtime_data.py`) 提供了完整的A股股票实时行情数据获取功能，包括：

### 🔥 核心功能

1. **实时股票行情获取**
   - 获取指定股票的实时价格、涨跌幅、成交量等
   - 支持批量获取多只股票数据
   - 自动数据清洗和格式化

2. **板块实时数据监控**
   - 计算板块平均涨跌幅
   - 统计板块内上涨/下跌股票数量
   - 分析板块市场情绪
   - 计算板块成交量和成交额

3. **市场概览**
   - 主要指数实时表现（上证、深证、创业板、科创50）
   - 全市场统计（上涨/下跌股票数、涨停/跌停数量）
   - 市场整体情绪分析

4. **热门股票排行**
   - 按成交额排序的热门股票
   - 板块涨跌幅排名
   - 实时市场热点追踪

5. **实时监控系统**
   - 后台定时更新数据
   - Redis缓存支持
   - 数据库持久化存储

## 🚀 快速开始

### 基础使用

```python
from realtime_data import RealtimeDataCollector, get_market_overview

# 创建数据收集器
collector = RealtimeDataCollector()

# 获取指定股票实时行情
stock_codes = ['000001', '000002', '600000']
quotes = collector.get_realtime_quotes(stock_codes)
print(quotes)

# 获取市场概览
market_data = get_market_overview()
print(market_data)
```

### 板块监控

```python
from realtime_data import get_sector_realtime_data

# 获取主要板块实时数据
sectors = ['新能源', '白酒', '医药', '科技']
sector_data = get_sector_realtime_data(sectors)

for sector, data in sector_data.items():
    print(f"{sector}: {data['avg_change_pct']:+.2f}% - {data['market_sentiment']}")
```

### 实时监控

```python
from realtime_data import start_realtime_monitoring

# 启动实时监控
collector = start_realtime_monitoring(
    stock_codes=['000001', '000002'],  # 监控股票
    sectors=['新能源', '白酒'],         # 监控板块
    interval=5                         # 5秒更新一次
)

# 监控一段时间后停止
import time
time.sleep(30)
collector.stop_realtime_monitoring()
```

## 📋 API 参考

### RealtimeDataCollector 类

#### 主要方法

- `get_realtime_quotes(stock_codes=None)` - 获取实时股票行情
- `get_sector_realtime_data(sectors=None)` - 获取板块实时数据
- `get_market_overview()` - 获取市场概览
- `get_hot_stocks(limit=20)` - 获取热门股票
- `get_sector_ranking()` - 获取板块排名
- `start_realtime_monitoring()` - 启动实时监控
- `stop_realtime_monitoring()` - 停止实时监控

#### 数据字段说明

**股票实时行情字段：**
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `current_price`: 当前价格
- `change_pct`: 涨跌幅(%)
- `change_amount`: 涨跌额
- `volume`: 成交量
- `amount`: 成交额
- `high`: 最高价
- `low`: 最低价
- `open`: 开盘价
- `pre_close`: 昨收价

**板块实时数据字段：**
- `sector`: 板块名称
- `avg_change_pct`: 平均涨跌幅
- `total_volume`: 总成交量
- `total_amount`: 总成交额
- `rising_count`: 上涨股票数
- `falling_count`: 下跌股票数
- `market_sentiment`: 市场情绪
- `strong_stocks`: 强势股票数(>5%)
- `weak_stocks`: 弱势股票数(<-5%)

## 🔧 配置说明

### 环境配置

在 `config.py` 中可以配置：

```python
class DataSourceConfig(BaseSettings):
    request_timeout: int = 30        # 请求超时时间
    request_delay: float = 1.0       # 请求间隔
    max_retries: int = 3            # 最大重试次数

class DatabaseConfig(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"  # Redis连接
    sqlite_path: str = "data/trading_agent.db"    # SQLite数据库路径
```

### 依赖包

主要依赖包：
- `akshare`: A股数据接口
- `pandas`: 数据处理
- `redis`: 缓存支持
- `sqlite3`: 数据存储
- `requests`: HTTP请求

## 📊 使用示例

### 示例1：获取市场概览

```python
from realtime_data import get_market_overview

market_data = get_market_overview()

# 显示主要指数
for index_name, data in market_data['indices'].items():
    print(f"{index_name}: {data['current_price']:.2f} ({data['change_pct']:+.2f}%)")

# 显示市场统计
stats = market_data['market_stats']
print(f"上涨股票: {stats['rising_stocks']} ({stats['rising_stocks']/stats['total_stocks']*100:.1f}%)")
print(f"下跌股票: {stats['falling_stocks']} ({stats['falling_stocks']/stats['total_stocks']*100:.1f}%)")
```

### 示例2：板块分析

```python
from realtime_data import RealtimeDataCollector

collector = RealtimeDataCollector()

# 获取板块排名
ranking = collector.get_sector_ranking()
print("板块涨跌幅排名:")
for sector in ranking.head(10).itertuples():
    print(f"{sector.rank:2d}. {sector.sector:8s} {sector.avg_change_pct:+6.2f}% - {sector.market_sentiment}")
```

### 示例3：热门股票追踪

```python
from realtime_data import RealtimeDataCollector

collector = RealtimeDataCollector()

# 获取成交额前20名
hot_stocks = collector.get_hot_stocks(limit=20)
print("成交额前20名:")
for stock in hot_stocks.itertuples():
    print(f"{stock.rank:2d}. {stock.stock_name}({stock.stock_code}) "
          f"{stock.current_price:6.2f} ({stock.change_pct:+5.2f}%) "
          f"成交额: {stock.amount:8.0f}万")
```

## ⚠️ 注意事项

1. **数据源限制**
   - 使用AKShare免费接口，有请求频率限制
   - 建议设置合理的请求间隔（默认1秒）

2. **网络连接**
   - 需要稳定的网络连接
   - 建议配置代理（如需要）

3. **数据准确性**
   - 实时数据可能有延迟
   - 建议结合多个数据源验证

4. **存储空间**
   - 实时数据会持续存储到数据库
   - 建议定期清理历史数据

## 🧪 测试

运行测试脚本：

```bash
python test_realtime.py
```

运行使用示例：

```bash
python example_realtime.py
```

## 📈 性能优化

1. **缓存策略**
   - 使用Redis缓存热点数据
   - 设置合理的缓存过期时间

2. **并发处理**
   - 支持异步数据获取
   - 多线程后台更新

3. **数据压缩**
   - 存储时压缩历史数据
   - 减少数据库空间占用

## 🔄 更新日志

- **v1.0.0** - 初始版本，基础实时数据获取功能
- 支持股票实时行情、板块监控、市场概览
- 集成Redis缓存和SQLite存储
- 提供完整的API接口和使用示例
