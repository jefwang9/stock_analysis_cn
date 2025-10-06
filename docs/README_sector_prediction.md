# A股股票分析智能体 - 板块预测模型

## 📊 模块功能

板块预测模型专注于每日收盘后的机器学习训练和预测，提供以下核心功能：

### 🔥 核心功能

1. **每日收盘后训练**
   - 自动获取历史数据（过去60天）
   - 特征工程：技术指标、舆情分析、市场情绪
   - 机器学习模型训练：RandomForest、GradientBoosting、Ridge
   - 模型性能评估和选择

2. **板块涨跌预测**
   - 预测每个板块第二天的上涨概率和下跌概率
   - 置信度计算和风险评估
   - 多模型集成预测
   - 预测结果记录和追踪

3. **模型表现记录**
   - 每日预测准确率统计
   - 模型性能历史追踪
   - 板块表现分析报告
   - 训练效果评估

4. **特征工程**
   - 技术指标：MA、RSI、MACD、KDJ、布林带
   - 舆情特征：情感得分、正面比例、舆情波动
   - 市场情绪：价格位置、动量、趋势强度
   - 成交量分析：量价关系、异常成交量

## 🚀 快速开始

### 基础使用

```python
from src.models.sector_prediction_fixed import SectorPredictionModel

# 创建预测模型
model = SectorPredictionModel()

# 运行每日训练流水线
result = model.daily_training_pipeline("2024-01-15")
print(f"训练结果: {result['summary']}")

# 获取模型表现摘要
performance = model.get_model_performance_summary(days=30)
print(f"30天平均准确率: {performance['overall_stats']['overall_accuracy']:.2%}")
```

### 每日训练流程

```python
# 1. 获取历史数据
from src.data.collectors.historical_data import get_main_sectors_data
sectors_data = get_main_sectors_data(days=60)

# 2. 获取舆情数据
from src.data.analyzers.sentiment_analyzer import analyze_all_sectors_sentiment
sentiment_data = analyze_all_sectors_sentiment(sectors_data, days=7)

# 3. 特征工程
all_features = model._prepare_all_sector_features(sectors_data, sentiment_data)

# 4. 训练模型
for sector, features_df in all_features.items():
    targets = model._calculate_targets(sectors_data.get(sector, {}), features_df)
    result = model.train_sector_model(sector, features_df, targets)
    
    if result['status'] == 'success':
        model.save_model(sector)
```

### 预测板块表现

```python
# 预测明天板块表现
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

# 准备特征数据
all_features = prepare_sector_features(sectors_data, sentiment_data)

# 进行预测
predictions_df = model.predict_all_sectors(all_features)

# 记录预测结果
for _, row in predictions_df.iterrows():
    model.record_prediction_performance(
        date=tomorrow,
        sector=row['sector'],
        prediction=row['predicted_change'],
        confidence=row.get('confidence', 0.0)
    )
```

## 📈 API接口

### 每日训练

```bash
# 启动每日训练
curl -X POST "http://localhost:8080/api/models/daily-training" \
     -H "Content-Type: application/json" \
     -d '{"target_date": "2024-01-15"}'
```

### 板块预测

```bash
# 预测指定日期板块表现
curl -X POST "http://localhost:8080/api/models/predict-daily" \
     -H "Content-Type: application/json" \
     -d '{"target_date": "2024-01-16"}'
```

### 模型表现

```bash
# 获取模型表现摘要
curl "http://localhost:8080/api/models/performance?days=30"
```

## 🎯 模型性能指标

### 评估指标

1. **R² 决定系数**
   - 衡量模型解释方差的能力
   - 范围：0-1，越接近1越好

2. **方向准确率**
   - 预测涨跌方向的准确率
   - 范围：0-1，>0.5为有效预测

3. **均方误差 (MSE)**
   - 预测值与实际值的平均平方差
   - 越小越好

4. **平均绝对误差 (MAE)**
   - 预测值与实际值的平均绝对差
   - 越小越好

### 特征重要性

模型会自动计算特征重要性，帮助理解哪些因素对预测最重要：

- **技术指标特征**：价格位置、动量、趋势强度
- **舆情特征**：情感得分、正面比例
- **市场特征**：成交量、波动率

## 📊 数据库结构

### 模型表现记录表 (model_performance)

| 字段 | 类型 | 说明 |
|------|------|------|
| date | TEXT | 预测日期 |
| sector | TEXT | 板块名称 |
| prediction | REAL | 预测涨跌幅 |
| actual_change | REAL | 实际涨跌幅 |
| accuracy | REAL | 预测准确率 |
| confidence | REAL | 预测置信度 |
| r2_score | REAL | R²决定系数 |
| direction_accuracy | REAL | 方向准确率 |

### 每日训练记录表 (daily_training)

| 字段 | 类型 | 说明 |
|------|------|------|
| date | TEXT | 训练日期 |
| sectors_trained | INTEGER | 训练板块数 |
| total_samples | INTEGER | 总样本数 |
| avg_r2_score | REAL | 平均R² |
| avg_direction_accuracy | REAL | 平均方向准确率 |
| status | TEXT | 训练状态 |

## 🔧 配置参数

### 模型配置 (config.py)

```python
class ModelConfig(BaseSettings):
    # 特征工程
    historical_days: int = 30  # 历史数据天数
    technical_indicators: List[str] = [
        "MA5", "MA10", "MA20", "MA30", "MA60",
        "RSI", "MACD", "KDJ", "BOLL", "WR"
    ]
    
    # 舆情分析
    sentiment_weight: float = 0.3  # 舆情权重
    
    # 模型训练
    train_ratio: float = 0.8
    validation_ratio: float = 0.1
    test_ratio: float = 0.1
```

## 📝 使用建议

### 最佳实践

1. **每日收盘后运行训练**
   - 建议在交易日收盘后30分钟内运行
   - 确保有足够的历史数据

2. **监控模型表现**
   - 定期检查预测准确率
   - 关注方向准确率是否>0.5

3. **特征工程优化**
   - 根据市场变化调整特征权重
   - 定期评估特征重要性

4. **模型更新策略**
   - 当准确率持续下降时重新训练
   - 考虑使用滚动窗口训练

### 注意事项

- 模型预测仅供参考，不构成投资建议
- 市场存在不确定性，预测准确率会波动
- 建议结合其他分析方法综合判断
- 定期评估和调整模型参数

## 🚨 故障排除

### 常见问题

1. **训练数据不足**
   - 确保有至少60天的历史数据
   - 检查数据质量和完整性

2. **预测准确率低**
   - 检查特征工程是否合理
   - 考虑增加更多特征或调整权重

3. **模型训练失败**
   - 检查数据格式和缺失值
   - 确保有足够的训练样本

4. **API调用超时**
   - 训练过程可能需要较长时间
   - 建议使用后台任务处理

## 📚 相关文档

- [项目总体说明](README.md)
- [历史数据获取](README_historical.md)
- [API接口文档](http://localhost:8080/docs)
- [配置说明](config.py)
