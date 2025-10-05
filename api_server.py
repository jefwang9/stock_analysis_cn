"""
A股股票分析智能体API接口
提供RESTful API服务
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from contextlib import asynccontextmanager
import pandas as pd

# 导入自定义模块
from config import settings
from historical_data import HistoricalDataCollector, get_stock_historical_data, get_sector_historical_data
from realtime_data import RealtimeDataCollector, get_market_overview, get_sector_realtime_data
from sentiment_analyzer import SentimentAnalyzer
from sector_prediction_fixed import SectorPredictionModel, prepare_sector_features, train_all_sector_models
from backtesting import Backtester
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)

# 全局变量
historical_collector = None
realtime_collector = None
sentiment_analyzer = None
prediction_model = None
backtester = None
report_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global historical_collector, realtime_collector, sentiment_analyzer, prediction_model, backtester, report_generator
    
    # 启动时初始化
    logger.info("正在初始化A股股票分析智能体...")
    
    try:
        historical_collector = HistoricalDataCollector()
        realtime_collector = RealtimeDataCollector()
        sentiment_analyzer = SentimentAnalyzer()
        prediction_model = SectorPredictionModel()
        backtester = Backtester()
        report_generator = ReportGenerator()
        
        logger.info("智能体初始化完成")
    except Exception as e:
        logger.error(f"智能体初始化失败: {e}")
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭智能体...")

# 创建FastAPI应用
app = FastAPI(
    title="A股股票分析智能体API",
    description="提供A股股票分析、预测和回测功能的API服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class StockRequest(BaseModel):
    stock_code: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SectorRequest(BaseModel):
    sector_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class PredictionRequest(BaseModel):
    sectors: Optional[List[str]] = None
    include_sentiment: bool = True

class SentimentRequest(BaseModel):
    stock_codes: List[str]
    stock_names: List[str]
    days: int = 7

class BacktestRequest(BaseModel):
    date: str
    predictions: List[Dict[str, Any]]
    actual_performances: Dict[str, float]

# API路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "A股股票分析智能体API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "components": {
            "historical_collector": historical_collector is not None,
            "realtime_collector": realtime_collector is not None,
            "sentiment_analyzer": sentiment_analyzer is not None,
            "prediction_model": prediction_model is not None,
            "backtester": backtester is not None,
            "report_generator": report_generator is not None
        }
    }

# 历史数据API
@app.get("/api/stocks")
async def get_stock_list():
    """获取股票列表"""
    try:
        if not historical_collector:
            raise HTTPException(status_code=500, detail="历史数据收集器未初始化")
        
        stock_list = historical_collector.get_stock_list()
        
        return {
            "status": "success",
            "data": stock_list.to_dict('records') if not stock_list.empty else [],
            "count": len(stock_list),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sectors")
async def get_sector_list():
    """获取板块列表"""
    try:
        if not historical_collector:
            raise HTTPException(status_code=500, detail="历史数据收集器未初始化")
        
        sector_list = historical_collector.get_sector_list()
        
        return {
            "status": "success",
            "data": sector_list.to_dict('records') if not sector_list.empty else [],
            "count": len(sector_list),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取板块列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stocks/historical")
async def get_stock_historical_data(request: StockRequest):
    """获取股票历史数据"""
    try:
        if not request.start_date:
            request.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not request.end_date:
            request.end_date = datetime.now().strftime('%Y-%m-%d')
        
        data = get_stock_historical_data(request.stock_code, request.start_date, request.end_date)
        
        return {
            "status": "success",
            "stock_code": request.stock_code,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "data": data.to_dict('records') if not data.empty else [],
            "count": len(data),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取股票历史数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sectors/historical")
async def get_sector_historical_data(request: SectorRequest):
    """获取板块历史数据"""
    try:
        if not request.start_date:
            request.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not request.end_date:
            request.end_date = datetime.now().strftime('%Y-%m-%d')
        
        data = get_sector_historical_data(request.sector_name, request.start_date, request.end_date)
        
        # 转换数据格式
        formatted_data = {}
        for stock_code, stock_data in data.items():
            formatted_data[stock_code] = stock_data.to_dict('records')
        
        return {
            "status": "success",
            "sector_name": request.sector_name,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "data": formatted_data,
            "stock_count": len(data),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取板块历史数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 实时数据API
@app.get("/api/market/overview")
async def get_market_overview():
    """获取市场概览"""
    try:
        if not realtime_collector:
            raise HTTPException(status_code=500, detail="实时数据收集器未初始化")
        
        market_data = realtime_collector.get_market_overview()
        
        return {
            "status": "success",
            "data": market_data,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取市场概览失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/sectors/realtime")
async def get_sector_realtime_data():
    """获取板块实时数据"""
    try:
        if not realtime_collector:
            raise HTTPException(status_code=500, detail="实时数据收集器未初始化")
        
        sector_data = realtime_collector.get_sector_realtime_data()
        
        return {
            "status": "success",
            "data": sector_data,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取板块实时数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/hot-stocks")
async def get_hot_stocks(limit: int = 20):
    """获取热门股票"""
    try:
        if not realtime_collector:
            raise HTTPException(status_code=500, detail="实时数据收集器未初始化")
        
        hot_stocks = realtime_collector.get_hot_stocks(limit)
        
        return {
            "status": "success",
            "data": hot_stocks.to_dict('records') if not hot_stocks.empty else [],
            "count": len(hot_stocks),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取热门股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/sector-ranking")
async def get_sector_ranking():
    """获取板块排名"""
    try:
        if not realtime_collector:
            raise HTTPException(status_code=500, detail="实时数据收集器未初始化")
        
        ranking = realtime_collector.get_sector_ranking()
        
        return {
            "status": "success",
            "data": ranking.to_dict('records') if not ranking.empty else [],
            "count": len(ranking),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取板块排名失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 舆情分析API
@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: SentimentRequest):
    """分析舆情数据"""
    try:
        if not sentiment_analyzer:
            raise HTTPException(status_code=500, detail="舆情分析器未初始化")
        
        sentiment_data = sentiment_analyzer.collect_all_sentiment_data(
            request.stock_codes, request.stock_names, request.days
        )
        
        return {
            "status": "success",
            "data": sentiment_data.to_dict('records') if not sentiment_data.empty else [],
            "count": len(sentiment_data),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"舆情分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 预测API
@app.post("/api/predict/sectors")
async def predict_sectors(request: PredictionRequest):
    """预测板块表现"""
    try:
        if not prediction_model:
            raise HTTPException(status_code=500, detail="预测模型未初始化")
        
        # 获取板块数据
        sectors = request.sectors or settings.trading.sectors[:10]  # 限制前10个板块
        
        # 获取历史数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        sectors_data = {}
        for sector in sectors:
            try:
                sector_data = get_sector_historical_data(sector, start_date, end_date)
                if sector_data:
                    sectors_data[sector] = sector_data
            except Exception as e:
                logger.warning(f"获取板块 {sector} 数据失败: {e}")
                continue
        
        if not sectors_data:
            raise HTTPException(status_code=400, detail="没有可用的板块数据")
        
        # 获取舆情数据（如果请求）
        sentiment_data = None
        if request.include_sentiment:
            try:
                sentiment_data = sentiment_analyzer.collect_all_sentiment_data(
                    [], [], days=7
                )
            except Exception as e:
                logger.warning(f"获取舆情数据失败: {e}")
        
        # 准备特征数据
        all_features = prepare_sector_features(sectors_data, sentiment_data or pd.DataFrame())
        
        # 进行预测
        predictions_df = prediction_model.predict_all_sectors(all_features)
        
        return {
            "status": "success",
            "data": predictions_df.to_dict('records'),
            "count": len(predictions_df),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"板块预测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 回测API
@app.post("/api/backtest/update")
async def update_backtest(request: BacktestRequest):
    """更新回测数据"""
    try:
        if not backtester:
            raise HTTPException(status_code=500, detail="回测系统未初始化")
        
        # 记录预测结果
        for pred in request.predictions:
            backtester.record_prediction(
                date=request.date,
                sector=pred['sector'],
                predicted_change=pred['predicted_change'],
                confidence=pred.get('confidence', 0.0)
            )
        
        # 更新实际结果
        for sector, actual_change in request.actual_performances.items():
            backtester.update_actual_result(request.date, sector, actual_change)
        
        # 计算准确率
        accuracy_stats = backtester.calculate_daily_accuracy(request.date)
        
        return {
            "status": "success",
            "accuracy_stats": accuracy_stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"更新回测数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/performance")
async def get_backtest_performance(days: int = 30):
    """获取回测性能"""
    try:
        if not backtester:
            raise HTTPException(status_code=500, detail="回测系统未初始化")
        
        performance_data = backtester.get_performance_report(days)
        
        return {
            "status": "success",
            "data": performance_data.to_dict('records') if not performance_data.empty else [],
            "count": len(performance_data),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取回测性能失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 报表API
@app.get("/api/reports/generate")
async def generate_reports(period_days: int = 30):
    """生成分析报告"""
    try:
        if not report_generator:
            raise HTTPException(status_code=500, detail="报表生成器未初始化")
        
        reports = report_generator.generate_comprehensive_report(
            pd.DataFrame(), {}, period_days
        )
        
        return {
            "status": "success",
            "reports": reports,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 数据摘要API
@app.get("/api/data/summary")
async def get_data_summary():
    """获取数据摘要"""
    try:
        if not historical_collector:
            raise HTTPException(status_code=500, detail="历史数据收集器未初始化")
        
        summary = historical_collector.get_data_summary()
        
        return {
            "status": "success",
            "summary": summary,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"获取数据摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 模型管理API
@app.post("/api/models/train")
async def train_models(background_tasks: BackgroundTasks):
    """训练预测模型"""
    try:
        if not prediction_model:
            raise HTTPException(status_code=500, detail="预测模型未初始化")
        
        # 在后台训练模型
        background_tasks.add_task(train_models_background)
        
        return {
            "status": "success",
            "message": "模型训练已开始，请稍后查看结果",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"开始模型训练失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def train_models_background():
    """后台训练模型"""
    try:
        logger.info("开始后台训练模型...")
        
        # 获取训练数据
        sectors = settings.trading.sectors[:5]  # 限制前5个板块
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        
        sectors_data = {}
        for sector in sectors:
            try:
                sector_data = get_sector_historical_data(sector, start_date, end_date)
                if sector_data:
                    sectors_data[sector] = sector_data
            except Exception as e:
                logger.warning(f"获取板块 {sector} 数据失败: {e}")
                continue
        
        if sectors_data:
            # 准备特征数据
            all_features = prepare_sector_features(sectors_data, pd.DataFrame())
            
            # 训练模型
            training_results = train_all_sector_models(all_features)
            
            logger.info(f"模型训练完成: {training_results}")
        else:
            logger.warning("没有可用的训练数据")
            
    except Exception as e:
        logger.error(f"后台模型训练失败: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
