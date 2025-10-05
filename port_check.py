#!/usr/bin/env python3
"""
简单的端口检查工具
快速查看端口占用情况
"""
import subprocess
import sys

def check_port(port):
    """检查指定端口"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"🔴 端口 {port} 被占用:")
            print(result.stdout)
            return True
        else:
            print(f"🟢 端口 {port} 空闲")
            return False
    except Exception as e:
        print(f"❌ 检查端口 {port} 时出错: {e}")
        return False

def check_common_ports():
    """检查常用端口"""
    ports = [8000, 8080, 3000, 5000, 9000]
    
    print("🌐 检查常用端口:")
    print("=" * 30)
    
    occupied = []
    for port in ports:
        if check_port(port):
            occupied.append(port)
        print()
    
    if occupied:
        print(f"📋 被占用的端口: {', '.join(map(str, occupied))}")
    else:
        print("✅ 所有常用端口都空闲")

def kill_port(port):
    """杀死占用端口的进程"""
    try:
        # 获取占用端口的进程ID
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid])
                    print(f"💀 已杀死进程 {pid}")
            print(f"✅ 端口 {port} 已清理")
        else:
            print(f"✅ 端口 {port} 没有被占用")
    except Exception as e:
        print(f"❌ 清理端口 {port} 时出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            if len(sys.argv) > 2:
                port = int(sys.argv[2])
                check_port(port)
            else:
                check_common_ports()
        elif sys.argv[1] == "kill":
            if len(sys.argv) > 2:
                port = int(sys.argv[2])
                kill_port(port)
            else:
                print("请指定端口号")
        else:
            print("用法:")
            print("  python port_check.py check [端口号]  # 检查端口")
            print("  python port_check.py kill [端口号]   # 清理端口")
    else:
        check_common_ports()
