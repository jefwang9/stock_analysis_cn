"""
股票历史数据获取模块
提供A股股票的历史数据获取、存储和管理功能
"""
import akshare as ak
import pandas as pd
import numpy as np
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import logging
from pathlib import Path
import time
import pickle
from config import settings

logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    """股票历史数据收集器"""
    
    def __init__(self):
        self.data_dir = Path(settings.data_dir)
        self.historical_dir = self.data_dir / "historical"
        self.historical_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self.db_path = settings.database.sqlite_path
        self._init_database()
        
        # 数据缓存
        self.cache = {}
        
        logger.info("历史数据收集器初始化完成")
    
    def _init_database(self):
        """初始化历史数据数据库表"""
        conn = sqlite3.connect(self.db_path)
        
        # 股票基本信息表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS stock_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT UNIQUE NOT NULL,
            stock_name TEXT NOT NULL,
            industry TEXT,
            market TEXT,
            list_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 股票历史行情表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS stock_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            trade_date DATE NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            volume INTEGER,
            amount REAL,
            amplitude REAL,
            change_pct REAL,
            change_amount REAL,
            turnover REAL,
            ma5 REAL,
            ma10 REAL,
            ma20 REAL,
            ma30 REAL,
            ma60 REAL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            macd_histogram REAL,
            kdj_k REAL,
            kdj_d REAL,
            kdj_j REAL,
            boll_upper REAL,
            boll_mid REAL,
            boll_lower REAL,
            wr REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stock_code, trade_date)
        )
        ''')
        
        # 板块信息表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sector_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_name TEXT UNIQUE NOT NULL,
            sector_code TEXT,
            description TEXT,
            stock_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 板块股票映射表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sector_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_name TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sector_name, stock_code)
        )
        ''')
        
        # 板块历史数据表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sector_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_name TEXT NOT NULL,
            trade_date DATE NOT NULL,
            avg_change_pct REAL,
            total_volume INTEGER,
            total_amount REAL,
            rising_count INTEGER,
            falling_count INTEGER,
            strong_count INTEGER,
            weak_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sector_name, trade_date)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("历史数据数据库表初始化完成")
    
    def get_stock_list(self, market: str = "A股") -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            market: 市场类型 ("A股", "港股", "美股"等)
            
        Returns:
            DataFrame: 股票基本信息
        """
        try:
            # 获取A股股票基本信息
            stock_info = ak.stock_info_a_code_name()
            
            # 添加市场信息
            stock_info['market'] = market
            stock_info['list_date'] = None  # 上市日期需要额外获取
            
            # 重命名列
            if '代码' in stock_info.columns and '名称' in stock_info.columns:
                stock_info = stock_info.rename(columns={
                    '代码': 'stock_code',
                    '名称': 'stock_name'
                })
            else:
                # 如果列名不同，尝试其他可能的列名
                column_mapping = {}
                for col in stock_info.columns:
                    if '代码' in col or 'code' in col.lower():
                        column_mapping[col] = 'stock_code'
                    elif '名称' in col or 'name' in col.lower():
                        column_mapping[col] = 'stock_name'
                
                if column_mapping:
                    stock_info = stock_info.rename(columns=column_mapping)
            
            # 保存到数据库
            self._save_stock_info(stock_info)
            
            logger.info(f"成功获取 {len(stock_info)} 只股票信息")
            return stock_info
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_sector_list(self) -> pd.DataFrame:
        """
        获取板块列表
        
        Returns:
            DataFrame: 板块信息
        """
        try:
            # 获取概念板块
            concept_sectors = ak.stock_board_concept_name_em()
            
            # 获取行业板块
            industry_sectors = ak.stock_board_industry_name_em()
            
            # 合并板块信息
            all_sectors = []
            
            # 处理概念板块
            for _, sector in concept_sectors.iterrows():
                all_sectors.append({
                    'sector_name': sector['板块名称'],
                    'sector_code': sector.get('板块代码', ''),
                    'sector_type': '概念',
                    'stock_count': sector.get('股票数量', 0),
                    'description': f"概念板块: {sector['板块名称']}"
                })
            
            # 处理行业板块
            for _, sector in industry_sectors.iterrows():
                all_sectors.append({
                    'sector_name': sector['板块名称'],
                    'sector_code': sector.get('板块代码', ''),
                    'sector_type': '行业',
                    'stock_count': sector.get('股票数量', 0),
                    'description': f"行业板块: {sector['板块名称']}"
                })
            
            sectors_df = pd.DataFrame(all_sectors)
            
            # 保存到数据库
            self._save_sector_info(sectors_df)
            
            logger.info(f"成功获取 {len(sectors_df)} 个板块信息")
            return sectors_df
            
        except Exception as e:
            logger.error(f"获取板块列表失败: {e}")
            return pd.DataFrame()
    
    def get_sector_stocks(self, sector_name: str) -> List[str]:
        """
        获取板块内的股票代码列表
        
        Args:
            sector_name: 板块名称
            
        Returns:
            List[str]: 股票代码列表
        """
        try:
            # 先从数据库查询
            cached_stocks = self._get_cached_sector_stocks(sector_name)
            if cached_stocks:
                return cached_stocks
            
            # 从API获取
            sector_stocks = ak.stock_board_concept_cons_em(symbol=sector_name)
            
            if not sector_stocks.empty:
                stock_codes = sector_stocks['代码'].tolist()
                
                # 保存到数据库
                self._save_sector_stocks(sector_name, stock_codes)
                
                logger.info(f"成功获取板块 {sector_name} 的 {len(stock_codes)} 只股票")
                return stock_codes
            
            return []
            
        except Exception as e:
            logger.error(f"获取板块 {sector_name} 股票失败: {e}")
            return []
    
    def get_stock_historical_data(self, stock_code: str, 
                                start_date: str, end_date: str,
                                adjust: str = "qfq") -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            adjust: 复权类型 ("qfq": 前复权, "hfq": 后复权, "": 不复权)
            
        Returns:
            DataFrame: 历史行情数据
        """
        try:
            # 先从数据库查询
            cached_data = self._get_cached_stock_data(stock_code, start_date, end_date)
            if not cached_data.empty:
                logger.info(f"从缓存获取 {stock_code} 历史数据")
                return cached_data
            
            # 从API获取
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df.empty:
                logger.warning(f"未获取到 {stock_code} 的历史数据")
                return pd.DataFrame()
            
            # 重命名列
            df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 
                         'Volume', 'Amount', 'Amplitude', 'Change_pct', 
                         'Change_amount', 'Turnover']
            
            # 处理日期
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # 添加技术指标
            df = self._add_technical_indicators(df)
            
            # 重置索引以便保存
            df_reset = df.reset_index()
            df_reset['stock_code'] = stock_code
            
            # 保存到数据库
            self._save_stock_data(df_reset)
            
            logger.info(f"成功获取 {stock_code} 从 {start_date} 到 {end_date} 的历史数据")
            return df
            
        except Exception as e:
            logger.error(f"获取 {stock_code} 历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_multiple_stocks_data(self, stock_codes: List[str], 
                               start_date: str, end_date: str,
                               batch_size: int = 10) -> Dict[str, pd.DataFrame]:
        """
        批量获取多只股票的历史数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            batch_size: 批处理大小
            
        Returns:
            Dict[str, DataFrame]: 股票代码到历史数据的映射
        """
        all_data = {}
        total_stocks = len(stock_codes)
        
        logger.info(f"开始批量获取 {total_stocks} 只股票的历史数据")
        
        for i in range(0, total_stocks, batch_size):
            batch_codes = stock_codes[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_stocks + batch_size - 1) // batch_size
            
            logger.info(f"处理第 {batch_num}/{total_batches} 批，包含 {len(batch_codes)} 只股票")
            
            for j, code in enumerate(batch_codes):
                try:
                    df = self.get_stock_historical_data(code, start_date, end_date)
                    if not df.empty:
                        all_data[code] = df
                    
                    # 避免请求过频
                    if j < len(batch_codes) - 1:
                        time.sleep(0.5)
                        
                except Exception as e:
                    logger.error(f"获取 {code} 数据失败: {e}")
                    continue
            
            # 批次间休息
            if i + batch_size < total_stocks:
                time.sleep(2)
        
        logger.info(f"批量获取完成，成功获取 {len(all_data)} 只股票的数据")
        return all_data
    
    def get_sector_historical_data(self, sector_name: str, 
                                 start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        获取板块内所有股票的历史数据
        
        Args:
            sector_name: 板块名称
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict[str, DataFrame]: 股票历史数据
        """
        # 获取板块内股票
        stock_codes = self.get_sector_stocks(sector_name)
        
        if not stock_codes:
            logger.warning(f"板块 {sector_name} 没有股票数据")
            return {}
        
        logger.info(f"开始获取板块 {sector_name} 的 {len(stock_codes)} 只股票历史数据")
        
        # 批量获取股票数据
        return self.get_multiple_stocks_data(stock_codes, start_date, end_date)
    
    def get_all_sectors_data(self, start_date: str, end_date: str,
                           sectors: List[str] = None) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        获取所有板块的历史数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            sectors: 板块列表，None表示获取所有板块
            
        Returns:
            Dict: 板块历史数据
        """
        if sectors is None:
            sectors = settings.trading.sectors
        
        all_sectors_data = {}
        
        logger.info(f"开始获取 {len(sectors)} 个板块的历史数据")
        
        for i, sector in enumerate(sectors):
            logger.info(f"正在获取板块 {sector} ({i+1}/{len(sectors)})")
            
            try:
                sector_data = self.get_sector_historical_data(sector, start_date, end_date)
                if sector_data:
                    all_sectors_data[sector] = sector_data
                
                # 避免请求过频
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"获取板块 {sector} 数据失败: {e}")
                continue
        
        logger.info(f"板块数据获取完成，成功获取 {len(all_sectors_data)} 个板块的数据")
        return all_sectors_data
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加技术指标"""
        try:
            # 移动平均线
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA10'] = df['Close'].rolling(window=10).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA30'] = df['Close'].rolling(window=30).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            
            # RSI
            df['RSI'] = self._calculate_rsi(df['Close'], 14)
            
            # MACD
            exp1 = df['Close'].ewm(span=12).mean()
            exp2 = df['Close'].ewm(span=26).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
            
            # KDJ
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
                      d_period: int = 3) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算KDJ指标"""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        
        rsv = 100 * (df['Close'] - low_min) / (high_max - low_min)
        rsv = rsv.fillna(method='bfill')
        
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
    
    def _save_stock_info(self, stock_info: pd.DataFrame):
        """保存股票基本信息到数据库"""
        conn = sqlite3.connect(self.db_path)
        
        for _, row in stock_info.iterrows():
            conn.execute('''
            INSERT OR REPLACE INTO stock_info 
            (stock_code, stock_name, market, list_date, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (row['stock_code'], row['stock_name'], row['market'], 
                  row['list_date'], datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _save_sector_info(self, sector_info: pd.DataFrame):
        """保存板块信息到数据库"""
        conn = sqlite3.connect(self.db_path)
        
        for _, row in sector_info.iterrows():
            conn.execute('''
            INSERT OR REPLACE INTO sector_info 
            (sector_name, sector_code, description, stock_count, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (row['sector_name'], row['sector_code'], row['description'],
                  row['stock_count'], datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _save_sector_stocks(self, sector_name: str, stock_codes: List[str]):
        """保存板块股票映射到数据库"""
        conn = sqlite3.connect(self.db_path)
        
        for stock_code in stock_codes:
            conn.execute('''
            INSERT OR REPLACE INTO sector_stocks (sector_name, stock_code)
            VALUES (?, ?)
            ''', (sector_name, stock_code))
        
        conn.commit()
        conn.close()
    
    def _save_stock_data(self, stock_data: pd.DataFrame):
        """保存股票历史数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        
        for _, row in stock_data.iterrows():
            conn.execute('''
            INSERT OR REPLACE INTO stock_daily 
            (stock_code, trade_date, open_price, high_price, low_price, close_price,
             volume, amount, amplitude, change_pct, change_amount, turnover,
             ma5, ma10, ma20, ma30, ma60, rsi, macd, macd_signal, macd_histogram,
             kdj_k, kdj_d, kdj_j, boll_upper, boll_mid, boll_lower, wr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['stock_code'], row['Date'], row['Open'], row['High'], row['Low'], row['Close'],
                row['Volume'], row['Amount'], row['Amplitude'], row['Change_pct'], 
                row['Change_amount'], row['Turnover'],
                row.get('MA5'), row.get('MA10'), row.get('MA20'), row.get('MA30'), row.get('MA60'),
                row.get('RSI'), row.get('MACD'), row.get('MACD_signal'), row.get('MACD_histogram'),
                row.get('KDJ_K'), row.get('KDJ_D'), row.get('KDJ_J'),
                row.get('BOLL_upper'), row.get('BOLL_mid'), row.get('BOLL_lower'), row.get('WR')
            ))
        
        conn.commit()
        conn.close()
    
    def _get_cached_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从数据库获取缓存的股票数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
            SELECT trade_date, open_price, high_price, low_price, close_price,
                   volume, amount, amplitude, change_pct, change_amount, turnover,
                   ma5, ma10, ma20, ma30, ma60, rsi, macd, macd_signal, macd_histogram,
                   kdj_k, kdj_d, kdj_j, boll_upper, boll_mid, boll_lower, wr
            FROM stock_daily 
            WHERE stock_code = ? AND trade_date BETWEEN ? AND ?
            ORDER BY trade_date
            '''
            
            df = pd.read_sql_query(query, conn, params=(stock_code, start_date, end_date))
            conn.close()
            
            if not df.empty:
                df['Date'] = pd.to_datetime(df['trade_date'])
                df.set_index('Date', inplace=True)
                
                # 重命名列
                column_mapping = {
                    'open_price': 'Open', 'high_price': 'High', 'low_price': 'Low', 'close_price': 'Close',
                    'volume': 'Volume', 'amount': 'Amount', 'amplitude': 'Amplitude',
                    'change_pct': 'Change_pct', 'change_amount': 'Change_amount', 'turnover': 'Turnover'
                }
                df = df.rename(columns=column_mapping)
            
            return df
            
        except Exception as e:
            logger.error(f"获取缓存数据失败: {e}")
            return pd.DataFrame()
    
    def _get_cached_sector_stocks(self, sector_name: str) -> List[str]:
        """从数据库获取缓存的板块股票"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = 'SELECT stock_code FROM sector_stocks WHERE sector_name = ?'
            result = conn.execute(query, (sector_name,)).fetchall()
            conn.close()
            
            return [row[0] for row in result]
            
        except Exception as e:
            logger.error(f"获取缓存板块股票失败: {e}")
            return []
    
    def export_data_to_csv(self, data: Dict[str, pd.DataFrame], 
                          output_dir: str = None) -> List[str]:
        """
        导出数据到CSV文件
        
        Args:
            data: 要导出的数据
            output_dir: 输出目录
            
        Returns:
            List[str]: 导出的文件路径列表
        """
        if output_dir is None:
            output_dir = self.historical_dir
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        for key, df in data.items():
            if isinstance(df, dict):
                # 处理嵌套字典（如板块数据）
                for sub_key, sub_df in df.items():
                    filename = f"{key}_{sub_key}_{datetime.now().strftime('%Y%m%d')}.csv"
                    filepath = output_path / filename
                    sub_df.to_csv(filepath)
                    exported_files.append(str(filepath))
            else:
                # 处理单个DataFrame
                filename = f"{key}_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = output_path / filename
                df.to_csv(filepath)
                exported_files.append(str(filepath))
        
        logger.info(f"数据已导出到 {len(exported_files)} 个CSV文件")
        return exported_files
    
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 股票数量
            stock_count = conn.execute('SELECT COUNT(*) FROM stock_info').fetchone()[0]
            
            # 板块数量
            sector_count = conn.execute('SELECT COUNT(*) FROM sector_info').fetchone()[0]
            
            # 历史数据记录数
            daily_count = conn.execute('SELECT COUNT(*) FROM stock_daily').fetchone()[0]
            
            # 数据日期范围
            date_range = conn.execute('''
                SELECT MIN(trade_date), MAX(trade_date) FROM stock_daily
            ''').fetchone()
            
            conn.close()
            
            return {
                'stock_count': stock_count,
                'sector_count': sector_count,
                'daily_records': daily_count,
                'date_range': {
                    'start_date': date_range[0],
                    'end_date': date_range[1]
                },
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"获取数据摘要失败: {e}")
            return {}

# 便捷函数
def get_stock_historical_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取单只股票历史数据"""
    collector = HistoricalDataCollector()
    return collector.get_stock_historical_data(stock_code, start_date, end_date)

def get_sector_historical_data(sector_name: str, start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """获取板块历史数据"""
    collector = HistoricalDataCollector()
    return collector.get_sector_historical_data(sector_name, start_date, end_date)

def get_all_sectors_historical_data(start_date: str, end_date: str, 
                                  sectors: List[str] = None) -> Dict[str, Dict[str, pd.DataFrame]]:
    """获取所有板块历史数据"""
    collector = HistoricalDataCollector()
    return collector.get_all_sectors_data(start_date, end_date, sectors)

def initialize_historical_database():
    """初始化历史数据库"""
    collector = HistoricalDataCollector()
    
    # 获取股票列表
    stock_list = collector.get_stock_list()
    
    # 获取板块列表
    sector_list = collector.get_sector_list()
    
    return {
        'stock_count': len(stock_list),
        'sector_count': len(sector_list),
        'status': 'success'
    }
