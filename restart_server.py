#!/usr/bin/env python3
"""
重启美易在线答疑服务器
"""

import os
import sys
import subprocess
import time

def stop_existing_processes():
    """停止现有的Python进程"""
    try:
        # 查找并停止所有Python进程
        result = subprocess.run(['wmic', 'process', 'where', "name='python.exe'", 'call', 'terminate'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 已停止现有的Python进程")
        else:
            print("⚠️  没有找到正在运行的Python进程")
    except Exception as e:
        print(f"停止进程时出错: {e}")

def start_server():
    """启动服务器"""
    print("🚀 启动美易在线答疑服务器...")

    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 启动服务器
    subprocess.Popen([sys.executable, 'web_app_final.py'])

    print("✅ 服务器启动成功")
    print("📱 本地访问地址: http://localhost:5000")
    print("🌐 外部访问地址: http://0.0.0.0:5000")
    print("🔧 管理员入口: http://localhost:5000/admin")
    print("🔍 测试页面: http://localhost:5000/test-hidden")

if __name__ == "__main__":
    print("=" * 50)
    print("美易在线答疑服务器重启工具")
    print("=" * 50)

    # 停止现有进程
    stop_existing_processes()

    # 等待一秒
    time.sleep(1)

    # 启动新服务器
    start_server()

    print("\n" + "=" * 50)
    print("服务器已在后台运行")
    print("=" * 50)