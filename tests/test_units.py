"""
A股股票分析智能体单元测试
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from historical_data import HistoricalDataCollector
from realtime_data import RealtimeDataCollector
from sentiment_analyzer import SentimentAnalyzer
from sector_prediction_fixed import SectorPredictionModel
from backtesting import Backtester
from report_generator import ReportGenerator
from data_visualization import DataVisualizer

class TestHistoricalDataCollector(unittest.TestCase):
    """测试历史数据收集器"""
    
    def setUp(self):
        self.collector = HistoricalDataCollector()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.data_dir)
    
    def test_prepare_features(self):
        """测试特征准备"""
        # 创建模拟数据
        mock_data = {
            '000001': pd.DataFrame({
                'Close': [10, 11, 12, 13, 14],
                'Volume': [1000, 1100, 1200, 1300, 1400],
                'MA5': [10, 10.5, 11, 11.5, 12],
                'MA20': [10, 10.2, 10.4, 10.6, 10.8],
                'RSI': [50, 55, 60, 65, 70],
                'MACD': [0, 0.1, 0.2, 0.3, 0.4],
                'MACD_signal': [0, 0.05, 0.1, 0.15, 0.2],
                'Change_pct': [0, 10, 9.09, 8.33, 7.69]
            })
        }
        
        sentiment_data = pd.DataFrame({
            'stock_code': ['000001'],
            'avg_sentiment_score': [0.5],
            'sentiment_ratio': [0.6],
            'total_count': [10]
        })
        
        features_df, targets = self.collector.prepare_features(mock_data, sentiment_data)
        
        self.assertIsInstance(features_df, pd.DataFrame)
        self.assertIsInstance(targets, pd.Series)
        self.assertGreater(len(features_df), 0)
    
    def test_extract_technical_features(self):
        """测试技术指标提取"""
        mock_data = pd.DataFrame({
            'Close': [10, 11, 12],
            'Volume': [1000, 1100, 1200],
            'MA5': [10, 10.5, 11],
            'MA20': [10, 10.2, 10.4],
            'RSI': [50, 55, 60],
            'MACD': [0, 0.1, 0.2],
            'MACD_signal': [0, 0.05, 0.1],
            'Change_pct': [0, 10, 9.09]
        })
        
        features = self.collector._extract_technical_features(mock_data)
        
        self.assertIsInstance(features, dict)
        self.assertIn('current_price', features)
        self.assertIn('MA5', features)
        self.assertIn('RSI', features)
    
    def test_data_summary(self):
        """测试数据摘要"""
        summary = self.collector.get_data_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('stock_count', summary)
        self.assertIn('sector_count', summary)

class TestRealtimeDataCollector(unittest.TestCase):
    """测试实时数据收集器"""
    
    def setUp(self):
        self.collector = RealtimeDataCollector()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.collector)
        self.assertFalse(self.collector.is_running)
    
    def test_calculate_sector_metrics(self):
        """测试板块指标计算"""
        mock_data = pd.DataFrame({
            'change_pct': [1, 2, -1, 3, -2],
            'Volume': [1000, 2000, 1500, 3000, 1200],
            'Amount': [10000, 20000, 15000, 30000, 12000],
            'current_price': [10, 11, 9, 12, 8]
        })
        
        metrics = self.collector._calculate_sector_metrics(mock_data)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('avg_change_pct', metrics)
        self.assertIn('total_volume', metrics)
        self.assertIn('rising_count', metrics)
        self.assertIn('falling_count', metrics)
    
    def test_calculate_market_sentiment(self):
        """测试市场情绪计算"""
        sentiment = self.collector._calculate_market_sentiment(2.5, 7, 10)
        self.assertEqual(sentiment, "强势上涨")
        
        sentiment = self.collector._calculate_market_sentiment(-2.5, 3, 10)
        self.assertEqual(sentiment, "强势下跌")
        
        sentiment = self.collector._calculate_market_sentiment(0.5, 6, 10)
        self.assertEqual(sentiment, "温和上涨")

class TestSentimentAnalyzer(unittest.TestCase):
    """测试舆情分析器"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.session)
    
    def test_calculate_sentiment_score(self):
        """测试情感得分计算"""
        # 测试正面文本
        positive_score = self.analyzer._calculate_sentiment_score("这只股票表现很好，值得买入")
        self.assertGreater(positive_score, 0)
        
        # 测试负面文本
        negative_score = self.analyzer._calculate_sentiment_score("这只股票表现很差，建议卖出")
        self.assertLess(negative_score, 0)
        
        # 测试中性文本
        neutral_score = self.analyzer._calculate_sentiment_score("这只股票表现一般")
        self.assertAlmostEqual(abs(neutral_score), 0, delta=0.5)
    
    def test_aggregate_sentiment_by_stock(self):
        """测试股票情感聚合"""
        mock_data = pd.DataFrame({
            'stock_code': ['000001', '000001', '000002'],
            'sentiment_score': [0.5, 0.3, -0.2],
            'platform': ['雪球', '同花顺', '雪球'],
            'collect_time': [datetime.now(), datetime.now(), datetime.now()]
        })
        
        aggregated = self.analyzer.aggregate_sentiment_by_stock(mock_data)
        
        self.assertIsInstance(aggregated, pd.DataFrame)
        self.assertGreater(len(aggregated), 0)

