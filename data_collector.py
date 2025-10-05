"""
股票数据收集模块
包含历史数据和实时数据获取功能
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import time
import logging
from config import settings

logger = logging.getLogger(__name__)

class StockDataCollector:
    """股票数据收集器"""
    
    def __init__(self):
        self.data_path = f"{settings.data_dir}/historical"
        
    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        try:
            # 获取A股股票基本信息
            stock_info = ak.stock_info_a_code_name()
            logger.info(f"成功获取 {len(stock_info)} 只股票信息")
            return stock_info
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_sector_stocks(self, sector_name: str) -> List[str]:
        """获取指定板块的股票代码列表"""
        try:
            # 获取板块股票（这里简化处理，实际可以根据具体需求调整）
            sector_stocks = ak.stock_board_concept_cons_em(symbol=sector_name)
            if not sector_stocks.empty:
                return sector_stocks['代码'].tolist()
            return []
        except Exception as e:
            logger.error(f"获取板块 {sector_name} 股票失败: {e}")
            return []
    
    def get_historical_data(self, stock_codes: List[str], 
                          start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        获取历史股票数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            
        Returns:
            Dict[股票代码, DataFrame]: 包含OHLCV数据的字典
        """
        historical_data = {}
        
        for i, code in enumerate(stock_codes):
            try:
                if i > 0 and i % 10 == 0:  # 每10只股票休息一下
                    time.sleep(1)
                
                # 获取股票历史数据
                df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                      start_date=start_date, end_date=end_date, adjust="qfq")
                
                if not df.empty:
                    # 重命名列名为英文，便于处理
                    df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 
                                'Volume', 'Amount', 'Amplitude', 'Change_pct', 
                                'Change_amount', 'Turnover']
                    
                    # 确保日期格式
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.set_index('Date', inplace=True)
                    
                    # 计算技术指标
                    df = self._add_technical_indicators(df)
                    
                    historical_data[code] = df
                    
            except Exception as e:
                logger.error(f"获取股票 {code} 历史数据失败: {e}")
                continue
        
        logger.info(f"成功获取 {len(historical_data)} 只股票的历史数据")


    def get_realtime_data(self, stock_codes: List[str]) -> pd.DataFrame:
        """获取实时股票数据"""
        try:
            # 获取实时行情
            realtime_data = ak.stock_zh_a_spot_em()
            
            # 筛选指定的股票代码
            if stock_codes:
                realtime_data = realtime_data[realtime_data['代码'].isin(stock_codes)]
            
            return realtime_data
            
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return pd.DataFrame()
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加技术指标"""
        try:
            # 移动平均线
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA10'] = df['Close'].rolling(window=10).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA30'] = df['Close'].rolling(window=30).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # RSI相对强弱指标
            df['RSI'] = self._calculate_rsi(df['Close'], 14)
            
            # MACD指标
            exp1 = df['Close'].ewm(span=12).mean()
            exp2 = df['Close'].ewm(span=26).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
            
            # KDJ指标
            df['KDJ_K'], df['KDJ_D'], df['KDJ_J'] = self._calculate_kdj(df)
            
            # 布林带
            df['BOLL_mid'] = df['Close'].rolling(window=20).mean()
            std = df['Close'].rolling(window=20).std()
            df['BOLL_upper'] = df['BOLL_mid'] + (std * 2)
            df['BOLL_lower'] = df['BOLL_mid'] - (std * 2)
            
            # WR威廉指标
            df['WR'] = self._calculate_wr(df)
            
            return df
            
        except Exception as e:
            logger.error(f"添加技术指标失败: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_kdj(self, df: pd.DataFrame, k_period: int = 9, 
                      d_period: int = 3) -> tuple:
        """计算KDJ指标"""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        
        rsv = 100 * (df['Close'] - low_min) / (high_max - low_min)
        rsv = rsv.fillna(method='bfill')  # 填充NaN值
        
        K = rsv.ewm(alpha=1/d_period).mean()
        D = K.ewm(alpha=1/d_period).mean()
        J = 3 * K - 2 * D
        
        return K, D, J
    
    def _calculate_wr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算威廉指标WR"""
        high_max = df['High'].rolling(window=period).max()
        low_min = df['Low'].rolling(window=period).min()
        
        wr = -100 * (high_max - df['Close']) / (high_max - low_min)
        return wr.fillna(method='bfill')
    
    def save_historical_data(self, data: Dict[str, pd.DataFrame], 
                           filename: str = None):
        """保存历史数据到文件"""
        if filename is None:
            filename = f"historical_data_{datetime.now().strftime('%Y%m%d')}.pkl"
        
        filepath = f"{self.data_path}/{filename}"
        pd.to_pickle(data, filepath)
        logger.info(f"历史数据已保存到 {filepath}")
    
    def load_historical_data(self, filename: str) -> Dict[str, pd.DataFrame]:
        """从文件加载历史数据"""
        try:
            filepath = f"{self.data_path}/{filename}"
            data = pd.read_pickle(filepath)
            logger.info(f"已加载历史数据文件 {filename}")
            return data
        except Exception as e:
            logger.error(f"加载历史数据失败: {e}")
            return {}

# 便捷函数
def get_sector_data(sector_name: str, days: int = 30) -> Dict[str, pd.DataFrame]:
    """获取指定板块的历史数据"""
    collector = StockDataCollector()
    
    # 获取板块股票列表
    stock_codes = collector.get_sector_stocks(sector_name)
    if not stock_codes:
        return {}
    
    # 计算日期范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 获取历史数据
    return collector.get_historical_data(stock_codes, start_date, end_date)

def get_main_sectors_data(days: int = 30) -> Dict[str, Dict[str, pd.DataFrame]]:
    """获取主要板块的历史数据"""
    sectors_data = {}
    collector = StockDataCollector()
    
    for sector in settings.trading.sectors:
        logger.info(f"正在获取 {sector} 板块数据...")
        sector_data = get_sector_data(sector, days)
        if sector_data:
            sectors_data[sector] = sector_data
        
        time.sleep(1)  # 避免请求过频
    
    return sectors_data
