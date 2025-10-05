"""
实时数据获取模块使用示例
演示如何使用实时数据获取功能
"""
import time
from realtime_data import RealtimeDataCollector, get_market_overview, get_sector_realtime_data

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建数据收集器
    collector = RealtimeDataCollector()
    
    # 获取指定股票的实时行情
    stock_codes = ['000001', '000002', '600000', '600036']  # 示例股票代码
    realtime_quotes = collector.get_realtime_quotes(stock_codes)
    
    if not realtime_quotes.empty:
        print("指定股票实时行情:")
        for _, stock in realtime_quotes.iterrows():
            print(f"  {stock['stock_name']}({stock['stock_code']}): "
                  f"{stock['current_price']:.2f} ({stock['change_pct']:+.2f}%)")
    else:
        print("未获取到股票数据")

def example_sector_monitoring():
    """板块监控示例"""
    print("\n=== 板块监控示例 ===")
    
    # 获取主要板块的实时数据
    sectors = ['新能源', '白酒', '医药', '科技', '金融', '地产']
    sector_data = get_sector_realtime_data(sectors)
    
    if sector_data:
        print("板块实时表现:")
        for sector, data in sector_data.items():
            print(f"  {sector}:")
            print(f"    平均涨跌幅: {data['avg_change_pct']:+.2f}%")
            print(f"    上涨股票: {data['rising_count']}只")
            print(f"    下跌股票: {data['falling_count']}只")
            print(f"    市场情绪: {data['market_sentiment']}")
            print(f"    总成交额: {data['total_amount']:.0f}万元")
            print()

def example_market_overview():
    """市场概览示例"""
    print("\n=== 市场概览示例 ===")
    
    market_data = get_market_overview()
    
    if market_data:
        # 显示主要指数
        print("主要指数表现:")
        for index_name, data in market_data.get('indices', {}).items():
            print(f"  {index_name}: {data['current_price']:.2f} "
                  f"({data['change_pct']:+.2f}%)")
        
        # 显示市场统计
        stats = market_data.get('market_stats', {})
        if stats:
            print(f"\n市场统计:")
            print(f"  总股票数: {stats.get('total_stocks', 0)}")
            print(f"  上涨股票: {stats.get('rising_stocks', 0)} "
                  f"({stats.get('rising_stocks', 0)/stats.get('total_stocks', 1)*100:.1f}%)")
            print(f"  下跌股票: {stats.get('falling_stocks', 0)} "
                  f"({stats.get('falling_stocks', 0)/stats.get('total_stocks', 1)*100:.1f}%)")
            print(f"  涨停股票: {stats.get('limit_up', 0)}")
            print(f"  跌停股票: {stats.get('limit_down', 0)}")
            print(f"  平均涨跌幅: {stats.get('avg_change_pct', 0):.2f}%")

def example_realtime_monitoring():
    """实时监控示例"""
    print("\n=== 实时监控示例 ===")
    
    collector = RealtimeDataCollector()
    
    # 启动实时监控（监控5秒）
    print("启动实时监控，监控5秒...")
    collector.start_realtime_monitoring(
        stock_codes=['000001', '000002'],  # 监控指定股票
        sectors=['新能源', '白酒'],  # 监控指定板块
        interval=2  # 每2秒更新一次
    )
    
    # 监控5秒
    time.sleep(5)
    
    # 停止监控
    collector.stop_realtime_monitoring()
    print("实时监控已停止")

def example_hot_stocks():
    """热门股票示例"""
    print("\n=== 热门股票示例 ===")
    
    collector = RealtimeDataCollector()
    
    # 获取成交额前20的股票
    hot_stocks = collector.get_hot_stocks(limit=20)
    
    if not hot_stocks.empty:
        print("成交额前20名股票:")
        for _, stock in hot_stocks.iterrows():
            print(f"  {stock['rank']:2d}. {stock['stock_name']}({stock['stock_code']}) "
                  f"{stock['current_price']:6.2f} ({stock['change_pct']:+5.2f}%) "
                  f"成交额: {stock['amount']:8.0f}万")

def example_sector_ranking():
    """板块排名示例"""
    print("\n=== 板块排名示例 ===")
    
    collector = RealtimeDataCollector()
    
    # 获取板块涨跌幅排名
    ranking = collector.get_sector_ranking()
    
    if not ranking.empty:
        print("板块涨跌幅排名:")
        print("  排名  板块名称      涨跌幅    上涨  下跌  情绪")
        print("  " + "-" * 50)
        
        for _, sector in ranking.head(15).iterrows():
            print(f"  {sector['rank']:2d}. {sector['sector']:8s} "
                  f"{sector['avg_change_pct']:+6.2f}% "
                  f"{sector['rising_count']:4d} {sector['falling_count']:4d} "
                  f"{sector['market_sentiment']}")

def main():
    """主函数"""
    print("A股实时数据获取模块使用示例")
    print("=" * 60)
    
    try:
        # 运行各种示例
        example_basic_usage()
        example_sector_monitoring()
        example_market_overview()
        example_hot_stocks()
        example_sector_ranking()
        
        # 实时监控示例（可选，会运行5秒）
        # example_realtime_monitoring()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成")
        
    except Exception as e:
        print(f"运行示例时出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
