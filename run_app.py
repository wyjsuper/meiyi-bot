#!/usr/bin/env python3
"""
启动脚本，自动配置环境变量并启动Streamlit应用
"""
import os
import subprocess
import sys

# 设置环境变量
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"

# 启动命令
cmd = [
    "streamlit",
    "run",
    "app_simple.py",
    "--server.port", "8501",
    "--server.address", "0.0.0.0",
    "--server.headless", "true"
]

print("正在启动美易机器人...")
print(f"命令: {' '.join(cmd)}")

try:
    # 启动应用
    process = subprocess.Popen(cmd, cwd=os.getcwd())
    print(f"应用已启动，PID: {process.pid}")
    print("访问地址: http://localhost:8501")

    # 等待进程结束
    process.wait()
except KeyboardInterrupt:
    print("\n正在停止应用...")
    process.terminate()
except Exception as e:
    print(f"启动失败: {e}")