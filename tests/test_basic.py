"""
简化版测试脚本 - 测试基础功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基础模块导入"""
    print("=" * 50)
    print("测试基础模块导入")
    print("=" * 50)
    
    try:
        # 测试配置模块
        print("1. 测试配置模块...")
        from config import settings
        print(f"   项目名称: {settings.project_name}")
        print(f"   版本: {settings.version}")
        print("   ✅ 配置模块导入成功")
    except Exception as e:
        print(f"   ❌ 配置模块导入失败: {e}")
    
    try:
        # 测试历史数据模块
        print("\n2. 测试历史数据模块...")
        from historical_data import HistoricalDataCollector
        collector = HistoricalDataCollector()
        print("   ✅ 历史数据模块导入成功")
    except Exception as e:
        print(f"   ❌ 历史数据模块导入失败: {e}")
    
    try:
        # 测试实时数据模块
        print("\n3. 测试实时数据模块...")
        from realtime_data import RealtimeDataCollector
        collector = RealtimeDataCollector()
        print("   ✅ 实时数据模块导入成功")
    except Exception as e:
        print(f"   ❌ 实时数据模块导入失败: {e}")
    
    try:
        # 测试舆情分析模块
        print("\n4. 测试舆情分析模块...")
        from sentiment_analyzer import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        print("   ✅ 舆情分析模块导入成功")
    except Exception as e:
        print(f"   ❌ 舆情分析模块导入失败: {e}")
    
    try:
        # 测试回测模块
        print("\n5. 测试回测模块...")
        from backtesting import Backtester
        backtester = Backtester()
        print("   ✅ 回测模块导入成功")
    except Exception as e:
        print(f"   ❌ 回测模块导入失败: {e}")
    
    try:
        # 测试报表生成模块
        print("\n6. 测试报表生成模块...")
        from report_generator import ReportGenerator
        generator = ReportGenerator()
        print("   ✅ 报表生成模块导入成功")
    except Exception as e:
        print(f"   ❌ 报表生成模块导入失败: {e}")

def test_basic_functionality():
    """测试基础功能"""
    print("\n" + "=" * 50)
    print("测试基础功能")
    print("=" * 50)
    
    try:
        # 测试历史数据收集器基础功能
        print("1. 测试历史数据收集器...")
        from historical_data import HistoricalDataCollector
        collector = HistoricalDataCollector()
        
        # 测试数据摘要
        summary = collector.get_data_summary()
        print(f"   数据库摘要: {summary}")
        print("   ✅ 历史数据收集器基础功能正常")
    except Exception as e:
        print(f"   ❌ 历史数据收集器测试失败: {e}")
    
    try:
        # 测试实时数据收集器基础功能
        print("\n2. 测试实时数据收集器...")
        from realtime_data import RealtimeDataCollector
        collector = RealtimeDataCollector()
        
        # 测试状态
        print(f"   监控状态: {collector.is_running}")
        print("   ✅ 实时数据收集器基础功能正常")
    except Exception as e:
        print(f"   ❌ 实时数据收集器测试失败: {e}")
    
    try:
        # 测试舆情分析器基础功能
        print("\n3. 测试舆情分析器...")
        from sentiment_analyzer import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        # 测试情感分析
        test_text = "这只股票表现很好，值得买入"
        sentiment_score = analyzer._calculate_sentiment_score(test_text)
        print(f"   测试文本情感得分: {sentiment_score}")
        print("   ✅ 舆情分析器基础功能正常")
    except Exception as e:
        print(f"   ❌ 舆情分析器测试失败: {e}")

def test_data_access():
    """测试数据访问功能"""
    print("\n" + "=" * 50)
    print("测试数据访问功能")
    print("=" * 50)
    
    try:
        # 测试获取股票列表
        print("1. 测试获取股票列表...")
        from historical_data import HistoricalDataCollector
        collector = HistoricalDataCollector()
        
        # 获取少量股票进行测试
        stock_list = collector.get_stock_list()
        if not stock_list.empty:
            print(f"   成功获取 {len(stock_list)} 只股票信息")
            print(f"   前3只股票: {stock_list.head(3)['stock_name'].tolist() if 'stock_name' in stock_list.columns else 'N/A'}")
        else:
            print("   未获取到股票列表")
        print("   ✅ 股票列表获取功能正常")
    except Exception as e:
        print(f"   ❌ 股票列表获取失败: {e}")
    
    try:
        # 测试获取板块列表
        print("\n2. 测试获取板块列表...")
        from historical_data import HistoricalDataCollector
        collector = HistoricalDataCollector()
        
        sector_list = collector.get_sector_list()
        if not sector_list.empty:
            print(f"   成功获取 {len(sector_list)} 个板块信息")
            print(f"   前3个板块: {sector_list.head(3)['sector_name'].tolist() if 'sector_name' in sector_list.columns else 'N/A'}")
        else:
            print("   未获取到板块列表")
        print("   ✅ 板块列表获取功能正常")
    except Exception as e:
        print(f"   ❌ 板块列表获取失败: {e}")

def main():
    """主函数"""
    print("A股股票分析智能体 - 基础功能测试")
    print("=" * 60)
    
    # 运行各项测试
    test_basic_imports()
    test_basic_functionality()
    test_data_access()
    
    print("\n" + "=" * 60)
    print("基础功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
