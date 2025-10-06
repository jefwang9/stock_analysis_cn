#!/usr/bin/env python3
"""
增强版API测试脚本
专注于板块预测模型功能测试
"""
import requests
import json
import time
from datetime import datetime, timedelta

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8080"
    
    # 移除实时数据端点，专注于板块预测功能
    endpoints = [
        "/api/health",
        "/api/stocks",
        "/api/sectors",
        "/api/models/performance?days=7",
        "/api/backtest/performance?days=7"
    ]
    
    print("🧪 开始测试API端点...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"测试: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功 - 状态码: {response.status_code}")
                if 'status' in data:
                    print(f"   状态: {data['status']}")
                if 'count' in data:
                    print(f"   数据量: {data['count']}")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                print(f"   响应: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败 - 服务器未启动")
        except requests.exceptions.Timeout:
            print(f"❌ 超时 - 请求时间过长")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("-" * 30)
        time.sleep(1)
    
    print("🎯 API端点测试完成")

def test_sector_prediction():
    """测试板块预测功能"""
    base_url = "http://localhost:8080"
    
    print("\n🔮 开始测试板块预测功能...")
    print("=" * 50)
    
    # 测试每日预测
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        url = f"{base_url}/api/models/predict-daily"
        data = {"target_date": tomorrow}
        
        print(f"测试每日板块预测: {tomorrow}")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 预测成功 - 预测板块数: {result.get('count', 0)}")
            
            if 'data' in result and result['data']:
                predictions = result['data']
                print("   预测结果:")
                for pred in predictions[:3]:  # 显示前3个
                    print(f"   - {pred['sector']}: {pred['predicted_change']:.2f}% (置信度: {pred.get('confidence', 0):.2f})")
        else:
            print(f"❌ 预测失败 - 状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 预测测试错误: {e}")
    
    print("-" * 30)
    
    # 测试模型表现
    try:
        url = f"{base_url}/api/models/performance?days=7"
        print("测试模型表现摘要")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取模型表现成功")
            
            if 'data' in result and 'overall_stats' in result['data']:
                stats = result['data']['overall_stats']
                print(f"   总体准确率: {stats.get('overall_accuracy', 0):.2%}")
                print(f"   预测次数: {stats.get('total_predictions', 0)}")
                print(f"   板块数: {stats.get('sectors_count', 0)}")
        else:
            print(f"❌ 获取模型表现失败 - 状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 模型表现测试错误: {e}")
    
    print("🎯 板块预测功能测试完成")

def test_daily_training():
    """测试每日训练功能"""
    base_url = "http://localhost:8080"
    
    print("\n🏋️ 开始测试每日训练功能...")
    print("=" * 50)
    
    try:
        url = f"{base_url}/api/models/daily-training"
        data = {"target_date": datetime.now().strftime('%Y-%m-%d')}
        
        print("测试每日训练启动")
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 训练启动成功 - 目标日期: {result.get('target_date')}")
            print(f"   消息: {result.get('message')}")
        else:
            print(f"❌ 训练启动失败 - 状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 每日训练测试错误: {e}")
    
    print("🎯 每日训练功能测试完成")

def test_web_pages():
    """测试Web页面"""
    base_url = "http://localhost:8080"
    
    pages = [
        "/",
        "/stocks",
        "/docs"
    ]
    
    print("\n🌐 开始测试Web页面...")
    print("=" * 50)
    
    for page in pages:
        try:
            url = f"{base_url}{page}"
            print(f"测试: {page}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    print(f"✅ 成功 - HTML页面")
                elif 'application/json' in content_type:
                    print(f"✅ 成功 - JSON响应")
                else:
                    print(f"✅ 成功 - {content_type}")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败 - 服务器未启动")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("-" * 30)
        time.sleep(1)
    
    print("🎯 Web页面测试完成")

if __name__ == "__main__":
    print("🚀 A股股票分析智能体 - 增强版API测试工具")
    print("专注于板块预测模型功能测试")
    print("请确保Web应用正在运行 (python start.py 选择选项2)")
    print()
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    test_api_endpoints()
    test_sector_prediction()
    test_daily_training()
    test_web_pages()
    
    print("\n🎉 所有测试完成！")
    print("📊 重点关注板块预测模型的准确率和表现")
