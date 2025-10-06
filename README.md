# A股股票分析智能体

一个专注于板块预测的A股股票分析智能体，提供每日收盘后训练、特征工程、模型表现记录等功能。

## 📁 项目结构

```
cn_stock_trading_agent/
├── 📁 src/                          # 源代码目录
│   ├── 📁 core/                     # 核心功能模块
│   │   ├── config.py                # 配置管理
│   │   └── __init__.py
│   ├── 📁 data/                     # 数据处理模块
│   │   ├── 📁 collectors/           # 数据收集器
│   │   │   ├── historical_data.py  # 历史数据收集
│   │   │   └── data_collector.py   # 通用数据收集器
│   │   ├── 📁 analyzers/           # 数据分析器
│   │   │   └── sentiment_analyzer.py # 情感分析
│   │   └── 📁 visualization/       # 数据可视化
│   │       └── data_visualization.py
│   ├── 📁 models/                   # 机器学习模型
│   │   ├── sector_prediction.py     # 板块预测模型
│   │   └── sector_prediction_fixed.py
│   ├── 📁 trading/                  # 交易相关
│   │   ├── backtesting.py          # 回测
│   │   ├── main_agent.py           # 主智能体
│   │   └── report_generator.py     # 报告生成
│   └── 📁 web/                      # Web应用
│       ├── api_server.py           # API服务器
│       ├── web_app.py              # Web界面
│       ├── templates/              # HTML模板
│       └── static/                 # 静态文件
├── 📁 tests/                        # 测试文件
├── 📁 examples/                     # 示例代码
├── 📁 data/                         # 数据存储
├── 📁 docs/                         # 文档
├── main.py                          # 主入口文件
├── requirements.txt                 # 依赖文件
└── README.md                        # 项目说明
```

## 📊 核心功能

### 🎯 板块预测模型
- **每日收盘后训练**: 自动获取历史数据，进行特征工程和模型训练
- **板块涨跌预测**: 预测每个板块第二天的上涨概率和下跌概率
- **模型表现记录**: 记录每天预测准确率，生成性能报表
- **特征工程**: 技术指标、舆情分析、市场情绪特征

### 📈 历史数据分析
- **股票数据获取**: 支持5000+只A股股票的历史数据
- **技术指标计算**: MA、RSI、MACD、KDJ、布林带等
- **板块数据聚合**: 按板块统计和分析股票表现

### 🔍 舆情分析
- **多平台数据收集**: 雪球、同花顺、东方财富等
- **情感分析**: 基于SnowNLP的情感得分计算
- **舆情聚合**: 按股票和板块聚合舆情数据

### 📊 回测和评估
- **预测准确率追踪**: 完整的预测和结果记录
- **性能评估**: 多种评估指标（R²、方向准确率等）
- **报表生成**: 自动生成Excel格式的分析报告

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行程序

```bash
# 使用新的启动脚本（推荐）
python start.py

# 或使用主入口文件
python main.py

# 或直接运行特定模块
python src/web/api_server.py      # 启动API服务器
python src/web/web_app.py         # 启动Web界面
python examples/example_historical.py  # 历史数据分析

# 测试API功能
python test_api.py
```

### 4. 端口管理

如果遇到端口占用问题，可以使用以下命令：

```bash
# 查看端口占用
lsof -i :8080
lsof -i :8000

# 杀死占用端口的进程
lsof -ti :8080 | xargs kill -9
lsof -ti :8000 | xargs kill -9
```

### 5. 访问服务

- **API服务器**: http://localhost:8000
- **Web界面**: http://localhost:8080
- **API文档**: http://localhost:8000/docs

### 6. 主要API端点

#### 板块预测相关
- `POST /api/models/daily-training` - 运行每日收盘后训练
- `POST /api/models/predict-daily` - 预测指定日期板块表现
- `GET /api/models/performance` - 获取模型表现摘要

#### 历史数据相关
- `GET /api/stocks` - 获取股票列表
- `GET /api/sectors` - 获取板块列表
- `POST /api/stocks/historical` - 获取股票历史数据
- `POST /api/sectors/historical` - 获取板块历史数据

#### 回测和评估
- `GET /api/backtest/performance` - 获取回测性能
- `POST /api/backtest/update` - 更新回测数据

## 📊 主要功能

### 1. 板块预测模型
- **每日训练**: 收盘后自动获取历史数据，进行特征工程和模型训练
- **涨跌预测**: 预测每个板块第二天的上涨概率和下跌概率
- **表现记录**: 记录每天预测准确率，生成性能报表
- **特征工程**: 技术指标、舆情分析、市场情绪特征

### 2. 历史数据分析
- **股票数据**: 获取5000+只A股股票的历史数据
- **技术指标**: MA、RSI、MACD、KDJ、布林带等指标计算
- **板块聚合**: 按板块统计和分析股票表现

### 3. 舆情分析
- **多平台收集**: 雪球、同花顺、东方财富等平台数据
- **情感分析**: 基于SnowNLP的情感得分计算
- **舆情聚合**: 按股票和板块聚合舆情数据

### 4. 回测和评估
- **准确率追踪**: 完整的预测和结果记录
- **性能评估**: R²、方向准确率等多种评估指标
- **报表生成**: 自动生成Excel格式的分析报告
- **Excel导出**: 详细数据导出

## 🔧 配置

项目使用Pydantic进行配置管理，主要配置项包括：

- **数据源配置**: AKShare、Tushare等
- **模型配置**: 特征工程、模型参数等
- **交易配置**: 板块列表、预测参数等
- **日志配置**: 日志级别、文件路径等

## 📈 API接口

### 市场数据
- `GET /api/market/overview` - 获取市场概览
- `GET /api/market/hot-stocks` - 获取热门股票
- `GET /api/market/sector-ranking` - 获取板块排名

### 历史数据
- `GET /api/historical/stock/{symbol}` - 获取股票历史数据
- `GET /api/historical/sector/{sector}` - 获取板块历史数据

### 预测分析
- `GET /api/prediction/sector` - 获取板块预测
- `POST /api/prediction/train` - 训练模型

### 回测
- `GET /api/backtest/results` - 获取回测结果
- `POST /api/backtest/run` - 运行回测

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_historical.py
python tests/test_realtime.py
```

## 📚 文档

详细文档请查看 `docs/` 目录：

- `README_historical.md` - 历史数据分析说明
- `README_realtime.md` - 实时数据分析说明
- `RUN_GUIDE.md` - 运行指南
- `PROJECT_SUMMARY.md` - 项目总结
- `DEPLOYMENT.md` - 部署指南

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证。

## ⚠️ 免责声明

本项目仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。