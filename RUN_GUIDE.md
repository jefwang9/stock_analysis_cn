# A股股票分析智能体 - 运行和测试指南

## 🚀 快速开始

### 1. 环境准备

#### 安装Python依赖
```bash
cd /Users/jwa/Documents/cn_stock_trading_agent
pip install -r requirements_core.txt
```

#### 可选：安装Redis（用于缓存）
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2. 基础测试

#### 运行基础功能测试
```bash
python test_basic.py
```

这个测试会验证：
- ✅ 所有模块导入正常
- ✅ 基础功能运行正常
- ✅ 数据访问功能正常
- ✅ 情感分析功能正常

#### 运行历史数据测试
```bash
python test_historical.py
```

#### 运行实时数据测试
```bash
python test_realtime.py
```

### 3. 使用示例

#### 运行历史数据使用示例
```bash
python example_historical.py
```

#### 运行实时数据使用示例
```bash
python example_realtime.py
```

## 📊 功能模块测试

### 历史数据获取模块

**功能：**
- 获取A股股票历史数据
- 计算技术指标（MA、RSI、MACD、KDJ等）
- 板块数据管理
- 数据库存储

**测试命令：**
```bash
python test_historical.py
```

**预期结果：**
- 成功获取股票列表（5000+只股票）
- 成功获取板块列表（500+个板块）
- 数据库初始化正常

### 实时数据获取模块

**功能：**
- 获取实时股票行情
- 板块实时数据监控
- 市场概览
- 热门股票排行

**测试命令：**
```bash
python test_realtime.py
```

**预期结果：**
- 成功获取市场概览
- 获取主要指数数据
- 板块实时数据（可能因网络问题有部分失败）

### 舆情分析模块

**功能：**
- 多平台舆情数据收集
- 情感分析
- 舆情聚合处理

**测试方法：**
```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
score = analyzer._calculate_sentiment_score("这只股票表现很好")
print(f"情感得分: {score}")  # 应该输出0-1之间的数值
```

### 回测系统模块

**功能：**
- 预测准确率追踪
- 性能评估
- 数据库存储

**测试方法：**
```python
from backtesting import Backtester

backtester = Backtester()
summary = backtester.get_data_summary()
print(summary)
```

### 报表生成模块

**功能：**
- Excel报告生成
- 图表可视化
- 综合分析报告

**测试方法：**
```python
from report_generator import ReportGenerator

generator = ReportGenerator()
# 生成测试报告
```

## 🔧 常见问题解决

### 1. 依赖包问题

**问题：** numpy版本冲突
```bash
pip install "numpy<2"
```

**问题：** pydantic导入错误
```bash
pip install pydantic-settings
```

### 2. 网络连接问题

**问题：** AKShare数据获取失败
- 检查网络连接
- 稍后重试
- 使用VPN（如需要）

**问题：** Redis连接失败
- Redis服务未启动：`brew services start redis`
- 或忽略Redis，系统会使用内存缓存

### 3. 数据获取问题

**问题：** 股票数据为空
- 检查股票代码格式
- 确认交易时间
- 检查数据源状态

**问题：** 板块数据为空
- 检查板块名称
- 确认板块存在
- 稍后重试

## 📈 性能优化建议

### 1. 数据获取优化

```python
# 批量获取数据，避免频繁请求
collector = HistoricalDataCollector()
data = collector.get_multiple_stocks_data(
    stock_codes=['000001', '000002', '600000'],
    start_date='2024-01-01',
    end_date='2024-01-31',
    batch_size=5  # 每批5只股票
)
```

### 2. 缓存使用

```python
# 使用Redis缓存
from realtime_data import RealtimeDataCollector

collector = RealtimeDataCollector()
# 系统会自动使用Redis缓存（如果可用）
```

### 3. 错误处理

```python
try:
    data = get_stock_historical_data("000001", "2024-01-01", "2024-01-31")
    if not data.empty:
        print(f"获取到 {len(data)} 条数据")
    else:
        print("未获取到数据")
except Exception as e:
    print(f"获取数据失败: {e}")
```

## 🎯 下一步开发

### 1. 机器学习模块

由于pandas版本兼容性问题，机器学习模块需要单独处理：

```bash
# 创建新的conda环境
conda create -n trading_agent python=3.9
conda activate trading_agent
pip install -r requirements_core.txt
```

### 2. 主智能体集成

```python
# 简化版主智能体测试
from historical_data import HistoricalDataCollector
from realtime_data import RealtimeDataCollector
from sentiment_analyzer import SentimentAnalyzer

# 创建各个模块实例
historical_collector = HistoricalDataCollector()
realtime_collector = RealtimeDataCollector()
sentiment_analyzer = SentimentAnalyzer()

print("所有模块创建成功！")
```

### 3. 定时任务

```python
import schedule
import time

def daily_task():
    print("执行每日任务...")
    # 这里添加每日任务逻辑

# 设置定时任务
schedule.every().day.at("15:30").do(daily_task)

# 运行调度器
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📝 测试报告

### 当前测试状态

✅ **已通过测试：**
- 配置模块
- 历史数据模块（基础功能）
- 实时数据模块（基础功能）
- 舆情分析模块
- 回测模块
- 报表生成模块

⚠️ **部分功能受限：**
- 机器学习模块（pandas版本兼容性）
- 网络数据获取（偶有连接问题）

✅ **核心功能正常：**
- 股票列表获取（5436只股票）
- 板块数据管理（525个板块）
- 情感分析（测试得分0.9911）
- 数据库操作

## 🚀 运行建议

1. **开发环境：** 使用conda创建独立环境
2. **生产环境：** 安装Redis服务
3. **网络环境：** 确保稳定的网络连接
4. **数据存储：** 定期清理历史数据

## 📞 技术支持

如遇到问题，请检查：
1. Python版本（推荐3.9）
2. 依赖包版本
3. 网络连接状态
4. Redis服务状态
5. 数据源可用性

