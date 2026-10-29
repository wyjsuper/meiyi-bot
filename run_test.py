#!/usr/bin/env python3
"""
测试运行脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from web_app_final import app

    print("美纳里尼合规报销智能助手")
    print("=" * 50)
    print("正在启动Web应用...")
    print("访问地址: http://localhost:5003")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5003, debug=True)

except Exception as e:
    print(f"启动失败: {e}")
    input("按Enter键退出...")