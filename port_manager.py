#!/usr/bin/env python3
"""
端口管理工具
查看和管理端口占用情况
"""
import subprocess
import sys
import os
import signal
import time

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def check_port_usage(port):
    """检查指定端口的使用情况"""
    print(f"🔍 检查端口 {port} 的使用情况...")
    print("=" * 50)
    
    # 使用lsof检查端口
    stdout, stderr, code = run_command(f"lsof -i :{port}")
    
    if code == 0 and stdout.strip():
        print("📊 端口占用详情:")
        print(stdout)
        
        # 提取PID
        lines = stdout.strip().split('\n')[1:]  # 跳过标题行
        pids = set()
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                try:
                    pid = int(parts[1])
                    pids.add(pid)
                except ValueError:
                    continue
        
        if pids:
            print(f"\n🔢 发现的进程ID: {', '.join(map(str, pids))}")
            return list(pids)
    else:
        print("✅ 端口未被占用")
        return []
    
    return []

def check_common_ports():
    """检查常用端口"""
    common_ports = [8000, 8080, 3000, 5000, 9000, 3001, 5001, 8001, 8081]
    
    print("🌐 检查常用端口占用情况...")
    print("=" * 50)
    
    occupied_ports = []
    
    for port in common_ports:
        stdout, stderr, code = run_command(f"lsof -i :{port}")
        if code == 0 and stdout.strip():
            occupied_ports.append(port)
            print(f"🔴 端口 {port} 被占用")
        else:
            print(f"🟢 端口 {port} 空闲")
    
    if occupied_ports:
        print(f"\n📋 被占用的端口: {', '.join(map(str, occupied_ports))}")
    else:
        print("\n✅ 所有常用端口都空闲")
    
    return occupied_ports

def kill_processes_by_port(port):
    """杀死占用指定端口的进程"""
    pids = check_port_usage(port)
    
    if not pids:
        print(f"✅ 端口 {port} 没有被占用")
        return
    
    print(f"\n⚠️  准备杀死占用端口 {port} 的进程...")
    
    for pid in pids:
        try:
            # 先尝试优雅关闭
            os.kill(pid, signal.SIGTERM)
            print(f"📤 发送SIGTERM信号到进程 {pid}")
            
            # 等待进程退出
            time.sleep(2)
            
            # 检查进程是否还在运行
            stdout, stderr, code = run_command(f"ps -p {pid}")
            if code == 0 and stdout.strip():
                # 强制杀死
                os.kill(pid, signal.SIGKILL)
                print(f"💀 强制杀死进程 {pid}")
            else:
                print(f"✅ 进程 {pid} 已优雅退出")
                
        except ProcessLookupError:
            print(f"✅ 进程 {pid} 已经不存在")
        except PermissionError:
            print(f"❌ 没有权限杀死进程 {pid}")
        except Exception as e:
            print(f"❌ 杀死进程 {pid} 时出错: {e}")

def kill_processes_by_name(name_pattern):
    """根据进程名模式杀死进程"""
    print(f"🔍 查找包含 '{name_pattern}' 的进程...")
    
    stdout, stderr, code = run_command(f"ps aux | grep '{name_pattern}' | grep -v grep")
    
    if code == 0 and stdout.strip():
        lines = stdout.strip().split('\n')
        pids = []
        
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                try:
                    pid = int(parts[1])
                    pids.append(pid)
                    print(f"📋 找到进程: {pid} - {' '.join(parts[10:])}")
                except ValueError:
                    continue
        
        if pids:
            print(f"\n⚠️  准备杀死 {len(pids)} 个进程...")
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"📤 发送SIGTERM信号到进程 {pid}")
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ 杀死进程 {pid} 时出错: {e}")
        else:
            print("✅ 没有找到匹配的进程")
    else:
        print("✅ 没有找到匹配的进程")

def show_network_connections():
    """显示网络连接"""
    print("🌐 当前网络连接...")
    print("=" * 50)
    
    stdout, stderr, code = run_command("netstat -an | grep LISTEN")
    
    if code == 0 and stdout.strip():
        print("📊 监听端口:")
        for line in stdout.strip().split('\n'):
            if any(port in line for port in ['8000', '8080', '3000', '5000', '9000']):
                print(f"  {line}")
    else:
        print("❌ 无法获取网络连接信息")

def main():
    """主函数"""
    print("🔧 端口管理工具")
    print("=" * 50)
    print("1. 检查指定端口")
    print("2. 检查常用端口")
    print("3. 杀死占用指定端口的进程")
    print("4. 杀死Python相关进程")
    print("5. 显示网络连接")
    print("6. 清理所有相关端口")
    print("=" * 50)
    
    try:
        choice = input("请选择操作 (1-6): ").strip()
        
        if choice == "1":
            port = input("请输入要检查的端口号: ").strip()
            try:
                port = int(port)
                check_port_usage(port)
            except ValueError:
                print("❌ 无效的端口号")
                
        elif choice == "2":
            check_common_ports()
            
        elif choice == "3":
            port = input("请输入要清理的端口号: ").strip()
            try:
                port = int(port)
                kill_processes_by_port(port)
            except ValueError:
                print("❌ 无效的端口号")
                
        elif choice == "4":
            kill_processes_by_name("python.*web")
            kill_processes_by_name("python.*api")
            kill_processes_by_name("uvicorn")
            
        elif choice == "5":
            show_network_connections()
            
        elif choice == "6":
            print("🧹 清理所有相关端口...")
            kill_processes_by_port(8000)
            kill_processes_by_port(8080)
            kill_processes_by_name("python.*web")
            kill_processes_by_name("python.*api")
            kill_processes_by_name("uvicorn")
            print("✅ 清理完成")
            
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")

if __name__ == "__main__":
    main()
