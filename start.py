#!/usr/bin/env python3
"""
A股股票分析智能体 - 启动脚本
提供稳定的启动方式，避免端口冲突
"""
import sys
import os
import subprocess
import time
import signal
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def kill_port_processes(port):
    """杀死占用指定端口的进程"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid])
                    print(f"已杀死占用端口{port}的进程: {pid}")
    except Exception as e:
        print(f"清理端口{port}时出错: {e}")

def start_api_server():
    """启动API服务器"""
    print("🚀 启动API服务器...")
    kill_port_processes(8000)
    
    try:
        from src.web.api_server import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"启动API服务器失败: {e}")

def start_web_app():
    """启动Web应用"""
    print("🌐 启动Web应用...")
    kill_port_processes(8080)
    
    try:
        from src.web.web_app import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    except Exception as e:
        print(f"启动Web应用失败: {e}")

def run_historical_analysis():
    """运行历史数据分析"""
    print("📊 运行历史数据分析...")
    try:
        from examples.example_historical import main
        main()
    except Exception as e:
        print(f"历史数据分析失败: {e}")

def run_realtime_analysis():
    """运行实时数据分析"""
    print("⚡ 运行实时数据分析...")
    try:
        from examples.example_realtime import main
        main()
    except Exception as e:
        print(f"实时数据分析失败: {e}")

def run_backtest():
    """运行回测"""
    print("🔄 运行回测...")
    try:
        from src.trading.backtesting import main
        main()
    except Exception as e:
        print(f"回测失败: {e}")

def generate_report():
    """生成报告"""
    print("📋 生成报告...")
    try:
        from src.trading.report_generator import main
        main()
    except Exception as e:
        print(f"生成报告失败: {e}")

def main():
    """主函数"""
    print("🚀 A股股票分析智能体")
    print("=" * 50)
    print("1. 启动API服务器 (端口8000)")
    print("2. 启动Web界面 (端口8080)")
    print("3. 运行历史数据分析")
    print("4. 运行实时数据分析")
    print("5. 运行回测")
    print("6. 生成报告")
    print("7. 清理端口并退出")
    print("=" * 50)
    
    try:
        choice = input("请选择要执行的操作 (1-7): ").strip()
        
        if choice == "1":
            start_api_server()
        elif choice == "2":
            start_web_app()
        elif choice == "3":
            run_historical_analysis()
        elif choice == "4":
            run_realtime_analysis()
        elif choice == "5":
            run_backtest()
        elif choice == "6":
            generate_report()
        elif choice == "7":
            print("清理端口...")
            kill_port_processes(8000)
            kill_port_processes(8080)
            print("端口已清理，程序退出")
        else:
            print("无效选择，请重新运行程序")
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except EOFError:
        print("\n程序退出")
    except Exception as e:
        print(f"程序执行出错: {e}")

if __name__ == "__main__":
    main()
