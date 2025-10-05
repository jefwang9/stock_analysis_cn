"""
历史数据获取模块测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from historical_data import HistoricalDataCollector, get_stock_historical_data, get_sector_historical_data
import pandas as pd
from datetime import datetime, timedelta

def test_historical_data():
    """测试历史数据获取功能"""
    print("=" * 60)
    print("A股历史数据获取模块测试")
    print("=" * 60)
    
    # 创建数据收集器
    collector = HistoricalDataCollector()
    
    # 1. 测试获取股票列表
    print("\n1. 获取股票列表...")
    stock_list = collector.get_stock_list()
    
    if not stock_list.empty:
        print(f"成功获取 {len(stock_list)} 只股票信息")
        print("前5只股票:")
        for _, stock in stock_list.head().iterrows():
            print(f"  {stock['stock_code']} - {stock['stock_name']}")
    else:
        print("获取股票列表失败")
    
    # 2. 测试获取板块列表
    print("\n2. 获取板块列表...")
    sector_list = collector.get_sector_list()
    
    if not sector_list.empty:
        print(f"成功获取 {len(sector_list)} 个板块信息")
        print("前5个板块:")
        for _, sector in sector_list.head().iterrows():
            print(f"  {sector['sector_name']} - {sector['sector_type']} ({sector['stock_count']}只股票)")
    else:
        print("获取板块列表失败")
    
    # 3. 测试获取单只股票历史数据
    print("\n3. 获取单只股票历史数据...")
    test_stock = "000001"  # 平安银行
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    stock_data = get_stock_historical_data(test_stock, start_date, end_date)
    
    if not stock_data.empty:
        print(f"成功获取 {test_stock} 从 {start_date} 到 {end_date} 的历史数据")
        print(f"数据行数: {len(stock_data)}")
        print("最新5个交易日数据:")
        print(stock_data.tail().to_string())
        
        # 检查技术指标
        print(f"\n技术指标列: {[col for col in stock_data.columns if col.startswith(('MA', 'RSI', 'MACD', 'KDJ', 'BOLL', 'WR'))]}")
    else:
        print(f"获取 {test_stock} 历史数据失败")
    
    # 4. 测试获取板块股票列表
    print("\n4. 获取板块股票列表...")
    test_sector = "新能源"
    sector_stocks = collector.get_sector_stocks(test_sector)
    
    if sector_stocks:
        print(f"板块 {test_sector} 包含 {len(sector_stocks)} 只股票")
        print(f"前10只股票: {sector_stocks[:10]}")
    else:
        print(f"获取板块 {test_sector} 股票列表失败")
    
    # 5. 测试获取板块历史数据（小规模测试）
    print("\n5. 获取板块历史数据（小规模测试）...")
    if sector_stocks:
        # 只测试前3只股票
        test_stocks = sector_stocks[:3]
        print(f"测试板块 {test_sector} 的前3只股票: {test_stocks}")
        
        sector_data = collector.get_multiple_stocks_data(test_stocks, start_date, end_date)
        
        if sector_data:
            print(f"成功获取 {len(sector_data)} 只股票的历史数据")
            for stock_code, data in sector_data.items():
                print(f"  {stock_code}: {len(data)} 个交易日数据")
        else:
            print("获取板块历史数据失败")
    
    # 6. 测试数据摘要
    print("\n6. 获取数据摘要...")
    summary = collector.get_data_summary()
    
    if summary:
        print("数据库摘要信息:")
        print(f"  股票数量: {summary.get('stock_count', 0)}")
        print(f"  板块数量: {summary.get('sector_count', 0)}")
        print(f"  历史记录数: {summary.get('daily_records', 0)}")
        date_range = summary.get('date_range', {})
        print(f"  数据日期范围: {date_range.get('start_date', 'N/A')} 到 {date_range.get('end_date', 'N/A')}")
        print(f"  最后更新: {summary.get('last_update', 'N/A')}")
    else:
        print("获取数据摘要失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

def test_specific_stocks():
    """测试特定股票的历史数据"""
    print("\n" + "=" * 60)
    print("特定股票历史数据测试")
    print("=" * 60)
    
    # 测试一些知名股票
    test_stocks = [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("600000", "浦发银行"),
        ("600036", "招商银行"),
        ("000858", "五粮液")
    ]
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    collector = HistoricalDataCollector()
    
    for stock_code, stock_name in test_stocks:
        print(f"\n测试股票: {stock_name}({stock_code})")
        
        try:
            data = collector.get_stock_historical_data(stock_code, start_date, end_date)
            
            if not data.empty:
                print(f"  数据行数: {len(data)}")
                print(f"  最新价格: {data['Close'].iloc[-1]:.2f}")
                print(f"  期间涨跌幅: {((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100:.2f}%")
                print(f"  最高价: {data['High'].max():.2f}")
                print(f"  最低价: {data['Low'].min():.2f}")
                print(f"  平均成交量: {data['Volume'].mean():.0f}")
                
                # 检查技术指标
                latest = data.iloc[-1]
                print(f"  最新MA5: {latest.get('MA5', 0):.2f}")
                print(f"  最新RSI: {latest.get('RSI', 0):.2f}")
            else:
                print(f"  未获取到数据")
                
        except Exception as e:
            print(f"  获取数据失败: {e}")

def test_sector_data():
    """测试板块数据获取"""
    print("\n" + "=" * 60)
    print("板块数据获取测试")
    print("=" * 60)
    
    # 测试主要板块
    test_sectors = ["新能源", "白酒", "医药", "科技", "金融"]
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    collector = HistoricalDataCollector()
    
    for sector in test_sectors:
        print(f"\n测试板块: {sector}")
        
        try:
            # 获取板块股票列表
            stocks = collector.get_sector_stocks(sector)
            
            if stocks:
                print(f"  板块股票数量: {len(stocks)}")
                print(f"  前5只股票: {stocks[:5]}")
                
                # 获取前3只股票的历史数据作为示例
                sample_stocks = stocks[:3]
                sector_data = collector.get_multiple_stocks_data(sample_stocks, start_date, end_date)
                
                if sector_data:
                    print(f"  成功获取 {len(sector_data)} 只股票的历史数据")
                    
                    # 计算板块平均表现
                    total_change = 0
                    valid_stocks = 0
                    
                    for stock_code, data in sector_data.items():
                        if len(data) > 0:
                            change_pct = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
                            total_change += change_pct
                            valid_stocks += 1
                    
                    if valid_stocks > 0:
                        avg_change = total_change / valid_stocks
                        print(f"  样本股票平均涨跌幅: {avg_change:.2f}%")
                else:
                    print("  未获取到股票历史数据")
            else:
                print(f"  未找到板块 {sector} 的股票")
                
        except Exception as e:
            print(f"  测试板块 {sector} 失败: {e}")

if __name__ == "__main__":
    try:
        # 基础功能测试
        test_historical_data()
        
        # 特定股票测试
        test_specific_stocks()
        
        # 板块数据测试
        test_sector_data()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
