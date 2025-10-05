"""
股票舆情分析模块
收集和分析雪球、同花顺、东方财富、小红书、微博上的股票舆情信息
"""
import requests
import json
import pandas as pd
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import jieba
from snownlp import SnowNLP
import logging
from config import settings
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """股票舆情分析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 情感分析配置
        self.positive_words = set(['上涨', '看涨', '突破', '买入', '推荐', '利好', '强劲', '爆发', '牛', '机会'])
        self.negative_words = set(['下跌', '看跌', '卖出', '利空', '风险', '预警', '熊', '崩盘', '跌停', '破位'])
    
    def collect_xueqiu_data(self, stock_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        收集雪球相关数据
        
        Args:
            stock_name: 股票名称
            days: 采集天数
            
        Returns:
            List[Dict]: 舆情数据列表
        """
        sentiment_data = []
        
        try:
            # 雪球搜索API (模拟)
            search_url = f"{settings.sentiment_source.xueqiu_api_url}symbol/search.json"
            params = {
                'q': stock_name,
                'count': 20,
                'comment': 1,
                'symbol': 1,
                'type': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=settings.data_source.request_timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('list', []):
                    sentiment_item = {
                        'platform': '雪球',
                        'stock_name': stock_name,
                        'title': item.get('title', ''),
                        'content': item.get('description', ''),
                        'author': item.get('user', {}).get('screen_name', ''),
                        'publish_time': item.get('created_at', ''),
                        'likes': item.get('view_count', 0),
                        'comments': item.get('reply_count', 0),
                        'sentiment_score': self._calculate_sentiment_score(
                            f"{item.get('title', '')} {item.get('description', '')}"
                        )
                    }
                    sentiment_data.append(sentiment_item)
            
            time.sleep(settings.data_source.request_delay)
            
        except Exception as e:
            logger.error(f"收集雪球数据失败: {e}")
        
        logger.info(f"从雪球收集到 {len(sentiment_data)} 条 {stock_name} 相关数据")
        return sentiment_data
    
    def collect_eastmoney_data(self, stock_code: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        收集东方财富相关数据
        
        Args:
            stock_code: 股票代码
            days: 采集天数
            
        Returns:
            List[Dict]: 舆情数据列表
        """
        sentiment_data = []
        
        try:
            # 东方财富资讯API
            news_url = f"{settings.sentiment_source.eastmoney_url}center/api/list"
            params = {
                'cb': 'jQuery',
                'category': 'xwzx',
                'market': 'chn',
                'stock_code': stock_code,
                'page': 1,
                'pageSize': 20
            }
            
            response = self.session.get(news_url, params=params, timeout=settings.data_source.request_timeout)
            
            if response.status_code == 200:
                # 解析JSONP响应
                content = response.text
                if content.startswith('jQuery'):
                    json_start = content.find('(') + 1
                    json_end = content.rfind(')')
                    json_content = content[json_start:json_end]
                    data = json.loads(json_content)
                    
                    for item in data.get('data', {}).get('list', []):
                        sentiment_item = {
                            'platform': '东方财富',
                            'stock_code': stock_code,
                            'title': item.get('title', ''),
                            'content': item.get('digest', ''),
                            'author': item.get('srcfrom', ''),
                            'publish_time': item.get('showtime', ''),
                            'likes': 0,
                            'comments': 0,
                            'sentiment_score': self._calculate_sentiment_score(
                                f"{item.get('title', '')} {item.get('digest', '')}"
                            )
                        }
                        sentiment_data.append(sentiment_item)
            
            time.sleep(settings.data_source.request_delay)
            
        except Exception as e:
            logger.error(f"收集东方财富数据失败: {e}")
        
        logger.info(f"从东方财富收集到 {len(sentiment_data)} 条 {stock_code} 相关数据")
        return sentiment_data
    
    def collect_tonghuashun_data(self, stock_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        收集同花顺相关数据
        
        Args:
            stock_name: 股票名称
            days: 采集天数
            
        Returns:
            List[Dict]: 舆情数据列表
        """
        sentiment_data = []
        
        try:
            # 同花顺资讯搜索
            search_url = f"{settings.sentiment_source.tonghuashun_url}hs/news/search"
            params = {
                'keyword': stock_name,
                'type': 'news',
                'time': days,
                'pageSize': 20
            }
            
            response = self.session.get(search_url, params=params, timeout=settings.data_source.request_timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 解析新闻列表（具体选择器需要根据实际页面调整）
                news_items = soup.find_all('div', class_='news-item')
                
                for item in news_items[:20]:  # 限制数量
                    try:
                        title_elem = item.find('a', class_='title')
                        content_elem = item.find('div', class_='content')
                        time_elem = item.find('span', class_='time')
                        
                        sentiment_item = {
                            'platform': '同花顺',
                            'stock_name': stock_name,
                            'title': title_elem.text.strip() if title_elem else '',
                            'content': content_elem.text.strip() if content_elem else '',
                            'author': '',
                            'publish_time': time_elem.text.strip() if time_elem else '',
                            'likes': 0,
                            'comments': 0,
                            'sentiment_score': self._calculate_sentiment_score(
                                f"{title_elem.text.strip() if title_elem else ''} {content_elem.text.strip() if content_elem else ''}"
                            )
                        }
                        sentiment_data.append(sentiment_item)
                    except Exception as e:
                        continue
            
            time.sleep(settings.data_source.request_delay)
            
        except Exception as e:
            logger.error(f"收集同花顺数据失败: {e}")
        
        logger.info(f"从同花顺收集到 {len(sentiment_data)} 条 {stock_name} 相关数据")
        return sentiment_data
    
    def collect_weibo_data(self, stock_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        收集微博相关数据
        
        Args:
            stock_name: 股票名称
            days: 采集天数
            
        Returns:
            List[Dict]: 舆情数据列表
        """
        sentiment_data = []
        
        try:
            # 微博实时搜索
            search_url = f"{settings.sentiment_source.weibo_url}weibo"
            params = {
                'q': stock_name,
                'typeall': 1,
                'suball': 1,
                'timescope': f'custom:{datetime.now() - timedelta(days=days)}:{datetime.now()}',
                'Refer': 's_weibo'
            }
            
            response = self.session.get(search_url, params=params, timeout=settings.data_source.request_timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 解析微博内容（具体选择器需要根据实际页面调整）
                weibo_items = soup.find_all('div', class_='card-content')
                
                for item in weibo_items[:15]:  # 限制数量
                    try:
                        text_elem = item.find('p', class_='txt')
                        author_elem = item.find('div', class_='info')
                        time_elem = item.find('div', class_='from')
                        
                        sentiment_item = {
                            'platform': '微博',
                            'stock_name': stock_name,
                            'title': '',
                            'content': text_elem.text.strip() if text_elem else '',
                            'author': author_elem.text.strip() if author_elem else '',
                            'publish_time': time_elem.text.strip() if time_elem else '',
                            'likes': 0,
                            'comments': 0,
                            'sentiment_score': self._calculate_sentiment_score(
                                text_elem.text.strip() if text_elem else ''
                            )
                        }
                        sentiment_data.append(sentiment_item)
                    except Exception as e:
                        continue
            
            time.sleep(settings.data_source.request_delay)
            
        except Exception as e:
            logger.error(f"收集微博数据失败: {e}")
        
        logger.info(f"从微博收集到 {len(sentiment_data)} 条 {stock_name} 相关数据")
        return sentiment_data
    
    def collect_all_sentiment_data(self, stock_codes: List[str], 
                                 stock_names: List[str], days: int = 7) -> pd.DataFrame:
        """
        收集所有平台的舆情数据
        
        Args:
            stock_codes: 股票代码列表
            stock_names: 股票名称列表
            days: 采集天数
            
        Returns:
            DataFrame: 统一的舆情数据
        """
        all_data = []
        
        for code, name in zip(stock_codes, stock_names):
            logger.info(f"正在收集 {name}({code}) 的舆情数据...")
            
            # 收集各平台数据
            data_sources = [
                ('雪球', lambda: self.collect_xueqiu_data(name, days)),
                ('东方财富', lambda: self.collect_eastmoney_data(code, days)),
                ('同花顺', lambda: self.collect_tonghuashun_data(name, days)),
                ('微博', lambda: self.collect_weibo_data(name, days))
            ]
            
            for platform_name, collect_func in data_sources:
                try:
                    platform_data = collect_func()
                    all_data.extend(platform_data)
                except Exception as e:
                    logger.error(f"收集 {platform_name} 数据失败: {e}")
            
            # 避免请求过频
            time.sleep(2)
        
        # 转换为DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            df['collect_time'] = datetime.now()
            logger.info(f"总共收集到 {len(df)} 条舆情数据")
            return df
        else:
            logger.warning("没有收集到任何舆情数据")
            return pd.DataFrame()
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """
        计算情感得分 (-1到1之间)
        
        Args:
            text: 文本内容
            
        Returns:
            float: 情感得分
        """
        if not text:
            return 0.0
        
        try:
            # 使用SnowNLP进行基础情感分析
            s = SnowNLP(text)
            snow_score = s.sentiments  # 0-1，0.5为中性
            
            # 基于关键词的情感调整
            words = jieba.lcut(text)
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            
            # 关键词加权
            if positive_count + negative_count > 0:
                keyword_bias = (positive_count - negative_count) / (positive_count + negative_count)
                final_score = snow_score * 0.7 + (keyword_bias + 1) / 2 * 0.3
            else:
                final_score = snow_score
            
            # 转换为-1到1的范围
            normalized_score = (final_score - 0.5) * 2
            
            return round(normalized_score, 4)
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return 0.0
    
    def aggregate_sentiment_by_stock(self, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        按股票聚合情感数据
        
        Args:
            sentiment_df: 原始舆情数据
            
        Returns:
            DataFrame: 聚合后的情感数据
        """
        if sentiment_df.empty:
            return pd.DataFrame()
        
        # 按股票代码或名称分组
        group_column = 'stock_code' if 'stock_code' in sentiment_df.columns else 'stock_name'
        
        aggregated_data = []
        
        for stock, group in sentiment_df.groupby(group_column):
            # 计算平均情感得分
            avg_sentiment = group['sentiment_score'].mean()
            
            # 计算情感分布
            positive_count = len(group[group['sentiment_score'] > 0.1])
            negative_count = len(group[group['sentiment_score'] < -0.1])
            neutral_count = len(group[group['sentiment_score'].between(-0.1, 0.1)])
            total_count = len(group)
            
            # 计算平台权重得分（基于数据来源数量）
            platform_weights = group['platform'].value_counts()
            weighted_sentiment = sum(group['sentiment_score'] * 
                                   (platform_weights[group['platform']] / total_count))
            
            aggregated_item = {
                group_column: stock,
                'avg_sentiment_score': round(avg_sentiment, 4),
                'weighted_sentiment_score': round(weighted_sentiment, 4),
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_count': total_count,
                'sentiment_ratio': round(positive_count / total_count, 4) if total_count > 0 else 0,
                'last_update': group['collect_time'].max()
            }
            
            aggregated_data.append(aggregated_item)
        
        return pd.DataFrame(aggregated_data)
    
    def filter_sentiment_data(self, sentiment_df: pd.DataFrame, 
                            min_sentiment_confidence: float = 0.3) -> pd.DataFrame:
        """
        过滤低置信度的情感数据
        
        Args:
            sentiment_df: 原始舆情数据
            min_sentiment_confidence: 最小情感置信度
            
        Returns:
            DataFrame: 过滤后的数据
        """
        # 基于数据量的权重过滤
        grouped = sentiment_df.groupby(['stock_code' if 'stock_code' in sentiment_df.columns else 'stock_name'])
        
        confidence_data = []
        for name, group in grouped:
            confidence_score = min(len(group) / 10, 1.0)  # 数据量置信度
            
            if confidence_score >= min_sentiment_confidence:
                confidence_data.extend(group.to_dict('records'))
        
        return pd.DataFrame(confidence_data)

# 便捷函数
def get_sector_sentiment(sector: str, stock_codes: List[str], 
                        stock_names: List[str], days: int = 7) -> pd.DataFrame:
    """获取板块整体舆情数据"""
    analyzer = SentimentAnalyzer()
    
    # 收集舆情数据
    sentiment_data = analyzer.collect_all_sentiment_data(stock_codes, stock_names, days)
    
    if sentiment_data.empty:
        return pd.DataFrame()
    
    # 聚合数据
    aggregated = analyzer.aggregate_sentiment_by_stock(sentiment_data)
    aggregated['sector'] = sector
    
    return aggregated

def analyze_all_sectors_sentiment(sectors_data: Dict[str, Dict[str, pd.DataFrame]], 
                                days: int = 7) -> pd.DataFrame:
    """分析所有板块的舆情数据"""
    analyzer = SentimentAnalyzer()
    all_sentiment_data = []
    
    for sector, stocks_data in sectors_data.items():
        logger.info(f"正在分析 {sector} 板块舆情...")
        
        # 获取板块内的股票代码和名称
        stock_codes = list(stocks_data.keys())
        stock_names = []  # 这里需要从股票数据中提取名称
        
        # 简化处理：使用代码作为名称
        stock_names = stock_codes
        
        # 收集舆情数据
        sector_sentiment = get_sector_sentiment(sector, stock_codes, stock_names, days)
        
        if not sector_sentiment.empty:
            all_sentiment_data.append(sector_sentiment)
        
        time.sleep(1)  # 避免请求过频
    
    if all_sentiment_data:
        combined_df = pd.concat(all_sentiment_data, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()
