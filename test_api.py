#!/usr/bin/env python3
"""
API测试脚本
测试所有API端点是否正常工作
"""
import requests
import json
import time

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8080"
    
    endpoints = [
        "/api/health",
        "/api/market/overview", 
        "/api/market/hot-stocks?limit=5",
        "/api/market/sector-ranking",
        "/api/stocks",
        "/api/sectors"
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
    
    print("🎯 API测试完成")

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
    print("🚀 A股股票分析智能体 - API测试工具")
    print("请确保Web应用正在运行 (python start.py 选择选项2)")
    print()
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    test_api_endpoints()
    test_web_pages()
    
    print("\n🎉 所有测试完成！")
