"""
A股股票分析智能体配置管理
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Dict, Any

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    sqlite_path: str = "data/trading_agent.db"
    redis_url: str = "redis://localhost:6379/0"
    
class DataSourceConfig(BaseSettings):
    """数据源配置"""
    # AKShare支持的数据源
    akshare_enabled: bool = True
    
    # 外部数据API
    tushare_token: str = ""  # Tushare需要注册获取token
    
    # 爬虫配置
    request_timeout: int = 30
    request_delay: float = 1.0  # 请求间隔，避免被封
    max_retries: int = 3
    
class SentimentSourceConfig(BaseSettings):
    """舆情数据源配置"""
    # 雪球API
    xueqiu_api_url: str = "https://xueqiu.com/"
    
    # 同花顺
    tonghuashun_url: str = "https://quote.eastmoney.com/"
    
    # 东方财富
    eastmoney_url: str = "https://quote.eastmoney.com/"
    
    # 小红书（需要特殊的爬取策略）
    xiaohongshu_enabled: bool = False
    
    # 微博
    weibo_url: str = "https://s.weibo.com/"
    
class ModelConfig(BaseSettings):
    """模型配置"""
    # 板块预测模型
    sector_model_path: str = "models/sector_prediction_model.pkl"
    
    # 特征工程
    historical_days: int = 30  # 历史数据天数
    technical_indicators: List[str] = [
        "MA5", "MA10", "MA20", "MA30", "MA60",
        "RSI", "MACD", "KDJ", "BOLL", "WR"
    ]
    
    # 舆情分析
    sentiment_weight: float = 0.3  # 舆情在预测中的权重
    
    # 模型训练
    train_ratio: float = 0.8
    validation_ratio: float = 0.1
    test_ratio: float = 0.1
    
class TradingConfig(BaseSettings):
    """交易配置"""
    # 交易时间
    market_open_time: str = "09:30"
    market_close_time: str = "15:00"
    
    # 板块列表（主要A股板块）
    sectors: List[str] = [
        "新能源", "白酒", "医药", "科技", "金融", "地产", "化工", "钢铁",
        "煤炭", "有色金属", "军工", "农业", "食品饮料", "汽车", "家电",
        "建筑材料", "机械", "电力", "环保", "传媒"
    ]
    
    # 预测配置
    predict_top_n: int = 3  # 预测前N个上涨板块
    predict_bottom_n: int = 3  # 预测前N个下跌板块

class LoggingConfig(BaseSettings):
    """日志配置"""
    log_level: str = "INFO"
    log_file: str = "logs/trading_agent.log"
    max_log_size: str = "10MB"
    log_rotation: str = "1 day"

class Settings(BaseSettings):
    """主配置类"""
    project_name: str = "A股股票分析智能体"
    version: str = "1.0.0"
    
    # 子配置
    database: DatabaseConfig = DatabaseConfig()
    data_source: DataSourceConfig = DataSourceConfig()
    sentiment_source: SentimentSourceConfig = SentimentSourceConfig()
    model: ModelConfig = ModelConfig()
    trading: TradingConfig = TradingConfig()
    logging: LoggingConfig = LoggingConfig()
    
    # 路径配置
    data_dir: str = "data"
    models_dir: str = "models"
    logs_dir: str = "logs"
    temp_dir: str = "temp"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
def ensure_directories():
    """确保必要的目录存在"""
    dirs = [
        settings.data_dir,
        settings.models_dir,
        settings.logs_dir,
        settings.temp_dir,
        f"{settings.data_dir}/historical",
        f"{settings.data_dir}/realtime",
        f"{settings.data_dir}/sentiment",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

# 在导入时自动创建目录
ensure_directories()
