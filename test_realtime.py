"""
实时数据获取模块测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realtime_data import RealtimeDataCollector, get_market_overview, get_sector_realtime_data
import pandas as pd
from datetime import datetime

def test_realtime_data():
    """测试实时数据获取功能"""
    print("=" * 50)
    print("A股实时数据获取模块测试")
    print("=" * 50)
    
    # 创建数据收集器
    collector = RealtimeDataCollector()
    
    # 1. 测试获取市场概览
    print("\n1. 获取市场概览...")
    market_overview = get_market_overview()
    
    if market_overview:
        print("主要指数:")
        for index_name, data in market_overview.get('indices', {}).items():
            print(f"  {index_name}: {data['current_price']:.2f} "
                  f"({data['change_pct']:+.2f}%)")
        
        stats = market_overview.get('market_stats', {})
        if stats:
            print(f"\n市场统计:")
            print(f"  总股票数: {stats.get('total_stocks', 0)}")
            print(f"  上涨股票: {stats.get('rising_stocks', 0)}")
            print(f"  下跌股票: {stats.get('falling_stocks', 0)}")
            print(f"  涨停股票: {stats.get('limit_up', 0)}")
            print(f"  跌停股票: {stats.get('limit_down', 0)}")
            print(f"  平均涨跌幅: {stats.get('avg_change_pct', 0):.2f}%")
    else:
        print("获取市场概览失败")
    
    # 2. 测试获取板块实时数据
    print("\n2. 获取板块实时数据...")
    sectors = ['新能源', '白酒', '医药', '科技', '金融']
    sector_data = get_sector_realtime_data(sectors)
    
    if sector_data:
        print("板块实时数据:")
        for sector, data in sector_data.items():
            print(f"  {sector}: {data['avg_change_pct']:+.2f}% "
                  f"(上涨{data['rising_count']}只, 下跌{data['falling_count']}只) "
                  f"- {data['market_sentiment']}")
    else:
        print("获取板块数据失败")
    
    # 3. 测试获取热门股票
    print("\n3. 获取热门股票...")
    hot_stocks = collector.get_hot_stocks(limit=10)
    
    if not hot_stocks.empty:
        print("成交额前10名:")
        for _, stock in hot_stocks.iterrows():
            print(f"  {stock['rank']}. {stock['stock_name']}({stock['stock_code']}) "
                  f"{stock['current_price']:.2f} ({stock['change_pct']:+.2f}%) "
                  f"成交额: {stock['amount']:.0f}万")
    else:
        print("获取热门股票失败")
    
    # 4. 测试板块排名
    print("\n4. 获取板块涨跌幅排名...")
    sector_ranking = collector.get_sector_ranking()
    
    if not sector_ranking.empty:
        print("板块涨跌幅排名 (前10名):")
        for _, sector in sector_ranking.head(10).iterrows():
            print(f"  {sector['rank']}. {sector['sector']}: {sector['avg_change_pct']:+.2f}% "
                  f"- {sector['market_sentiment']}")
    else:
        print("获取板块排名失败")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_realtime_data()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
