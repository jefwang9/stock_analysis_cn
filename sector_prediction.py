"""
板块预测模型模块
基于历史数据和舆情分析预测板块涨跌
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any, Optional
import joblib
import logging
from config import settings

logger = logging.getLogger(__name__)

class SectorPredictionModel:
    """板块预测模型"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_scores = {}
        
    def prepare_features(self, historical_data: Dict[str, pd.DataFrame], 
                        sentiment_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        准备特征数据
        
        Args:
            historical_data: 历史股票数据
            sentiment_data: 舆情数据
            
        Returns:
            Tuple[DataFrame, Series]: 特征矩阵和目标变量
        """
        features_list = []
        targets_list = []
        
        for stock_code, stock_data in historical_data.items():
            if stock_data.empty:
                continue
            
            # 技术指标特征
            tech_features = self._extract_technical_features(stock_data)
            
            # 舆情特征
            sentiment_features = self._extract_sentiment_features(stock_code, sentiment_data)
            
            # 市场情绪特征
            market_features = self._extract_market_features(stock_data)
            
            # 组合特征
            combined_features = {**tech_features, **sentiment_features, **market_features}
            combined_features['stock_code'] = stock_code
            
            features_list.append(combined_features)
            
            # 计算目标变量（下一日涨跌幅）
            current_close = stock_data['Close'].iloc[-1]
            next_close = stock_data['Close'].shift(-1).iloc[-1]
            
            if pd.notna(next_close):
                target = (next_close - current_close) / current_close * 100
                targets_list.append(target)
            else:
                targets_list.append(0)
        
        features_df = pd.DataFrame(features_list)
        targets_series = pd.Series(targets_list)
        
        # 处理缺失值
        features_df = features_df.fillna(features_df.mean())
        
        return features_df, targets_series




    def _extract_technical_features(self, stock_data: pd.DataFrame) -> Dict[str, float]:
        """提取技术要求特征"""
        latest_data = stock_data.iloc[-1]
        
        features = {}
        
        # 移动平均线
        features['MA5'] = latest_data.get('MA5', 0)
        features['MA10'] = latest_data.get('MA10', 0)
        features['MA20'] = latest_data.get('MA20', 0)
        features['MA30'] = latest_data.get('MA30', 0)
        
        # MA相对于价格的位置
        current_price = latest_data['Close']
        features['price_vs_MA5'] = current_price / latest_data.get('MA5', current_price) - 1
        features['price_vs_MA10'] = current_price / latest_data.get('MA10', current_price) - 1
        features['price_vs_MA20'] = current_price / latest_data.get('MA20', current_price) - 1
        
        # RSI
        features['RSI'] = latest_data.get('RSI', 50)
        features['RSI_oversold'] = 1 if features['RSI'] < 30 else 0
        features['RSI_overbought'] = 1 if features['RSI'] > 70 else 0
        
        # MACD
        features['MACD'] = latest_data.get('MACD', 0)
        features['MACD_signal'] = latest_data.get('MACD_signal', 0)
        features['MACD_golden_cross'] = 1 if features['MACD'] > features['MACD_signal'] else 0
        
        # KDJ
        features['KDJ_K'] = latest_data.get('KDJ_K', 50)
        features['KDJ_D'] = latest_data.get('KDJ_D', 50)
        features['KDJ_J'] = latest_data.get('KDJ_J', 50)
        features['KDJ_golden_cross'] = 1 if features['KDJ_K'] > features['KDJ_D'] else 0
        
        # 布林带
        bb_mid = latest_data.get('BOLL_mid', current_price)
        bb_upper = latest_data.get('BOLL_upper', current_price)
        bb_lower = latest_data.get('BOLL_lower', current_price)
        
        features['BB_position'] = (current_price - bb_lower) / (bb_upper - bb_lower)
        features['BB_squeeze'] = 1 if (bb_upper - bb_lower) / bb_mid < 0.05 else 0
        
        # WR威廉指标
        features['WR'] = latest_data.get('WR', -50)
        
        # 成交量
        features['volume'] = latest_data.get('Volume', 0)
        features['volume_ma5'] = stock_data['Volume'].rolling(5).mean().iloc[-1] if len(stock_data) >= 5 else features['volume']
        features['volume_ratio'] = features['volume'] / features['volume_ma5'] if features['volume_ma5'] != 0 else 1
        
        # 价格变化
        features['daily_change'] = stock_data['Change_pct'].iloc[-1] if 'Change_pct' in stock_data.columns else 0
        features['price_change_ma5'] = stock_data['Close'].pct_change().rolling(5).mean().iloc[-1]
        features['volatility'] = stock_data['Close'].pct_change().std()
        
        return features
    
    def _extract_sentiment_features(self, stock_code: str, 
                                  sentiment_data: pd.DataFrame) -> Dict[str, float]:
        """提取舆情特征"""
        # 获取该股票的舆情数据
        stock_sentiment = sentiment_data[
            (sentiment_data['stock_code'] == stock_code) | 
            (sentiment_data['stock_name'] == stock_code)
        ]
        
        if stock_sentiment.empty:
            return {
                'sentiment_score': 0.0,
                'sentiment_positive_ratio': 0.5,
                'sentiment_count': 0,
                'sentiment_volatility': 0.0
            }
        
        latest_sentiment = stock_sentiment.iloc[-1]
        
        return {
            'sentiment_score': latest_sentiment.get('avg_sentiment_score', 0.0),
            'sentiment_positive_ratio': latest_sentiment.get('sentiment_ratio', 0.5),
            'sentiment_count': latest_sentiment.get('total_count', 0),
            'sentiment_volatility': stock_sentiment['avg_sentiment_score'].std() if len(stock_sentiment) > 1 else 0.0
        }
    
    def _extract_market_features(self, stock_data: pd.DataFrame) -> Dict[str, float]:
        """提取市场情绪特征"""
        latest = stock_data.iloc[-1]
        
        # 基于价格位置的市场特征
        high_10d = stock_data['High'].rolling(10).max().iloc[-1]
        low_10d = stock_data['Low'].rolling(10).min().iloc[-1]
        current_price = latest['Close']
        
        features = {
            'price_position_10d': (current_price - low_10d) / (high_10d - low_10d) if high_10d != low_10d else 0.5,
            'relative_volume': features.get('volume_ratio', 1.0),
            'price_momentum_5d': stock_data['Close'].pct_change(5).iloc[-1],
            'trend_strength': abs(stock_data['Close'].rolling(10).mean().pct_change().iloc[-1]),
            'gap_vs_yesterday': (current_price - stock_data['Open'].iloc[-1]) / stock_data['Open'].iloc[-1]
        }
        
        return features
    
    def train_sector_model(self, sector: str, features_df: pd.DataFrame, 
                         targets_series: pd.Series) -> Dict[str, Any]:
        """
        训练板块预测模型
        
        Args:
            sector: 板块名称
            features_df: 特征数据
            targets_series: 目标变量
            
        Returns:
            Dict: 训练结果
        """
        # 移除非数值列
        feature_columns = features_df.select_dtypes(include=[np.number]).columns
        X = features_df[feature_columns]
        y = targets_series
        
        # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 分割训练和测试数据
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # 定义多个模型进行集成
        models_dict = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'gbm': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'xgb': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'lightgbm': lgb.LGBMRegressor(n_estimators=100, random_state=42)
        }
        
        model_scores = {}
        trained_models = {}
        
        for model_name, model in models_dict.items():
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测
            y_pred = model.predict(X_test)
            
            # 计算评分
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            model_scores[model_name] = {
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'accuracy': self._calculate_direction_accuracy(y_test, y_pred)
            }
            
            trained_models[model_name] = model
        
        # 选择最佳模型
        best_model_name = max(model_scores.keys(), key=lambda x: model_scores[x]['r2'])
        best_model = trained_models[best_model_name]
        
        # 保存模型和标准化器
        self.models[sector] = best_model
        self.scalers[sector] = scaler
        self.model_scores[sector] = model_scores[best_model_name]
        
        # 特征重要性
        if hasattr(best_model, 'feature_importances_'):
            self.feature_importance[sector] = dict(zip(feature_columns, best_model.feature_importances_))
        
        logger.info(f"板块 {sector} 模型训练完成，最佳模型: {best_model_name}, R²: {model_scores[best_model_name]['r2']:.4f}")
        
        return {
            'best_model': best_model_name,
            'scores': model_scores,
            'feature_count': len(feature_columns),
            'training_samples': len(y_train),
            'test_samples': len(y_test)
        }
    
    def _calculate_direction_accuracy(self, y_true: pd.Series, y_pred: pd.Series) -> float:
        """计算方向准确率"""
        true_direction = np.sign(y_true)
        pred_direction = np.sign(y_pred)
        accuracy = np.mean(true_direction == pred_direction)
        return accuracy
    
    def predict_sector_performance(self, sector: str, features_df: pd.DataFrame) -> float:
        """
        预测板块表现
        
        Args:
            sector: 板块名称
            features_df: 特征数据
            
        Returns:
            float: 预测的涨跌幅
        """
        if sector not in self.models:
            logger.error(f"板块 {sector} 的模型未训练")
            return 0.0
        
        try:
            model = self.models[sector]
            scaler = self.scalers[sector]
            
            # 获取数值特征
            feature_columns = [col for col in features_df.columns 
                             if features_df[col].dtype in ['float64', 'int64']]
            X = features_df[feature_columns].fillna(0)
            
            # 标准化
            X_scaled = scaler.transform(X)
            
            # 预测
            prediction = model.predict(X_scaled)[0]
            
            logger.info(f"板块 {sector} 预测涨跌幅: {prediction:.2f}%")
            return prediction
            
        except Exception as e:
            logger.error(f"预测板块 {sector} 表现失败: {e}")
            return 0.0
    
    def predict_all_sectors(self, all_features: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        预测所有板块表现
        
        Args:
            all_features: 所有板块的特征数据
            
        Returns:
            DataFrame: 预测结果
        """
        predictions = []
        
        for sector, features_df in all_features.items():
            pred_score = self.predict_sector_performance(sector, features_df)
            
            predictions.append({
                'sector': sector,
                'predicted_change': pred_score,
                'confidence': self._calculate_prediction_confidence(features_df),
                'prediction_time': datetime.now()
            })
        
        predictions_df = pd.DataFrame(predictions)
        
        # 排序获取涨跌前三
        predictions_df['change_abs'] = abs(predictions_df['predicted_change'])
        top_gainers = predictions_df.nlargest(settings.trading.predict_top_n, 'predicted_change')
        top_losers = predictions_df.nsmallest(settings.trading.predict_bottom_n, 'predicted_change')
        
        logger.info(f"预测涨幅前三板块: {top_gainers['sector'].tolist()}")
        logger.info(f"预测跌幅前三板块: {top_losers['sector'].tolist()}")
        
        return predictions_df
    
    def _calculate_prediction_confidence(self, features_df: pd.DataFrame) -> float:
        """计算预测置信度"""
        # 基于数据完整性和特征值的合理性计算置信度
        feature_completeness = 1 - features_df.isnull().sum().sum() / (len(features_df.columns) * len(features_df))
        
        # 简化置信度计算
        confidence = feature_completeness * 0.8 + 0.2
        
        return confidence
    
    def save_model(self, sector: str, model_path: str = None):
        """保存模型"""
        if model_path is None:
            model_path = f"{settings.models_dir}/{sector}_model.pkl"
        
        save_data = {
            'model': self.models.get(sector),
            'scaler': self.scalers.get(sector),
            'scores': self.model_scores.get(sector),
            'feature_importance': self.feature_importance.get(sector),
            'timestamp': datetime.now()
        }
        
        joblib.dump(save_data, model_path)
        logger.info(f"板块 {sector} 模型已保存到 {model_path}")
    
    def load_model(self, sector: str, model_path: str = None):
        """加载模型"""
        if model_path is None:
            model_path = f"{settings.models_dir}/{sector}_model.pkl"
        
        try:
            save_data = joblib.load(model_path)
            
            self.models[sector] = save_data['model']
            self.scalers[sector] = save_data['scaler']
            self.model_scores[sector] = save_data.get('scores')
            self.feature_importance[sector] = save_data.get('feature_importance')
            
            logger.info(f"板块 {sector} 模型已从 {model_path} 加载")
            
        except Exception as e:
            logger.error(f"加载板块 {sector} 模型失败: {e}")

# 便捷函数
def prepare_sector_features(sectors_data: Dict[str, Dict[str, pd.DataFrame]], 
                          sentiment_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """为所有板块准备特征数据"""
    predictor = SectorPredictionModel()
    all_features = {}
    
    for sector, stocks_data in sectors_data.items():
        logger.info(f"正在为 {sector} 板块准备特征...")
        
        features_df, targets = predictor.prepare_features(stocks_data, sentiment_data)
        all_features[sector] = features_df
    
    return all_features

def train_all_sector_samples(all_features: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """训练所有板块的预测模型"""
    predictor = SectorPredictionModel()
    training_results = {}
    
    for sector, features_df in all_features.items():
        logger.info(f"正在训练 {sector} 板块模型...")
        
        # 为训练准备目标变量（这里简化处理，实际应该从历史数据计算）
        targets = pd.Series(np.random.normal(0, 2, len(features_df)))  # 临时目标变量
        
        result = predictor.train_sector_model(sector, features_df, targets)
        training_results[sector] = result
        
        # 保存模型
        predictor.save_model(sector)
    
    return training_results
