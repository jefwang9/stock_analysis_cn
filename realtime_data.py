"""
股票实时数据获取模块
提供A股股票的实时行情数据获取功能
"""
import akshare as ak
import pandas as pd
import numpy as np
import requests
import json
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import logging
from config import settings
import threading
from queue import Queue
import redis
import sqlite3

logger = logging.getLogger(__name__)

class RealtimeDataCollector:
    """股票实时数据收集器"""
    
    def __init__(self):
        self.redis_client = None
        self.data_queue = Queue()
        self.is_running = False
        self.update_interval = 5  # 更新间隔（秒）
        
        # 初始化Redis连接（用于缓存实时数据）
        try:
            self.redis_client = redis.from_url(settings.database.redis_url)
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，将使用内存缓存")
            self.redis_client = None
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化实时数据数据库表"""
        conn = sqlite3.connect(settings.database.sqlite_path)
        
        # 实时行情表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS realtime_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            current_price REAL,
            change_amount REAL,
            change_pct REAL,
            volume INTEGER,
            amount REAL,
            high REAL,
            low REAL,
            open REAL,
            pre_close REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stock_code, timestamp)
        )
        ''')
        
        # 板块实时数据表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sector_realtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector TEXT NOT NULL,
            avg_change_pct REAL,
            total_volume INTEGER,
            total_amount REAL,
            rising_count INTEGER,
            falling_count INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sector, timestamp)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_realtime_quotes(self, stock_codes: List[str] = None) -> pd.DataFrame:
        """
        获取实时股票行情
        
        Args:
            stock_codes: 股票代码列表，None表示获取全部A股
            
        Returns:
            DataFrame: 实时行情数据
        """
        try:
            # 使用AKShare获取实时行情
            realtime_data = ak.stock_zh_a_spot_em()
            
            if stock_codes:
                # 筛选指定股票
                realtime_data = realtime_data[realtime_data['代码'].isin(stock_codes)]
            
            # 重命名列名
            column_mapping = {
                '代码': 'stock_code',
                '名称': 'stock_name',
                '最新价': 'current_price',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'amount',
                '最高': 'high',
                '最低': 'low',
                '今开': 'open',
                '昨收': 'pre_close'
            }
            
            realtime_data = realtime_data.rename(columns=column_mapping)
            
            # 添加时间戳
            realtime_data['timestamp'] = datetime.now()
            
            # 数据清洗
            realtime_data = self._clean_realtime_data(realtime_data)
            
            logger.info(f"成功获取 {len(realtime_data)} 只股票的实时行情")
            
            return realtime_data
            
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_sector_realtime_data(self, sectors: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        获取板块实时数据
        
        Args:
            sectors: 板块列表，None表示获取所有板块
            
        Returns:
            Dict: 板块实时数据
        """
        if sectors is None:
            sectors = settings.trading.sectors
        
        sector_data = {}
        
        try:
            # 获取所有股票实时数据
            all_stocks = self.get_realtime_quotes()
            
            if all_stocks.empty:
                return sector_data
            
            # 为每个板块计算实时指标
            for sector in sectors:
                # 获取板块内股票（简化处理，实际应该从板块股票映射获取）
                sector_stocks = self._get_sector_stocks(sector)
                
                if not sector_stocks:
                    continue
                
                # 筛选板块内股票数据
                sector_stock_data = all_stocks[all_stocks['stock_code'].isin(sector_stocks)]
                
                if sector_stock_data.empty:
                    continue
                
                # 计算板块指标
                sector_metrics = self._calculate_sector_metrics(sector_stock_data)
                sector_data[sector] = sector_metrics
                
                # 缓存到Redis
                if self.redis_client:
                    cache_key = f"sector_realtime:{sector}"
                    self.redis_client.setex(
                        cache_key, 
                        60,  # 1分钟过期
                        json.dumps(sector_metrics, default=str)
                    )
            
            logger.info(f"成功获取 {len(sector_data)} 个板块的实时数据")
            
        except Exception as e:
            logger.error(f"获取板块实时数据失败: {e}")
        
        return sector_data
    
    def _get_sector_stocks(self, sector: str) -> List[str]:
        """获取板块内的股票代码列表"""
        try:
            # 使用AKShare获取板块股票
            sector_stocks = ak.stock_board_concept_cons_em(symbol=sector)
            if not sector_stocks.empty:
                return sector_stocks['代码'].tolist()
            return []
        except Exception as e:
            logger.error(f"获取板块 {sector} 股票失败: {e}")
            return []
    
    def _calculate_sector_metrics(self, sector_stocks: pd.DataFrame) -> Dict[str, Any]:
        """计算板块实时指标"""
        try:
            # 基础统计
            total_stocks = len(sector_stocks)
            avg_change_pct = sector_stocks['change_pct'].mean()
            total_volume = sector_stocks['volume'].sum()
            total_amount = sector_stocks['amount'].sum()
            
            # 涨跌统计
            rising_stocks = len(sector_stocks[sector_stocks['change_pct'] > 0])
            falling_stocks = len(sector_stocks[sector_stocks['change_pct'] < 0])
            flat_stocks = total_stocks - rising_stocks - falling_stocks
            
            # 强势股票（涨幅>5%）
            strong_stocks = len(sector_stocks[sector_stocks['change_pct'] > 5])
            
            # 弱势股票（跌幅>5%）
            weak_stocks = len(sector_stocks[sector_stocks['change_pct'] < -5])
            
            # 成交量活跃度
            volume_avg = sector_stocks['volume'].mean()
            volume_std = sector_stocks['volume'].std()
            volume_ratio = volume_std / volume_avg if volume_avg > 0 else 0
            
            # 价格分布
            price_stats = {
                'avg_price': sector_stocks['current_price'].mean(),
                'max_price': sector_stocks['current_price'].max(),
                'min_price': sector_stocks['current_price'].min(),
                'price_std': sector_stocks['current_price'].std()
            }
            
            return {
                'sector': sector,
                'total_stocks': total_stocks,
                'avg_change_pct': round(avg_change_pct, 4),
                'total_volume': int(total_volume),
                'total_amount': round(total_amount, 2),
                'rising_count': rising_stocks,
                'falling_count': falling_stocks,
                'flat_count': flat_stocks,
                'strong_stocks': strong_stocks,
                'weak_stocks': weak_stocks,
                'volume_ratio': round(volume_ratio, 4),
                'price_stats': price_stats,
                'timestamp': datetime.now(),
                'market_sentiment': self._calculate_market_sentiment(avg_change_pct, rising_stocks, total_stocks)
            }
            
        except Exception as e:
            logger.error(f"计算板块指标失败: {e}")
            return {}
    
    def _calculate_market_sentiment(self, avg_change_pct: float, rising_count: int, total_count: int) -> str:
        """计算市场情绪"""
        rising_ratio = rising_count / total_count if total_count > 0 else 0
        
        if avg_change_pct > 2 and rising_ratio > 0.7:
            return "强势上涨"
        elif avg_change_pct > 1 and rising_ratio > 0.6:
            return "温和上涨"
        elif avg_change_pct > 0 and rising_ratio > 0.5:
            return "小幅上涨"
        elif avg_change_pct < -2 and rising_ratio < 0.3:
            return "强势下跌"
        elif avg_change_pct < -1 and rising_ratio < 0.4:
            return "温和下跌"
        elif avg_change_pct < 0 and rising_ratio < 0.5:
            return "小幅下跌"
        else:
            return "震荡整理"
    
    def _clean_realtime_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """清洗实时数据"""
        try:
            # 移除无效数据
            data = data.dropna(subset=['current_price'])
            
            # 转换数据类型
            numeric_columns = ['current_price', 'change_pct', 'change_amount', 
                              'volume', 'amount', 'high', 'low', 'open', 'pre_close']
            
            for col in numeric_columns:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # 移除异常值
            data = data[data['current_price'] > 0]
            data = data[data['volume'] >= 0]
            
            return data
            
        except Exception as e:
            logger.error(f"清洗实时数据失败: {e}")
            return data
    
    def save_realtime_data(self, data: pd.DataFrame, table_name: str = 'realtime_quotes'):
        """保存实时数据到数据库"""
        try:
            conn = sqlite3.connect(settings.database.sqlite_path)
            
            # 保存到数据库
            data.to_sql(table_name, conn, if_exists='append', index=False)
            
            conn.close()
            
            logger.info(f"实时数据已保存到 {table_name} 表")
            
        except Exception as e:
            logger.error(f"保存实时数据失败: {e}")
    
    def get_cached_sector_data(self, sector: str) -> Optional[Dict[str, Any]]:
        """从缓存获取板块数据"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"sector_realtime:{sector}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
        except Exception as e:
            logger.error(f"获取缓存数据失败: {e}")
        
        return None
    
    def start_realtime_monitoring(self, stock_codes: List[str] = None, 
                                sectors: List[str] = None, 
                                interval: int = 5):
        """
        启动实时监控
        
        Args:
            stock_codes: 监控的股票代码
            sectors: 监控的板块
            interval: 更新间隔（秒）
        """
        self.is_running = True
        self.update_interval = interval
        
        def monitoring_loop():
            while self.is_running:
                try:
                    # 获取实时数据
                    if stock_codes:
                        realtime_data = self.get_realtime_quotes(stock_codes)
                        if not realtime_data.empty:
                            self.save_realtime_data(realtime_data)
                    
                    if sectors:
                        sector_data = self.get_sector_realtime_data(sectors)
                        # 保存板块数据
                        for sector, metrics in sector_data.items():
                            self._save_sector_data(sector, metrics)
                    
                    # 等待下次更新
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"实时监控出错: {e}")
                    time.sleep(self.update_interval)
        
        # 在后台线程中运行监控
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        logger.info(f"实时监控已启动，更新间隔: {interval}秒")
    
    def _save_sector_data(self, sector: str, metrics: Dict[str, Any]):
        """保存板块数据到数据库"""
        try:
            conn = sqlite3.connect(settings.database.sqlite_path)
            
            conn.execute('''
            INSERT OR REPLACE INTO sector_realtime 
            (sector, avg_change_pct, total_volume, total_amount, 
             rising_count, falling_count, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sector, metrics['avg_change_pct'], metrics['total_volume'],
                  metrics['total_amount'], metrics['rising_count'], 
                  metrics['falling_count'], datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"保存板块数据失败: {e}")
    
    def stop_realtime_monitoring(self):
        """停止实时监控"""
        self.is_running = False
        logger.info("实时监控已停止")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览"""
        try:
            # 获取大盘指数
            index_data = ak.stock_zh_index_spot_em()
            
            # 获取主要指数
            main_indices = ['上证指数', '深证成指', '创业板指', '科创50']
            market_overview = {}
            
            for index_name in main_indices:
                index_info = index_data[index_data['名称'] == index_name]
                if not index_info.empty:
                    market_overview[index_name] = {
                        'current_price': index_info['最新价'].iloc[0],
                        'change_pct': index_info['涨跌幅'].iloc[0],
                        'change_amount': index_info['涨跌额'].iloc[0],
                        'volume': index_info['成交量'].iloc[0],
                        'amount': index_info['成交额'].iloc[0]
                    }
            
            # 获取市场统计 - 使用指数数据估算，避免获取所有股票
            try:
                # 从指数数据中获取市场概览信息
                market_stats = {
                    'total_stocks': 5000,  # 估算A股总数
                    'rising_stocks': 0,    # 这些需要实时数据，暂时设为0
                    'falling_stocks': 0,
                    'limit_up': 0,
                    'limit_down': 0,
                    'avg_change_pct': 0,
                    'total_volume': 0,
                    'total_amount': 0
                }
                
                # 如果有指数数据，使用指数涨跌幅作为市场整体表现
                if market_overview:
                    avg_index_change = sum([idx['change_pct'] for idx in market_overview.values()]) / len(market_overview)
                    market_stats['avg_change_pct'] = avg_index_change
                    
            except Exception as e:
                logger.warning(f"获取市场统计失败: {e}")
                # 如果获取详细统计失败，返回基本统计
                market_stats = {
                    'total_stocks': 0,
                    'rising_stocks': 0,
                    'falling_stocks': 0,
                    'limit_up': 0,
                    'limit_down': 0,
                    'avg_change_pct': 0,
                    'total_volume': 0,
                    'total_amount': 0
                }
            
            return {
                'indices': market_overview,
                'market_stats': market_stats,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            return {}
    
    def get_hot_stocks(self, limit: int = 20) -> pd.DataFrame:
        """获取热门股票（按成交额排序）"""
        try:
            all_stocks = self.get_realtime_quotes()
            
            if all_stocks.empty:
                return pd.DataFrame()
            
            # 按成交额排序
            hot_stocks = all_stocks.nlargest(limit, 'amount')
            
            # 添加排名
            hot_stocks['rank'] = range(1, len(hot_stocks) + 1)
            
            return hot_stocks[['rank', 'stock_code', 'stock_name', 'current_price', 
                             'change_pct', 'volume', 'amount']]
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return pd.DataFrame()
    
    def get_sector_ranking(self) -> pd.DataFrame:
        """获取板块涨跌幅排名"""
        try:
            sector_data = self.get_sector_realtime_data()
            
            if not sector_data:
                return pd.DataFrame()
            
            # 转换为DataFrame
            ranking_data = []
            for sector, metrics in sector_data.items():
                ranking_data.append({
                    'sector': sector,
                    'avg_change_pct': metrics['avg_change_pct'],
                    'rising_count': metrics['rising_count'],
                    'falling_count': metrics['falling_count'],
                    'total_stocks': metrics['total_stocks'],
                    'market_sentiment': metrics['market_sentiment']
                })
            
            ranking_df = pd.DataFrame(ranking_data)
            ranking_df = ranking_df.sort_values('avg_change_pct', ascending=False)
            ranking_df['rank'] = range(1, len(ranking_df) + 1)
            
            return ranking_df
            
        except Exception as e:
            logger.error(f"获取板块排名失败: {e}")
            return pd.DataFrame()

# 便捷函数
def get_realtime_quotes(stock_codes: List[str] = None) -> pd.DataFrame:
    """获取实时股票行情"""
    collector = RealtimeDataCollector()
    return collector.get_realtime_quotes(stock_codes)

def get_sector_realtime_data(sectors: List[str] = None) -> Dict[str, Dict[str, Any]]:
    """获取板块实时数据"""
    collector = RealtimeDataCollector()
    return collector.get_sector_realtime_data(sectors)

def get_market_overview() -> Dict[str, Any]:
    """获取市场概览"""
    collector = RealtimeDataCollector()
    return collector.get_market_overview()

def start_realtime_monitoring(stock_codes: List[str] = None, 
                            sectors: List[str] = None, 
                            interval: int = 5):
    """启动实时监控"""
    collector = RealtimeDataCollector()
    collector.start_realtime_monitoring(stock_codes, sectors, interval)
    return collector
