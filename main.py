#!/usr/bin/env python3
"""
A股股票分析智能体 - 主入口文件
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    print("🚀 A股股票分析智能体")
    print("=" * 50)
    print("1. 启动API服务器")
    print("2. 启动Web界面")
    print("3. 运行历史数据分析")
    print("4. 运行实时数据分析")
    print("5. 运行回测")
    print("6. 生成报告")
    print("=" * 50)
    
    choice = input("请选择要执行的操作 (1-6): ").strip()
    
    if choice == "1":
        from src.web.api_server import app
        import uvicorn
        print("启动API服务器...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif choice == "2":
        from src.web.web_app import app
        import uvicorn
        print("启动Web界面...")
        uvicorn.run(app, host="0.0.0.0", port=8080)
    elif choice == "3":
        from examples.example_historical import main as run_historical
        print("运行历史数据分析...")
        run_historical()
    elif choice == "4":
        from examples.example_realtime import main as run_realtime
        print("运行实时数据分析...")
        run_realtime()
    elif choice == "5":
        from src.trading.backtesting import main as run_backtest
        print("运行回测...")
        run_backtest()
    elif choice == "6":
        from src.trading.report_generator import main as generate_report
        print("生成报告...")
        generate_report()
    else:
        print("无效选择，请重新运行程序")

if __name__ == "__main__":
    main()
