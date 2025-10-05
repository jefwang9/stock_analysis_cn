"""
回测和准确率追踪模块
跟踪和评估板块预测模型的准确性
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any, Optional
import sqlite3
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class Backtester:
    """板块预测回测器"""
    
    def __init__(self):
        self.db_path = settings.database.sqlite_path
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        conn = sqlite3.connect(self.db_path)
        
        # 预测记录表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            sector TEXT NOT NULL,
            predicted_change REAL NOT NULL,
            actual_change REAL,
            confidence REAL,
            is_correct BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 板块表现表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sector_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            sector TEXT NOT NULL,
            actual_change REAL NOT NULL,
            top_gainer BOOLEAN DEFAULT FALSE,
            top_loser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 准确率统计表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS accuracy_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            total_predictions INTEGER,
            correct_predictions INTEGER,
            accuracy_rate REAL,
            avg_confident REAL,
            top_gainer_accuracy REAL,
            top_loser_accuracy REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_prediction(self, date: str, sector: str, predicted_change: float, 
                         confidence: float = 0.0):
        """
        记录预测结果
        
        Args:
            date: 预测日期
            sector: 板块名称
            predicted_change: 预测涨跌幅
            confidence: 预测置信度
        """
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
        INSERT INTO predictions (date, sector, predicted_change, confidence)
        VALUES (?, ?, ?, ?)
        ''', (date, sector, predicted_change, confidence))
        
        conn.commit()
        conn.close()
        
        logger.info(f"已记录 {date} {sector} 的预测结果")
    
    def update_actual_result(self, date: str, sector: str, actual_change: float):
        """
        更新实际结果
        
        Args:
            date: 交易日
            sector: 板块名称
            actual_change: 实际涨跌幅
        """
        conn = sqlite3.connect(self.db_path)
        
        # 更新预测记录
        conn.execute('''
        UPDATE predictions 
        SET actual_change = ?, is_correct = ?
        WHERE date = ? AND sector = ?
        ''', (actual_change, self._determine_direction_correct(actual_change, conn.execute('SELECT predicted_change FROM predictions WHERE date = ? AND sector = ?', (date, sector)).fetchone()), date, sector))
        
        # 记录板块表现
        # 计算该日期的top gainer/loser
        all_changes = conn.execute('SELECT actual_change FROM sector_performance WHERE date = ?', (date,)).fetchall()
        
        if all_changes:
            changes_list = [c[0] for c in all_changes]
            top_gainer_threshold = np.percentile(changes_list, 75)  # 75分位数为强势
            top_loser_threshold = np.percentile(changes_list, 25)  # 25分位数为弱势
        else:
            top_gainer_threshold = 2.0  # 默认阈值
            top_loser_threshold = -2.0
        
        is_top_gainer = actual_change >= top_gainer_threshold
        is_top_loser = actual_change <= top_loser_threshold
        
        conn.execute('''
        INSERT OR REPLACE INTO sector_performance (date, sector, actual_change, top_gainer, top_loser)
        VALUES (?, ?, ?, ?, ?)
        ''', (date, sector, actual_change, is_top_gainer, is_top_loser))
        
        conn.commit()
        conn.close()
        
        logger.info(f"已更新 {date} {sector} 的实际结果: {actual_change:.2f}%")
    
    def _determine_direction_correct(self, actual_change: float, predicted_change_tuple) -> bool:
        """判断方向预测是否正确"""
        if not predicted_change_tuple:
            return False
        
        predicted_change = predicted_change_tuple[0]
        actual_direction = np.sign(actual_change)
        predicted_direction = np.sign(predicted_change)
        
        return actual_direction == predicted_direction
    
    def calculate_daily_accuracy(self, date: str) -> Dict[str, Any]:
        """
        计算指定日期的预测准确率
        
        Args:
            date: 日期字符串
            
        Returns:
            Dict: 准确率统计
        """
        conn = sqlite3.connect(self.db_path)
        
        # 获取当天的预测记录
        predictions = pd.read_sql_query('''
        SELECT * FROM predictions 
        WHERE date = ? AND actual_change IS NOT NULL
        ''', conn, params=(date,))
        
        if predictions.empty:
            conn.close()
            return {'error': '没有找到当天的预测记录'}
        
        # 计算总体准确率
        total_predictions = len(predictions)
        correct_predictions = len(predictions[predictions['is_correct'] == True])
        overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # 计算top gainer预测准确率
        top_gainer_predictions = predictions[
            (predictions['predicted_change'] > 0) & 
            (predictions['predicted_change'].rank(ascending=False) <= settings.trading.predict_top_n)
        ]
        
        top_gainer_accuracy = 0
        if not top_gainer_predictions.empty:
            actual_top_gainers = predictions[predictions['actual_change'] >= predictions['actual_change'].quantile(0.75)]
            top_gainer_correct = len(set(top_gainer_predictions['sector']) & set(actual_top_gainers['sector']))
            top_gainer_accuracy = top_gainer_correct / len(top_gainer_predictions) if len(top_gainer_predictions) > 0 else 0
        
        # 计算top loser预测准确率
        top_loser_predictions = predictions[
            (predictions['predicted_change'] < 0) & 
            (predictions['predicted_change'].rank(ascending=True) <= settings.trading.predict_bottom_n)
        ]
        
        top_loser_accuracy = 0
        if not top_loser_predictions.empty:
            actual_top_losers = predictions[predictions['actual_change'] <= predictions['actual_change'].quantile(0.25)]
            top_loser_correct = len(set(top_loser_predictions['sector']) & set(actual_top_losers['sector']))
            top_loser_accuracy = top_loser_correct / len(top_loser_predictions) if len(top_loser_predictions) > 0 else 0
        
        # 计算平均置信度
        avg_confidence = predictions['confidence'].mean()
        
        conn.close()
        
        accuracy_stats = {
            'date': date,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'accuracy_rate': overall_accuracy,
            'avg_confidence': avg_confidence,
            'top_gainer_accuracy': top_gainer_accuracy,
            'top_loser_accuracy': top_loser_accuracy
        }
        
        # 保存到数据库
        self._save_accuracy_stats(accuracy_stats)
        
        logger.info(f"{date} 预测准确率: {overall_accuracy:.2%}")
        
        return accuracy_stats
    
    def _save_accuracy_stats(self, stats: Dict[str, Any]):
        """保存准确率统计到数据库"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
        INSERT INTO accuracy_stats 
        (date, total_predictions, correct_predictions, accuracy_rate, 
         avg_confidence, top_gainer_accuracy, top_loser_accuracy)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (stats['date'], stats['total_predictions'], stats['correct_predictions'],
              stats['accuracy_rate'], stats['avg_confidence'], 
              stats['top_gainer_accuracy'], stats['top_loser_accuracy']))
        
        conn.commit()
        conn.close()
    
    def get_performance_report(self, days: int = 30) -> pd.DataFrame:
        """
        生成性能报告
        
        Args:
            days: 统计天数
            
        Returns:
            DataFrame: 性能报告
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        
        # 获取准确率统计数据
        accuracy_data = pd.read_sql_query('''
        SELECT * FROM accuracy_stats 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
        ''', conn, params=(start_date, end_date))
        
        conn.close()
        
        if accuracy_data.empty:
            logger.warning("没有找到足够的历史数据进行报表分析")
            return pd.DataFrame()
        
        return accuracy_data
    
    def get_sector_performance_report(self, sector: str, days: int = 30) -> Dict[str, Any]:
        """
        生成特定板块的性能报告
        
        Args:
            sector: 板块名称
            days: 统计天数
            
        Returns:
            Dict: 板块性能报告
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        
        # 获取板块预测记录
        predictions = pd.read_sql_query('''
        SELECT * FROM predictions 
        WHERE sector = ? AND date BETWEEN ? AND ?
        AND actual_change IS NOT NULL
        ORDER BY date DESC
        ''', conn, params=(sector, start_date, end_date))
        
        conn.close()
        
        if predictions.empty:
            return {'error': f'板块 {sector} 没有足够的历史数据'}
        
        # 计算各项指标
        total_predictions = len(predictions)
        correct_predictions = len(predictions[predictions['is_correct'] == True])
        accuracy_rate = correct_predictions / total_predictions
        
        # 方向预测准确性
        positive_correct = len(predictions[
            (predictions['predicted_change'] >= 0) & 
            (predictions['actual_change'] >= 0)
        ])
        negative_correct = len(predictions[
            (predictions['predicted_change'] < 0) & 
            (predictions['actual_change'] < 0)
        ])
        
        positive_total = len(predictions[predictions['predicted_change'] >= 0])
        negative_total = len(predictions[predictions['predicted_change'] < 0])
        
        positive_accuracy = positive_correct / positive_total if positive_total > 0 else 0
        negative_accuracy = negative_correct / negative_total if negative_total > 0 else 0
        
        # 收益率分析
        mae = np.mean(np.abs(predictions['predicted_change'] - predictions['actual_change']))
        rmse = np.sqrt(np.mean((predictions['predicted_change'] - predictions['actual_change']) ** 2))
        
        return {
            'sector': sector,
            'period': f"{start_date} 到 {end_date}",
            'total_predictions': total_predictions,
            'accuracy_rate': accuracy_rate,
            'positive_accuracy': positive_accuracy,
            'negative_accuracy': negative_accuracy,
            'mae': mae,
            'rmse': rmse,
            'avg_predicted_change': predictions['predicted_change'].mean(),
            'actual_change': predictions['actual_change'].mean(),
            'confidence': predictions['confidence'].mean()
        }
    
    def generate_comprehensive_report(self, days: int = 30) -> Dict[str, Any]:
        """
        生成综合报告
        
        Args:
            days: 统计天数
            
        Returns:
            Dict: 综合报告
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        
        # 总体统计
        overall_stats = pd.read_sql_query('''
        SELECT 
            COUNT(*) as total_predictions,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_predictions,
            AVG(confidence) as avg_confidence,
            COUNT(DISTINCT sector) as sectors_counted
        FROM predictions 
        WHERE date BETWEEN ? AND ? AND actual_change IS NOT NULL
        ''', conn, params=(start_date, end_date))
        
        conn.close()
        
        # 性能趋势
        performance_trend = self.get_performance_report(days)
        
        # 热门板块分析
        hot_sectors = self._analyze_hot_sectors(start_date, end_date)
        
        # 模型改进建议
        improvement_suggestions = self._generate_improvement_suggestions(performance_trend)
        
        return {
            'report_period': f"{start_date} 到 {end_date}",
            'overall_statistics': overall_stats.iloc[0].to_dict() if not overall_stats.empty else {},
            'performance_trend': performance_trend.to_dict('records') if not performance_trend.empty else [],
            'hot_sectors': hot_sectors,
            'improvement_suggestions': improvement_suggestions,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_hot_sectors(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """分析热门板块"""
        conn = sqlite3.connect(self.db_path)
        
        hot_sectors = pd.read_sql_query('''
        SELECT 
            sector,
            COUNT(*) as prediction_count,
            AVG(CASE WHEN is_correct = 1 THEN 1.0 ELSE 0.0 END) as accuracy,
            SUM(ABS(predicted_change)) as total_potential,
            AVG(confidence) as avg_confidence
        FROM predictions 
        WHERE date BETWEEN ? AND ?
        GROUP BY sector
        HAVING COUNT(*) > 0
        ORDER BY prediction_count DESC, accuracy DESC
        LIMIT 10
        ''', conn, params=(start_date, end_date))
        
        conn.close()
        
        return hot_sectors.to_dict('records')
    
    def _generate_improvement_suggestions(self, performance_trend: pd.DataFrame) -> List[str]:
        """生成模型改进建议"""
        suggestions = []
        
        if performance_trend.empty:
            return suggestions
        
        # 分析趋势
        recent_accuracy = performance_trend['accuracy_rate'].mean()
        
        if recent_accuracy < 0.5:
            suggestions.append("总体准确率偏低，建议检查数据质量和特征工程")
        
        if recent_accuracy > 0.7:
            suggestions.append("模型表现良好，可以考虑增加预测频率")
        
        # 分析置信度
        avg_confidence = performance_trend['avg_confidence'].mean()
        if avg_confidence < 0.6:
            suggestions.append("平均置信度较低，建议提高特征选择质量")
        
        # 分析top gainer/loser准确率
        top_gainer_acc = performance_trend['top_gainer_accuracy'].mean()
        top_loser_acc = performance_trend['top_loser_accuracy'].mean()
        
        if top_gainer_acc < 0.4:
            suggestions.append("上涨板块预测准确率偏低，建议增强牛市信号识别")
        
        if top_loser_acc < 0.4:
            suggestions.append("下跌板块预测准确率偏低，建议增强熊市信号识别")
        
        if not suggestions:
            suggestions.append("模型运行正常，暂无特别改进建议")
        
        return suggestions

# 便捷函数
def daily_backtest_update(date: str, predictions_df: pd.DataFrame, 
                         actual_performances: Dict[str, float]):
    """每日回测更新"""
    backtester = Backtester()
    
    # 记录预测结果
    for _, row in predictions_df.iterrows():
        backtester.record_prediction(
            date=date,
            sector=row['sector'],
            predicted_change=row['predicted_change'],
            confidence=row.get('confidence', 0.0)
        )
    
    # 更新实际结果
    for sector, actual_change in actual_performances.items():
        backtester.update_actual_result(date, sector, actual_change)
    
    # 计算当日准确率
    accuracy_stats = backtester.calculate_daily_accuracy(date)
    
    logger.info(f"{date} 回测更新完成，准确率: {accuracy_stats.get('accuracy_rate', 0):.2%}")
    
    return accuracy_stats

def generate_period_report(days: int = 30) -> Dict[str, Any]:
    """生成期间报告"""
    backtester = Backtester()
    return backtester.generate_comprehensive_report(days)
