#!/usr/bin/env python3
"""
Content Pilot GUI 快速启动脚本
作者: Agnes AI Assistant
日期: 2026-11-16
"""

import subprocess
import sys
import os
import time

def check_environment():
    """检查运行环境"""
    print("=" * 60)
    print("BingDashan Content Pilot - 环境检查")
    print("=" * 60)
    
    # 检查Python
    python_path = "/root/.local/bin/python3.12"
    if not os.path.exists(python_path):
        python_path = "python3"
    
    print(f"\n[1/4] Python环境: {python_path}")
    try:
        result = subprocess.run([python_path, "--version"], capture_output=True, text=True, timeout=5)
        print(f"  ✓ {result.stdout.strip()}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # 检查虚拟环境
    venv_path = "/opt/content-pilot/.venv"
    print(f"\n[2/4] 虚拟环境: {venv_path}")
    if os.path.exists(venv_path):
        print("  ✓ 已存在")
    else:
        print("  ⚠ 需要创建...")
        try:
            subprocess.run([python_path, "-m", "venv", venv_path], check=True, timeout=60)
            print("  ✓ 创建成功")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            return False
    
    # 检查项目目录
    project_path = "/opt/content-pilot"
    print(f"\n[3/4] 项目目录: {project_path}")
    if os.path.exists(project_path):
        print(f"  ✓ 存在 ({len(os.listdir(project_path))} 个文件)")
    else:
        print(f"  ✗ 不存在")
        return False
    
    # 检查端口可用性
    print(f"\n[4/4] 端口检查: 8080")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8080))
        if result == 0:
            print("  ⚠ 端口被占用，将使用8081")
            port = 8081
        else:
            print("  ✓ 可用")
            port = 8080
        sock.close()
    except Exception as e:
        print(f"  ⚠ 无法检查端口: {e}")
        port = 8080
    
    return True

def start_gui(port=8080):
    """启动GUI服务"""
    print("\n" + "=" * 60)
    print("正在启动Content Pilot GUI...")
    print("=" * 60)
    
    activate_script = "/opt/content-pilot/.venv/bin/activate"
    if sys.platform == "win32":
        activate_script = "/opt/content-pilot/.venv/Scripts/activate"
    
    cmd = f"source {activate_script} && content-pilot gui --port {port}"
    
    print(f"\n访问地址: http://localhost:{port}")
    print(f"\n按 Ctrl+C 停止服务\n")
    
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print("\n服务已停止")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="启动Content Pilot GUI")
    parser.add_argument("--port", type=int, default=8080, help="端口号")
    args = parser.parse_args()
    
    if check_environment():
        start_gui(args.port)
    else:
        print("\n环境检查失败，请检查上述错误信息")
        sys.exit(1)