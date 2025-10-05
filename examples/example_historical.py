"""
历史数据获取模块使用示例
演示如何使用历史数据获取功能
"""
import pandas as pd
from datetime import datetime, timedelta
from historical_data import (
    HistoricalDataCollector, 
    get_stock_historical_data, 
    get_sector_historical_data,
    get_all_sectors_historical_data,
    initialize_historical_database
)

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建数据收集器
    collector = HistoricalDataCollector()
    
    # 获取单只股票历史数据
    stock_code = "000001"  # 平安银行
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"获取 {stock_code} 从 {start_date} 到 {end_date} 的历史数据...")
    
    stock_data = get_stock_historical_data(stock_code, start_date, end_date)
    
    if not stock_data.empty:
        print(f"成功获取 {len(stock_data)} 个交易日数据")
        print("最新5个交易日:")
        print(stock_data.tail()[['Close', 'Volume', 'Change_pct']].to_string())
    else:
        print("未获取到数据")

def example_sector_analysis():
    """板块分析示例"""
    print("\n=== 板块分析示例 ===")
    
    # 获取板块历史数据
    sector_name = "新能源"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    print(f"分析板块: {sector_name}")
    
    sector_data = get_sector_historical_data(sector_name, start_date, end_date)
    
    if sector_data:
        print(f"板块包含 {len(sector_data)} 只股票")
        
        # 分析板块表现
        sector_performance = []
        
        for stock_code, data in sector_data.items():
            if len(data) > 0:
                # 计算期间涨跌幅
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                change_pct = ((end_price / start_price) - 1) * 100
                
                # 计算波动率
                volatility = data['Close'].pct_change().std() * 100
                
                sector_performance.append({
                    'stock_code': stock_code,
                    'change_pct': change_pct,
                    'volatility': volatility,
                    'avg_volume': data['Volume'].mean()
                })
        
        # 转换为DataFrame分析
        perf_df = pd.DataFrame(sector_performance)
        
        if not perf_df.empty:
            print(f"\n板块表现分析:")
            print(f"  平均涨跌幅: {perf_df['change_pct'].mean():.2f}%")
            print(f"  涨跌幅标准差: {perf_df['change_pct'].std():.2f}%")
            print(f"  上涨股票数: {len(perf_df[perf_df['change_pct'] > 0])}")
            print(f"  下跌股票数: {len(perf_df[perf_df['change_pct'] < 0])}")
            
            # 显示表现最好和最差的股票
            best_stocks = perf_df.nlargest(3, 'change_pct')
            worst_stocks = perf_df.nsmallest(3, 'change_pct')
            
            print(f"\n表现最好的3只股票:")
            for _, stock in best_stocks.iterrows():
                print(f"  {stock['stock_code']}: {stock['change_pct']:+.2f}%")
            
            print(f"\n表现最差的3只股票:")
            for _, stock in worst_stocks.iterrows():
                print(f"  {stock['stock_code']}: {stock['change_pct']:+.2f}%")
    else:
        print("未获取到板块数据")

def example_batch_data_collection():
    """批量数据收集示例"""
    print("\n=== 批量数据收集示例 ===")
    
    collector = HistoricalDataCollector()
    
    # 获取主要板块的历史数据
    sectors = ["新能源", "白酒", "医药"]
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"批量获取 {len(sectors)} 个板块的历史数据...")
    
    all_sectors_data = get_all_sectors_historical_data(start_date, end_date, sectors)
    
    if all_sectors_data:
        print(f"成功获取 {len(all_sectors_data)} 个板块的数据")
        
        # 分析各板块表现
        sector_summary = []
        
        for sector_name, stocks_data in all_sectors_data.items():
            if stocks_data:
                # 计算板块平均表现
                total_change = 0
                valid_stocks = 0
                
                for stock_code, data in stocks_data.items():
                    if len(data) > 0:
                        change_pct = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
                        total_change += change_pct
                        valid_stocks += 1
                
                if valid_stocks > 0:
                    avg_change = total_change / valid_stocks
                    sector_summary.append({
                        'sector': sector_name,
                        'stock_count': len(stocks_data),
                        'avg_change_pct': avg_change
                    })
        
        # 显示板块排名
        if sector_summary:
            summary_df = pd.DataFrame(sector_summary)
            summary_df = summary_df.sort_values('avg_change_pct', ascending=False)
            
            print(f"\n板块表现排名:")
            for i, (_, sector) in enumerate(summary_df.iterrows(), 1):
                print(f"  {i}. {sector['sector']}: {sector['avg_change_pct']:+.2f}% "
                      f"({sector['stock_count']}只股票)")
    else:
        print("未获取到板块数据")