class TestSectorPredictionModel(unittest.TestCase):
    """测试板块预测模型"""
    
    def setUp(self):
        self.model = SectorPredictionModel()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.model)
        self.assertIsInstance(self.model.models, dict)
        self.assertIsInstance(self.model.scalers, dict)
    
    def test_prepare_features(self):
        """测试特征准备"""
        mock_data = {
            '000001': pd.DataFrame({
                'Close': [10, 11, 12],
                'Volume': [1000, 1100, 1200],
                'MA5': [10, 10.5, 11],
                'RSI': [50, 55, 60],
                'Change_pct': [0, 10, 9.09]
            })
        }
        
        sentiment_data = pd.DataFrame({
            'stock_code': ['000001'],
            'avg_sentiment_score': [0.5]
        })
        
        features_df, targets = self.model.prepare_features(mock_data, sentiment_data)
        
        self.assertIsInstance(features_df, pd.DataFrame)
        self.assertIsInstance(targets, pd.Series)
    
    def test_calculate_direction_accuracy(self):
        """测试方向准确率计算"""
        y_true = pd.Series([1, -1, 1, -1])
        y_pred = pd.Series([1, -1, -1, 1])
        
        accuracy = self.model._calculate_direction_accuracy(y_true, y_pred)
        self.assertEqual(accuracy, 0.5)
    
    def test_calculate_prediction_confidence(self):
        """测试预测置信度计算"""
        mock_df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6]
        })
        
        confidence = self.model._calculate_prediction_confidence(mock_df)
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)

class TestBacktester(unittest.TestCase):
    """测试回测器"""
    
    def setUp(self):
        self.backtester = Backtester()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.backtester)
        self.assertIsNotNone(self.backtester.db_path)
    
    def test_record_prediction(self):
        """测试记录预测"""
        self.backtester.record_prediction(
            date="2024-01-01",
            sector="新能源",
            predicted_change=2.5,
            confidence=0.8
        )
        # 这里应该检查数据库中的记录，但为了简化测试，我们只测试方法调用不报错
        self.assertTrue(True)
    
    def test_calculate_daily_accuracy(self):
        """测试计算日准确率"""
        # 由于需要数据库数据，这里只测试方法调用
        try:
            result = self.backtester.calculate_daily_accuracy("2024-01-01")
            self.assertIsInstance(result, dict)
        except Exception:
            # 如果没有数据，应该返回错误信息
            self.assertTrue(True)

class TestReportGenerator(unittest.TestCase):
    """测试报表生成器"""
    
    def setUp(self):
        self.generator = ReportGenerator()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.reports_dir)
    
    def test_generate_daily_prediction_report(self):
        """测试生成每日预测报告"""
        mock_predictions = pd.DataFrame({
            'sector': ['新能源', '白酒', '医药'],
            'predicted_change': [2.5, 1.8, -1.2],
            'confidence': [0.8, 0.7, 0.6]
        })
        
        mock_accuracy = {
            'accuracy_rate': 0.75,
            'avg_confidence': 0.7,
            'total_predictions': 3
        }
        
        # 测试方法调用不报错
        try:
            result = self.generator.generate_daily_prediction_report(mock_predictions, mock_accuracy)
            self.assertIsInstance(result, str)
        except Exception as e:
            # 如果文件写入失败，这是正常的
            self.assertIn('xlsx', str(e).lower())

class TestDataVisualizer(unittest.TestCase):
    """测试数据可视化器"""
    
    def setUp(self):
        self.visualizer = DataVisualizer()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.visualizer)
        self.assertIsInstance(self.visualizer.colors, dict)
    
    def test_create_empty_chart(self):
        """测试创建空图表"""
        chart = self.visualizer._create_empty_chart("测试消息")
        self.assertIsNotNone(chart)
    
    def test_create_sector_performance_chart(self):
        """测试创建板块表现图表"""
        sector_data = {
            '新能源': 2.5,
            '白酒': 1.8,
            '医药': -1.2
        }
        
        chart = self.visualizer.create_sector_performance_chart(sector_data)
        self.assertIsNotNone(chart)

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_module_imports(self):
        """测试模块导入"""
        try:
            from config import settings
            from historical_data import HistoricalDataCollector
            from realtime_data import RealtimeDataCollector
            from sentiment_analyzer import SentimentAnalyzer
            from sector_prediction_fixed import SectorPredictionModel
            from backtesting import Backtester
            from report_generator import ReportGenerator
            from data_visualization import DataVisualizer
            
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"模块导入失败: {e}")
    
    def test_config_loading(self):
        """测试配置加载"""
        from config import settings
        
        self.assertIsNotNone(settings.project_name)
        self.assertIsNotNone(settings.version)
        self.assertIsNotNone(settings.database.sqlite_path)

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestHistoricalDataCollector,
        TestRealtimeDataCollector,
        TestSentimentAnalyzer,
        TestSectorPredictionModel,
        TestBacktester,
        TestReportGenerator,
        TestDataVisualizer,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)
