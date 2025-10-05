# A股股票分析智能体

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能完整的A股股票分析智能体，提供历史数据分析、实时数据监控、舆情分析、板块预测、回测评估和可视化展示等功能。

## 🌟 主要特性

### 📊 数据获取与分析
- **历史数据**: 支持5000+只A股股票的历史数据获取
- **实时数据**: 实时行情、市场概览、板块排名
- **技术指标**: MA、RSI、MACD、KDJ、布林带、威廉指标等
- **板块数据**: 500+个板块的详细数据

### 🤖 智能分析
- **舆情分析**: 多平台舆情数据收集（雪球、同花顺、东方财富、小红书、微博）
- **情感分析**: 基于SnowNLP的智能情感识别
- **板块预测**: 机器学习模型预测板块涨跌
- **特征工程**: 多维度特征提取和组合

### 🔄 回测与评估
- **回测系统**: 完整的预测准确率追踪
- **性能评估**: 多种评估指标和统计分析
- **历史记录**: 完整的预测和结果记录
- **报表生成**: 专业的Excel分析报告

### 🌐 现代化接口
- **RESTful API**: 完整的API服务，支持21个端点
- **Web界面**: 响应式Web应用，实时数据展示
- **数据可视化**: 交互式图表和仪表板
- **自动文档**: Swagger/OpenAPI自动生成文档

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 4GB+ 内存
- 稳定的网络连接
- Redis (可选，用于缓存)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd cn_stock_trading_agent
```

2. **创建虚拟环境**
```bash
python -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements_core.txt
```

4. **配置环境变量**
```bash
cp env_example.txt .env
# 编辑 .env 文件，配置必要的参数
```

5. **初始化数据库**
```bash
python -c "from historical_data import HistoricalDataCollector; HistoricalDataCollector()"
```

### 运行方式

#### 方式1: 基础功能测试
```bash
# 运行基础测试
python test_basic.py

# 运行单元测试
python test_simple.py
```

#### 方式2: API服务器
```bash
# 启动API服务器
python api_server.py

# 访问API文档
# http://localhost:8000/docs
```

#### 方式3: Web界面
```bash
# 启动Web应用
python web_app.py

# 访问Web界面
# http://localhost:8080
```

#### 方式4: 主智能体
```bash
# 启动主智能体
python main_agent.py
```

## 📖 使用指南

### API使用示例

#### 获取市场概览
```bash
curl http://localhost:8000/api/market/overview
```

#### 获取股票列表
```bash
curl http://localhost:8000/api/stocks
```

#### 获取板块预测
```bash
curl -X POST http://localhost:8000/api/predict/sectors \
  -H "Content-Type: application/json" \
  -d '{"sectors": ["新能源", "白酒", "医药"], "include_sentiment": true}'
```

#### 获取历史数据
```bash
curl -X POST http://localhost:8000/api/stocks/historical \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "000001", "start_date": "2024-01-01", "end_date": "2024-01-31"}'
```

### Python代码示例

#### 获取股票历史数据
```python
from historical_data import get_stock_historical_data

# 获取平安银行历史数据
data = get_stock_historical_data("000001", "2024-01-01", "2024-01-31")
print(f"获取到 {len(data)} 条数据")
```

#### 获取实时市场数据
```python
from realtime_data import get_market_overview

# 获取市场概览
market_data = get_market_overview()
print(f"上证指数: {market_data['indices']['上证指数']['current_price']}")
```

#### 舆情分析
```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
sentiment_score = analyzer._calculate_sentiment_score("这只股票表现很好")
print(f"情感得分: {sentiment_score}")
```

#### 板块预测
```python
from sector_prediction_fixed import SectorPredictionModel