def example_technical_analysis():
    """技术分析示例"""
    print("\n=== 技术分析示例 ===")
    
    # 获取一只股票的历史数据
    stock_code = "000858"  # 五粮液
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print(f"技术分析: {stock_code}")
    
    stock_data = get_stock_historical_data(stock_code, start_date, end_date)
    
    if not stock_data.empty:
        latest = stock_data.iloc[-1]
        
        print(f"最新交易日: {latest.name.strftime('%Y-%m-%d')}")
        print(f"收盘价: {latest['Close']:.2f}")
        print(f"涨跌幅: {latest['Change_pct']:+.2f}%")
        
        # 技术指标分析
        print(f"\n技术指标:")
        print(f"  MA5: {latest.get('MA5', 0):.2f}")
        print(f"  MA10: {latest.get('MA10', 0):.2f}")
        print(f"  MA20: {latest.get('MA20', 0):.2f}")
        print(f"  RSI: {latest.get('RSI', 0):.2f}")
        print(f"  MACD: {latest.get('MACD', 0):.4f}")
        
        # 趋势分析
        current_price = latest['Close']
        ma5 = latest.get('MA5', current_price)
        ma20 = latest.get('MA20', current_price)
        
        if current_price > ma5 > ma20:
            trend = "强势上涨"
        elif current_price > ma5:
            trend = "温和上涨"
        elif current_price < ma5 < ma20:
            trend = "强势下跌"
        elif current_price < ma5:
            trend = "温和下跌"
        else:
            trend = "震荡整理"
        
        print(f"\n趋势分析: {trend}")
        
        # RSI分析
        rsi = latest.get('RSI', 50)
        if rsi > 70:
            rsi_signal = "超买"
        elif rsi < 30:
            rsi_signal = "超卖"
        else:
            rsi_signal = "正常"
        
        print(f"RSI信号: {rsi_signal} ({rsi:.1f})")
    else:
        print("未获取到股票数据")

def example_data_export():
    """数据导出示例"""
    print("\n=== 数据导出示例 ===")
    
    collector = HistoricalDataCollector()
    
    # 获取一些数据用于导出
    stock_code = "000001"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    stock_data = get_stock_historical_data(stock_code, start_date, end_date)
    
    if not stock_data.empty:
        # 导出到CSV
        export_data = {stock_code: stock_data}
        exported_files = collector.export_data_to_csv(export_data)
        
        print(f"数据已导出到以下文件:")
        for file_path in exported_files:
            print(f"  {file_path}")
    else:
        print("没有数据可导出")

def example_database_initialization():
    """数据库初始化示例"""
    print("\n=== 数据库初始化示例 ===")
    
    print("初始化历史数据库...")
    
    result = initialize_historical_database()
    
    if result['status'] == 'success':
        print(f"数据库初始化成功:")
        print(f"  股票数量: {result['stock_count']}")
        print(f"  板块数量: {result['sector_count']}")
    else:
        print("数据库初始化失败")

def example_data_summary():
    """数据摘要示例"""
    print("\n=== 数据摘要示例 ===")
    
    collector = HistoricalDataCollector()
    
    summary = collector.get_data_summary()
    
    if summary:
        print("数据库摘要信息:")
        print(f"  股票数量: {summary.get('stock_count', 0)}")
        print(f"  板块数量: {summary.get('sector_count', 0)}")
        print(f"  历史记录数: {summary.get('daily_records', 0)}")
        
        date_range = summary.get('date_range', {})
        if date_range.get('start_date'):
            print(f"  数据日期范围: {date_range['start_date']} 到 {date_range['end_date']}")
        
        print(f"  最后更新: {summary.get('last_update', 'N/A')}")
    else:
        print("获取数据摘要失败")

def main():
    """主函数"""
    print("A股历史数据获取模块使用示例")
    print("=" * 60)
    
    try:
        # 运行各种示例
        example_basic_usage()
        example_sector_analysis()
        example_batch_data_collection()
        example_technical_analysis()
        example_data_export()
        example_data_summary()
        
        # 数据库初始化示例（可选，会下载大量数据）
        # example_database_initialization()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成")
        
    except Exception as e:
        print(f"运行示例时出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
