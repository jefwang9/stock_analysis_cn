"""
A股股票分析智能体主模块
协调各个子模块，提供统一的接口和工作流程
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import schedule
import time
from threading import Thread
import asyncio

# 导入自定义模块
from config import settings
from data_collector import StockDataCollector, get_main_sectors_data
from historical_data import HistoricalDataCollector, get_stock_historical_data, get_sector_historical_data
from realtime_data import RealtimeDataCollector, get_market_overview, get_sector_realtime_data
from sentiment_analyzer import SentimentAnalyzer, analyze_all_sectors_sentiment
from sector_prediction import SectorPredictionModel, prepare_sector_features
from backtesting import Backtester, daily_backtest_update
from report_generator import ReportGenerator, generate_comprehensive_report

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.logging.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AStockTradingAgent:
    """A股股票分析智能体"""
    
    def __init__(self):
        self.data_collector = StockDataCollector()
        self.historical_collector = HistoricalDataCollector()
        self.realtime_collector = RealtimeDataCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.prediction_model = SectorPredictionModel()
        self.backtester = Backtester()
        self.report_generator = ReportGenerator()
        
        # 工作状态
        self.is_running = False
        self.last_prediction_date = None
        self.models_trained = False
        
        logger.info("A股股票分析智能体初始化完成")
    
    def initialize(self) -> Dict[str, Any]:
        """
        初始化智能体
        包括数据收集、训练模型等
        """
        logger.info("开始初始化智能体...")
        
        try:
            # 1. 获取历史数据
            logger.info("正在获取历史数据...")
            sectors_data = get_main_sectors_data(days=settings.model.historical_days + 30)
            
            if not sectors_data:
                raise Exception("无法获取历史数据，初始化失败")
            
            logger.info(f"成功获取 {len(sectors_data)} 个板块的历史数据")
            
            # 2. 收集舆情数据
            logger.info("正在收集舆情数据...")
            sentiment_data = analyze_all_sectors_sentiment(sectors_data, days=7)
            
            # 3. 训练预测模型
            logger.info("正在训练预测模型...")
            self._train_models(sectors_data, sentiment_data)
            
            # 4. 初始化完成
            self.models_trained = True
            logger.info("智能体初始化完成")
            
            return {
                'status': 'success',
                'message': '初始化完成',
                'sectors_count': len(sectors_data),
                'models_trained': self.models_trained,
                'sentiment_data_count': len(sentiment_data) if not sentiment_data.empty else 0
            }
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'models_trained': False
            }
    
    def _train_models(self, sectors_data: Dict[str, Dict[str, pd.DataFrame]], 
                     sentiment_data: pd.DataFrame):
        """训练所有板块的预测模型"""
        
        # 准备特征数据
        all_features = prepare_sector_features(sectors_data, sentiment_data)
        
        # 为每个板块训练模型
        for sector in sectors_data.keys():
            if sector in all_features and not all_features[sector].empty:
                logger.info(f"正在训练 {sector} 板块模型...")
                
                # 生成随机目标变量（实际应用中应该使用真实的历史涨跌幅）
                features_df = all_features[sector]
                targets = self._generate_mock_targets(features_df, sector)
                
                # 训练模型
                try:
                    self.prediction_model.train_sector_model(sector, features_df, targets)
                    self.prediction_model.save_model(sector)
                    logger.info(f"{sector} 板块模型训练完成")
                except Exception as e:
                    logger.error(f"{sector} 板块模型训练失败: {e}")
    
    def _generate_mock_targets(self, features_df: pd.DataFrame, sector: str) -> pd.Series:
        """生成模拟目标变量（实际应用中应从真实数据计算）"""
        # 这里简化处理，实际应该基于板块的历史表现生成
        np.random.seed(hash(sector) % 1000)
        return pd.Series(np.random.normal(0, 3, len(features_df)))
    
    def predict_daily_sectors(self, target_date: str = None) -> Dict[str, Any]:
        """
        预测指定日期的板块表现
        
        Args:
            target_date: 目标日期，默认明天
            
        Returns:
            Dict: 预测结果
        """
        if not self.models_trained:
            logger.error("模型尚未训练，无法进行预测")
            return {'status': 'error', 'message': '模型尚未训练'}
        
        try:
            if target_date is None:
                target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            logger.info(f"开始预测 {target_date} 的板块表现...")
            
            # 1. 获取最新的股票数据
            latest_data = get_main_sectors_data(days=settings.model.historical_days)
            
            # 2. 收集最新舆情数据
            sentiment_data = analyze_all_sectors_sentiment(latest_data, days=3)
            
            # 3. 准备特征数据
            all_features = prepare_sector_features(latest_data, sentiment_data)
            
            # 4. 进行预测
            predictions_df = self.prediction_model.predict_all_sectors(all_features)
            
            # 5. 保存预测结果到数据库
            for _, row in predictions_df.iterrows():
                self.backtester.record_prediction(
                    date=target_date,
                    sector=row['sector'],
                    predicted_change=row['predicted_change'],
                    confidence=row.get('confidence', 0.0)
                )
            
            # 6. 生成预测报告
            predictions_summary = self._summarize_predictions(predictions_df)
            
            logger.info(f"预测完成，预测 {target_date} 涨幅前三: {predictions_summary['top_gainers']}")
            logger.info(f"预测 {target_date} 跌幅前三: {predictions_summary['top_losers']}")
            
            return {
                'status': 'success',
                'target_date': target_date,
                'predictions': predictions_df.to_dict('records'),
                'summary': predictions_summary,
                'model_confidence': predictions_df['confidence'].mean()
            }
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _summarize_predictions(self, predictions_df: pd.DataFrame) -> Dict[str, Any]:
        """总结预测结果"""
        
        # 获取涨幅前三
        top_gainers = predictions_df.nlargest(settings.trading.predict_top_n, 'predicted_change')
        
        # 获取跌幅前三
        top_losers = predictions_df.nsmallest(settings.trading.predict_bottom_n, 'predicted_change')
        
        return {
            'top_gainers': top_gainers['sector'].tolist(),
            'top_losers': top_losers['sector'].tolist(),
            'gainer_predictions': top_gainers[['sector', 'predicted_change']].to_dict('records'),
            'loser_predictions': top_losers[['sector', 'predicted_change']].to_dict('records'),
            'avg_prediction': predictions_df['predicted_change'].mean(),
            'prediction_std': predictions_df['predicted_change'].std()
        }
    
    def update_actual_results(self, date: str, actual_performances: Dict[str, float]):
        """
        更新实际结果
        
        Args:
            date: 交易日
            actual_performances: 各板块实际表现 {板块名: 涨跌幅}
        """
        logger.info(f"正在更新 {date} 的实际结果...")
        
        try:
            # 更新回测数据
            accuracy_stats = daily_backtest_update(date, pd.DataFrame(), actual_performances)
            
            logger.info(f"{date} 实际结果更新完成，当日准确率: {accuracy_stats.get('accuracy_rate', 0):.2%}")
            
            return {
                'status': 'success',
                'accuracy_stats': accuracy_stats
            }
            
        except Exception as e:
            logger.error(f"更新实际结果失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_reports(self, include_sector_analysis: bool = True, 
                        period_days: int = 30) -> Dict[str, str]:
        """
        生成分析报告
        
        Args:
            include_sector_analysis: 是否包含板块分析
            period_days: 统计周期天数
            
        Returns:
            Dict: 生成的报告文件路径
        """
        logger.info("正在生成分析报告...")
        
        try:
            # 获取最新的准确率统计
            latest_performance = self.backtester.get_performance_report(period_days)
            
            if latest_performance.empty:
                logger.warning("没有足够的历史数据生成报表")
                return {}
            
            latest_stats = {
                'accuracy_rate': latest_performance['accuracy_rate'].mean(),
                'avg_confidence': latest_performance['avg_confidence'].mean(),
                'top_gainer_accuracy': latest_performance['top_gainer_accuracy'].mean(),
                'top_loser_accuracy': latest_performance['top_loser_accuracy'].mean(),
                'total_predictions': latest_performance['total_predictions'].sum()
            }
            
            # 生成综合报告
            empty_predictions = pd.DataFrame()
            reports = self.report_generator.generate_comprehensive_report(
                empty_predictions, latest_stats, period_days)
            
            logger.info(f"分析报告生成完成")
            return reports
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return {}
    
    def run_daily_workflow(self):
        """运行每日工作流程"""
        logger.info("开始每日工作流程...")
        
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 1. 预测明天的板块表现
            logger.info("步骤1: 预测明天板块表现...")
            prediction_result = self.predict_daily_sectors()
            
            if prediction_result['status'] != 'success':
                logger.error("预测失败，终止每日工作流程")
                return
            
            # 2. 更新昨天的实际结果（如果有的话）
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            if self._has_actual_data(yesterday):
                logger.info("步骤2: 更新昨天实际结果...")
                actual_performances = self._get_actual_performances(yesterday)
                if actual_performances:
                    self.update_actual_results(yesterday, actual_performances)
            
            # 3. 生成日报
            logger.info("步骤3: 生成日报...")
            self._generate_daily_report(prediction_result)
            
            logger.info("每日工作流程完成")
            
        except Exception as e:
            logger.error(f"每日工作流程执行失败: {e}")
    
    def _has_actual_data(self, date: str) -> bool:
        """检查是否有指定日期的实际数据"""
        # 这里简化处理，实际应该查询数据库或API
        return False  # 临时返回False，实际应用中会实现真实的数据检查
    
    def _get_actual_performances(self, date: str) -> Dict[str, float]:
        """获取指定日期的实际板块表现"""
        # 这里简化处理，实际应该从数据源获取真实数据
        return {}  # 临时返回空字典
    
    def _generate_daily_report(self, prediction_result: Dict[str, Any]):
        """生成每日报告"""
        # 这里简化处理，实际会生成详细的报告
        logger.info(f"日报告已生成，预测结果: {prediction_result.get('summary', {})}")
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        logger.info("启动定时任务调度器...")
        
        # 每日收盘后15:30预测第二天
        schedule.every().day.at("15:30").do(self.run_daily_workflow)
        
        # 每日开盘前09:00更新实际结果
        schedule.every().day.at("09:00").do(self._update_morning_results)
        
        # 每周五生成周报
        schedule.every().friday.at("18:00").do(
            lambda: self.generate_reports(period_days=7)
        )
        
        # 每月最后一天生成月报
        schedule.every().month.do(
            lambda: self.generate_reports(period_days=30)
        )
        
        self.is_running = True
        
        # 在后台线程中运行调度器
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        
        Thread(target=run_scheduler, daemon=True).start()
        
        logger.info("定时任务调度器已启动")
    
    def _update_morning_results(self):
        """早上更新实际结果"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        actual_performances = self._get_actual_performances(yesterday)
        
        if actual_performances:
            self.update_actual_results(yesterday, actual_performances)
            logger.info(f"已更新 {yesterday} 的实际结果")
    
    def stop_scheduler(self):
        """停止定时任务调度器"""
        self.is_running = False
        schedule.clear()
        logger.info("定时任务调度器已停止")
    
    def get_historical_data(self, stock_code: str = None, sector_name: str = None,
                           start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取历史数据"""
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            if stock_code:
                # 获取单只股票历史数据
                data = get_stock_historical_data(stock_code, start_date, end_date)
                return {
                    'status': 'success',
                    'data_type': 'stock',
                    'stock_code': stock_code,
                    'data': data.to_dict('records') if not data.empty else [],
                    'start_date': start_date,
                    'end_date': end_date
                }
            elif sector_name:
                # 获取板块历史数据
                data = get_sector_historical_data(sector_name, start_date, end_date)
                return {
                    'status': 'success',
                    'data_type': 'sector',
                    'sector_name': sector_name,
                    'data': {k: v.to_dict('records') for k, v in data.items()} if data else {},
                    'start_date': start_date,
                    'end_date': end_date
                }
            else:
                return {'status': 'error', 'message': '请指定股票代码或板块名称'}
                
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def initialize_historical_database(self) -> Dict[str, Any]:
        """初始化历史数据库"""
        try:
            logger.info("开始初始化历史数据库...")
            
            # 获取股票列表
            stock_list = self.historical_collector.get_stock_list()
            
            # 获取板块列表
            sector_list = self.historical_collector.get_sector_list()
            
            logger.info(f"历史数据库初始化完成: {len(stock_list)}只股票, {len(sector_list)}个板块")
            
            return {
                'status': 'success',
                'stock_count': len(stock_list),
                'sector_count': len(sector_list),
                'message': '历史数据库初始化完成'
            }
            
        except Exception as e:
            logger.error(f"初始化历史数据库失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要"""
        try:
            summary = self.historical_collector.get_data_summary()
            
            return {
                'status': 'success',
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"获取数据摘要失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def export_historical_data(self, stock_codes: List[str] = None, 
                              sectors: List[str] = None,
                              start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """导出历史数据"""
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            export_data = {}
            
            # 导出股票数据
            if stock_codes:
                for stock_code in stock_codes:
                    data = get_stock_historical_data(stock_code, start_date, end_date)
                    if not data.empty:
                        export_data[stock_code] = data
            
            # 导出板块数据
            if sectors:
                for sector in sectors:
                    data = get_sector_historical_data(sector, start_date, end_date)
                    if data:
                        export_data[f"sector_{sector}"] = data
            
            # 导出到CSV
            if export_data:
                exported_files = self.historical_collector.export_data_to_csv(export_data)
                
                return {
                    'status': 'success',
                    'exported_files': exported_files,
                    'file_count': len(exported_files)
                }
            else:
                return {'status': 'error', 'message': '没有数据可导出'}
                
        except Exception as e:
            logger.error(f"导出历史数据失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_realtime_market_data(self) -> Dict[str, Any]:
        """获取实时市场数据"""
        try:
            market_overview = get_market_overview()
            sector_data = get_sector_realtime_data()
            
            return {
                'status': 'success',
                'market_overview': market_overview,
                'sector_data': sector_data,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"获取实时市场数据失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_hot_stocks(self, limit: int = 20) -> Dict[str, Any]:
        """获取热门股票"""
        try:
            hot_stocks = self.realtime_collector.get_hot_stocks(limit)
            
            return {
                'status': 'success',
                'hot_stocks': hot_stocks.to_dict('records') if not hot_stocks.empty else [],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_sector_ranking(self) -> Dict[str, Any]:
        """获取板块排名"""
        try:
            ranking = self.realtime_collector.get_sector_ranking()
            
            return {
                'status': 'success',
                'ranking': ranking.to_dict('records') if not ranking.empty else [],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"获取板块排名失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def start_realtime_monitoring(self, stock_codes: List[str] = None, 
                                sectors: List[str] = None, 
                                interval: int = 5):
        """启动实时监控"""
        try:
            self.realtime_collector.start_realtime_monitoring(
                stock_codes=stock_codes,
                sectors=sectors,
                interval=interval
            )
            logger.info("实时监控已启动")
            return {'status': 'success', 'message': '实时监控已启动'}
        except Exception as e:
            logger.error(f"启动实时监控失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def stop_realtime_monitoring(self):
        """停止实时监控"""
        try:
            self.realtime_collector.stop_realtime_monitoring()
            logger.info("实时监控已停止")
            return {'status': 'success', 'message': '实时监控已停止'}
        except Exception as e:
            logger.error(f"停止实时监控失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            'running': self.is_running,
            'models_trained': self.models_trained,
            'last_prediction_date': self.last_prediction_date,
            'registered_jobs': len(schedule.jobs),
            'realtime_monitoring': self.realtime_collector.is_running
        }
    
    def restart_models(self):
        """重新训练模型"""
        logger.info("开始重新训练模型...")
        self.models_trained = False
        
        try:
            result = self.initialize()
            if result['status'] == 'success':
                logger.info("模型重新训练完成")
                return {'status': 'success', 'message': '模型重新训练完成'}
            else:
                logger.error("模型重新训练失败")
                return {'status': 'error', 'message': '模型重新训练失败'}
        except Exception as e:
            logger.error(f"重新训练模型时发生错误: {e}")
            return {'status': 'error', 'message': str(e)}

# 便捷函数和API接口
def create_agent() -> AStockTradingAgent:
    """创建智能体实例"""
    return AStockTradingAgent()

def initialize_and_run():
    """初始化并运行智能体"""
    agent = create_agent()
    
    # 初始化
    init_result = agent.initialize()
    if init_result['status'] != 'success':
        logger.error(f"初始化失败: {init_result['message']}")
        return agent
    
    # 启动定时任务
    agent.start_scheduler()
    
    return agent

if __name__ == "__main__":
    # 创建智能体
    agent = initialize_and_run()
    
    # 如果初始化成功，保持运行
    if agent.models_trained:
        logger.info("智能体启动成功，正在运行...")
        try:
            while True:
                time.sleep(60)  # 每分钟检查一次状态
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止智能体...")
            agent.stop_scheduler()
            logger.info("智能体已停止")
    else:
        logger.error("智能体初始化失败，程序退出")
