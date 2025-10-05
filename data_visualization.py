"""
数据可视化模块
提供各种图表和可视化功能
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from config import settings

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class DataVisualizer:
    """数据可视化器"""
    
    def __init__(self):
        self.colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'secondary': '#6c757d'
        }
    
    def create_stock_chart(self, stock_data: pd.DataFrame, 
                         stock_name: str = "股票", 
                         chart_type: str = "candlestick") -> go.Figure:
        """
        创建股票图表
        
        Args:
            stock_data: 股票数据
            stock_name: 股票名称
            chart_type: 图表类型 ("candlestick", "line", "volume")
            
        Returns:
            plotly图表对象
        """
        if stock_data.empty:
            return self._create_empty_chart("无数据")
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'{stock_name} 价格走势', '成交量'),
            row_width=[0.7, 0.3]
        )
        
        # K线图
        if chart_type == "candlestick" and all(col in stock_data.columns for col in ['Open', 'High', 'Low', 'Close']):
            fig.add_trace(
                go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name="K线"
                ),
                row=1, col=1
            )
        else:
            # 折线图
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    mode='lines',
                    name='收盘价',
                    line=dict(color=self.colors['primary'])
                ),
                row=1, col=1
            )
        
        # 移动平均线
        if 'MA5' in stock_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['MA5'],
                    mode='lines',
                    name='MA5',
                    line=dict(color=self.colors['warning'], width=1)
                ),
                row=1, col=1
            )
        
        if 'MA20' in stock_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['MA20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color=self.colors['info'], width=1)
                ),
                row=1, col=1
            )
        
        # 成交量
        if 'Volume' in stock_data.columns:
            colors = ['red' if close >= open else 'green' 
                     for close, open in zip(stock_data['Close'], stock_data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    name='成交量',
                    marker_color=colors
                ),
                row=2, col=1
            )
        
        # 更新布局
        fig.update_layout(
            title=f'{stock_name} 技术分析图表',
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def create_sector_performance_chart(self, sector_data: Dict[str, float], 
                                      chart_type: str = "bar") -> go.Figure:
        """
        创建板块表现图表
        
        Args:
            sector_data: 板块数据 {板块名: 涨跌幅}
            chart_type: 图表类型 ("bar", "pie", "treemap")
            
        Returns:
            plotly图表对象
        """
        if not sector_data:
            return self._create_empty_chart("无板块数据")
        
        # 转换为DataFrame
        df = pd.DataFrame(list(sector_data.items()), columns=['sector', 'change_pct'])
        df = df.sort_values('change_pct', ascending=False)
        
        if chart_type == "bar":
            # 柱状图
            colors = ['red' if x < 0 else 'green' for x in df['change_pct']]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df['sector'],
                    y=df['change_pct'],
                    marker_color=colors,
                    text=[f"{x:.2f}%" for x in df['change_pct']],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='板块涨跌幅排名',
                xaxis_title='板块',
                yaxis_title='涨跌幅 (%)',
                height=500,
                template='plotly_white'
            )
            
        elif chart_type == "pie":
            # 饼图（只显示前10个板块）
            top_sectors = df.head(10)
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=top_sectors['sector'],
                    values=abs(top_sectors['change_pct']),
                    textinfo='label+percent',
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='板块表现分布（前10名）',
                height=500,
                template='plotly_white'
            )
            
        elif chart_type == "treemap":
            # 树状图
            fig = go.Figure(go.Treemap(
                labels=df['sector'],
                values=abs(df['change_pct']),
                parents=[''] * len(df),
                textinfo='label+value',
                texttemplate='%{label}<br>%{value:.2f}%'
            ))
            
            fig.update_layout(
                title='板块表现树状图',
                height=500,
                template='plotly_white'
            )
        
        return fig
    
    def create_market_overview_chart(self, market_data: Dict[str, Any]) -> go.Figure:
        """
        创建市场概览图表
        
        Args:
            market_data: 市场数据
            
        Returns:
            plotly图表对象
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('主要指数', '市场统计', '涨跌分布', '情绪分析'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # 主要指数
        if 'indices' in market_data:
            indices = market_data['indices']
            index_names = list(indices.keys())
            index_changes = [indices[name]['change_pct'] for name in index_names]
            
            colors = ['red' if x < 0 else 'green' for x in index_changes]
            
            fig.add_trace(
                go.Bar(
                    x=index_names,
                    y=index_changes,
                    marker_color=colors,
                    name='指数涨跌幅'
                ),
                row=1, col=1
            )
        
        # 市场统计
        if 'market_stats' in market_data:
            stats = market_data['market_stats']
            
            # 涨跌分布饼图
            rising = stats.get('rising_stocks', 0)
            falling = stats.get('falling_stocks', 0)
            flat = stats.get('total_stocks', 0) - rising - falling
            
            fig.add_trace(
                go.Pie(
                    labels=['上涨', '下跌', '平盘'],
                    values=[rising, falling, flat],
                    name='涨跌分布'
                ),
                row=1, col=2
            )
            
            # 市场情绪指标
            sentiment_score = (rising - falling) / stats.get('total_stocks', 1) * 100
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=sentiment_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "市场情绪"},
                    gauge={
                        'axis': {'range': [-100, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-100, -50], 'color': "lightgray"},
                            {'range': [-50, 0], 'color': "yellow"},
                            {'range': [0, 50], 'color': "lightgreen"},
                            {'range': [50, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0
                        }
                    }
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title='市场概览仪表板',
            height=800,
            template='plotly_white'
        )
        
        return fig
    
    def create_prediction_chart(self, predictions: pd.DataFrame) -> go.Figure:
        """
        创建预测结果图表
        
        Args:
            predictions: 预测数据
            
        Returns:
            plotly图表对象
        """
        if predictions.empty:
            return self._create_empty_chart("无预测数据")
        
        # 按预测涨跌幅排序
        predictions = predictions.sort_values('predicted_change', ascending=False)
        
        fig = go.Figure()
        
        # 添加预测柱状图
        colors = ['red' if x < 0 else 'green' for x in predictions['predicted_change']]
        
        fig.add_trace(
            go.Bar(
                x=predictions['sector'],
                y=predictions['predicted_change'],
                marker_color=colors,
                text=[f"{x:.2f}%" for x in predictions['predicted_change']],
                textposition='auto',
                name='预测涨跌幅'
            )
        )
        
        # 添加置信度散点图
        fig.add_trace(
            go.Scatter(
                x=predictions['sector'],
                y=predictions['predicted_change'],
                mode='markers',
                marker=dict(
                    size=predictions['confidence'] * 20,
                    color=predictions['confidence'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="置信度")
                ),
                name='置信度',
                text=[f"置信度: {x:.2f}" for x in predictions['confidence']],
                hovertemplate='%{text}<br>预测: %{y:.2f}%<extra></extra>'
            )
        )
        
        fig.update_layout(
            title='板块预测结果',
            xaxis_title='板块',
            yaxis_title='预测涨跌幅 (%)',
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    def create_backtest_chart(self, performance_data: pd.DataFrame) -> go.Figure:
        """
        创建回测结果图表
        
        Args:
            performance_data: 回测性能数据
            
        Returns:
            plotly图表对象
        """
        if performance_data.empty:
            return self._create_empty_chart("无回测数据")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('准确率趋势', '置信度趋势', '上涨板块准确率', '下跌板块准确率'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 准确率趋势
        fig.add_trace(
            go.Scatter(
                x=performance_data['date'],
                y=performance_data['accuracy_rate'],
                mode='lines+markers',
                name='准确率',
                line=dict(color=self.colors['primary'])
            ),
            row=1, col=1
        )
        
        # 置信度趋势
        fig.add_trace(
            go.Scatter(
                x=performance_data['date'],
                y=performance_data['avg_confidence'],
                mode='lines+markers',
                name='平均置信度',
                line=dict(color=self.colors['info'])
            ),
            row=1, col=2
        )
        
        # 上涨板块准确率
        fig.add_trace(
            go.Scatter(
                x=performance_data['date'],
                y=performance_data['top_gainer_accuracy'],
                mode='lines+markers',
                name='上涨板块准确率',
                line=dict(color=self.colors['success'])
            ),
            row=2, col=1
        )
        
        # 下跌板块准确率
        fig.add_trace(
            go.Scatter(
                x=performance_data['date'],
                y=performance_data['top_loser_accuracy'],
                mode='lines+markers',
                name='下跌板块准确率',
                line=dict(color=self.colors['danger'])
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='回测性能分析',
            height=800,
            template='plotly_white'
        )
        
        return fig
    
    def create_sentiment_chart(self, sentiment_data: pd.DataFrame) -> go.Figure:
        """
        创建舆情分析图表
        
        Args:
            sentiment_data: 舆情数据
            
        Returns:
            plotly图表对象
        """
        if sentiment_data.empty:
            return self._create_empty_chart("无舆情数据")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('情感得分分布', '平台分布', '时间趋势', '情感强度'),
            specs=[[{"type": "histogram"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 情感得分分布
        fig.add_trace(
            go.Histogram(
                x=sentiment_data['sentiment_score'],
                nbinsx=20,
                name='情感得分分布'
            ),
            row=1, col=1
        )
        
        # 平台分布
        platform_counts = sentiment_data['platform'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=platform_counts.index,
                values=platform_counts.values,
                name='平台分布'
            ),
            row=1, col=2
        )
        
        # 时间趋势
        if 'publish_time' in sentiment_data.columns:
            sentiment_data['date'] = pd.to_datetime(sentiment_data['publish_time']).dt.date
            daily_sentiment = sentiment_data.groupby('date')['sentiment_score'].mean()
            
            fig.add_trace(
                go.Scatter(
                    x=daily_sentiment.index,
                    y=daily_sentiment.values,
                    mode='lines+markers',
                    name='情感趋势'
                ),
                row=2, col=1
            )
        
        # 情感强度
        sentiment_data['sentiment_intensity'] = abs(sentiment_data['sentiment_score'])
        intensity_counts = sentiment_data['sentiment_intensity'].value_counts().head(10)
        
        fig.add_trace(
            go.Bar(
                x=intensity_counts.index,
                y=intensity_counts.values,
                name='情感强度'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='舆情分析仪表板',
            height=800,
            template='plotly_white'
        )
        
        return fig
    
    def create_correlation_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """
        创建相关性热力图
        
        Args:
            data: 数据
            
        Returns:
            plotly图表对象
        """
        if data.empty:
            return self._create_empty_chart("无数据")
        
        # 计算相关性矩阵
        numeric_data = data.select_dtypes(include=[np.number])
        correlation_matrix = numeric_data.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='特征相关性热力图',
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """创建空图表"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400,
            template='plotly_white'
        )
        return fig
    
    def save_chart(self, fig: go.Figure, filename: str, format: str = "html"):
        """
        保存图表
        
        Args:
            fig: 图表对象
            filename: 文件名
            format: 格式 ("html", "png", "pdf")
        """
        try:
            if format == "html":
                fig.write_html(filename)
            elif format == "png":
                fig.write_image(filename)
            elif format == "pdf":
                fig.write_image(filename)
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            logger.info(f"图表已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存图表失败: {e}")

# 便捷函数
def create_stock_chart(stock_data: pd.DataFrame, stock_name: str = "股票") -> go.Figure:
    """创建股票图表"""
    visualizer = DataVisualizer()
    return visualizer.create_stock_chart(stock_data, stock_name)

def create_sector_chart(sector_data: Dict[str, float]) -> go.Figure:
    """创建板块图表"""
    visualizer = DataVisualizer()
    return visualizer.create_sector_performance_chart(sector_data)

def create_market_chart(market_data: Dict[str, Any]) -> go.Figure:
    """创建市场图表"""
    visualizer = DataVisualizer()
    return visualizer.create_market_overview_chart(market_data)
