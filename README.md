# A股股票分析智能体

一个基于机器学习的A股股票分析智能体，提供历史数据分析、实时数据监控、情感分析和板块预测等功能。

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
│   │   │   ├── realtime_data.py    # 实时数据收集
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
python examples/example_realtime.py   # 实时数据分析

# 测试API功能
python test_api.py
```

### 3. 访问服务

- **API服务器**: http://localhost:8000
- **Web界面**: http://localhost:8080
- **API文档**: http://localhost:8000/docs

## 📊 主要功能

### 1. 数据收集
- **历史数据**: 获取股票历史价格、成交量等数据
- **实时数据**: 获取实时股价、市场概览等
- **情感数据**: 从雪球、东方财富等平台获取市场情感

### 2. 数据分析
- **技术指标**: MA、RSI、MACD、KDJ等
- **情感分析**: 基于NLP的情感分析
- **板块分析**: 板块轮动分析

### 3. 机器学习
- **板块预测**: 使用XGBoost、LightGBM等模型预测板块走势
- **特征工程**: 技术指标、情感指标等特征构建
- **模型训练**: 自动训练和优化模型

### 4. 回测系统
- **策略回测**: 基于预测结果的策略回测
- **性能评估**: 收益率、夏普比率等指标
- **风险控制**: 止损、仓位管理等

### 5. 报告生成
- **日报生成**: 每日预测报告
- **可视化**: 图表和趋势分析
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