model = SectorPredictionModel()
# 训练模型并进行预测
predictions = model.predict_all_sectors(features_data)
print(predictions)
```

## 📁 项目结构

```
cn_stock_trading_agent/
├── 📄 config.py                    # 配置管理
├── 📄 env_example.txt              # 环境变量模板
├── 📄 requirements_core.txt        # 核心依赖包
├── 📄 main_agent.py                # 主智能体
├── 📊 historical_data.py           # 历史数据获取
├── 📊 realtime_data.py             # 实时数据获取
├── 🧠 sentiment_analyzer.py        # 舆情分析
├── 🤖 sector_prediction_fixed.py   # 板块预测模型
├── 📈 backtesting.py               # 回测系统
├── 📋 report_generator.py           # 报表生成
├── 📊 data_visualization.py        # 数据可视化
├── 🌐 api_server.py                # API服务器
├── 🌐 web_app.py                   # Web应用
├── 🧪 test_basic.py                # 基础功能测试
├── 🧪 test_simple.py               # 简化单元测试
├── 📚 DEPLOYMENT.md                # 部署文档
├── 📚 RUN_GUIDE.md                 # 运行指南
├── 📚 PROJECT_SUMMARY.md           # 项目总结
├── 📁 templates/                   # Web模板
│   └── 📄 index.html              # 主页模板
├── 📁 data/                        # 数据目录
├── 📁 models/                      # 模型目录
├── 📁 logs/                        # 日志目录
└── 📁 temp/                        # 临时文件目录
```

## 🔧 核心模块说明

### 📊 数据获取模块

#### historical_data.py
- **功能**: 获取A股历史数据和技术指标
- **特性**: 支持5000+只股票，计算MA、RSI、MACD等指标
- **数据库**: SQLite持久化存储

#### realtime_data.py
- **功能**: 获取实时行情和市场数据
- **特性**: 实时监控、板块排名、热门股票
- **缓存**: Redis缓存支持

### 🧠 分析模块

#### sentiment_analyzer.py
- **功能**: 多平台舆情数据收集和分析
- **平台**: 雪球、同花顺、东方财富、小红书、微博
- **算法**: 基于SnowNLP的情感分析

#### sector_prediction_fixed.py
- **功能**: 板块涨跌预测模型
- **算法**: RandomForest、GradientBoosting、Ridge
- **特征**: 技术指标、舆情、市场情绪

### 📈 评估模块

#### backtesting.py
- **功能**: 预测准确率追踪和回测
- **指标**: 准确率、置信度、方向准确率
- **记录**: 完整的预测和结果历史

#### report_generator.py
- **功能**: 生成专业的分析报告
- **格式**: Excel、PDF等格式
- **内容**: 预测结果、准确率统计、图表

### 🌐 接口模块

#### api_server.py
- **框架**: FastAPI异步框架
- **端点**: 21个RESTful API端点
- **文档**: 自动生成Swagger文档

#### web_app.py
- **界面**: 响应式Web应用
- **功能**: 实时数据展示、交互式图表
- **技术**: HTML5、Bootstrap、Chart.js

## 📊 数据源说明

### 主要数据源
- **AKShare**: A股股票数据的主要来源
- **雪球**: 股票讨论和舆情数据
- **同花顺**: 实时行情和板块数据
- **东方财富**: 财经新闻和研报
- **小红书**: 投资心得和讨论
- **微博**: 市场情绪和热点

### 数据更新频率
- **实时数据**: 5秒间隔更新
- **历史数据**: 每日收盘后更新
- **舆情数据**: 每小时更新
- **预测结果**: 每日收盘后生成

## 🧪 测试说明

### 测试覆盖
- **基础功能测试**: 7/9模块测试通过
- **API接口测试**: 21个端点测试
- **数据获取测试**: 5000+股票数据验证
- **分析功能测试**: 情感分析、技术指标计算

### 运行测试
```bash
# 基础功能测试
python test_basic.py

# 单元测试
python test_simple.py

# API测试
curl http://localhost:8000/health
```

## 🚀 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t stock-trading-agent .

# 运行容器
docker run -d \
  --name stock-agent \
  -p 8000:8000 \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  stock-trading-agent
```

### 生产环境部署
```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api_server:app

# 使用systemd管理
sudo systemctl enable stock-agent
sudo systemctl start stock-agent
```

详细部署说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 📈 性能指标

### 数据处理能力
- **股票数量**: 5000+只A股
- **板块数量**: 500+个板块
- **历史数据**: 支持多时间范围
- **实时更新**: 5秒间隔监控

### 分析精度
- **情感分析**: 基于SnowNLP的准确情感识别
- **技术指标**: 标准金融技术指标计算
- **预测模型**: 多算法集成预测
- **回测系统**: 完整的准确率追踪

### 系统性能
- **API响应**: 毫秒级响应时间
- **并发处理**: 支持多用户同时访问
- **内存使用**: 优化的内存管理
- **错误恢复**: 自动错误恢复机制

## 🔧 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite:///data/trading_agent.db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/trading_agent.log
```

### 配置文件
主要配置在 `config.py` 中，包括：
- 数据库连接配置
- API服务配置
- 模型参数配置
- 日志配置

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd cn_stock_trading_agent

# 创建开发分支
git checkout -b feature/new-feature

# 安装开发依赖
pip install -r requirements_core.txt
```

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试
- 更新相关文档

### 提交规范
```bash
# 提交格式
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
```

## 📞 技术支持

### 常见问题

**Q: 如何解决pandas版本冲突？**
A: 使用 `pip install "numpy<2"` 降级numpy版本

**Q: Redis连接失败怎么办？**
A: 系统会自动使用内存缓存，或安装Redis服务

**Q: 数据获取失败怎么办？**
A: 检查网络连接，稍后重试，或使用VPN

**Q: 如何添加新的数据源？**
A: 参考现有模块，实现相应的数据获取接口

### 获取帮助
- 📚 查看 [运行指南](RUN_GUIDE.md)
- 📚 查看 [部署文档](DEPLOYMENT.md)
- 📚 查看 [项目总结](PROJECT_SUMMARY.md)
- 🐛 提交Issue报告问题
- 💬 参与讨论和交流

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢以下开源项目的支持：
- [AKShare](https://github.com/akfamily/akshare) - A股数据接口
- [FastAPI](https://github.com/tiangolo/fastapi) - 现代API框架
- [Plotly](https://github.com/plotly/plotly.py) - 交互式图表
- [Pandas](https://github.com/pandas-dev/pandas) - 数据分析库
- [Scikit-learn](https://github.com/scikit-learn/scikit-learn) - 机器学习库

## 🔄 更新日志

### v1.0.0 (2024-10-04)
- ✅ 初始版本发布
- ✅ 完整的数据获取和分析功能
- ✅ API接口和Web界面
- ✅ 数据可视化和报表生成
- ✅ 单元测试和部署文档

---

## 🎯 项目目标

我们的目标是构建一个功能完整、技术先进、易于使用的A股股票分析智能体，为投资者提供：

- 📊 **全面的数据分析** - 历史、实时、舆情多维度分析
- 🤖 **智能的预测能力** - 基于机器学习的板块预测
- 🌐 **现代化的接口** - RESTful API和Web界面
- 📈 **专业的可视化** - 交互式图表和仪表板
- 🔄 **完整的回测** - 预测准确率追踪和评估

**让我们一起构建更智能的A股分析工具！** 🚀
