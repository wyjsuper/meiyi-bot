#!/usr/bin/env python3
"""
美纳里尼合规报销智能助手 - 运行脚本
"""

import sys
import os
import argparse

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description='美纳里尼合规报销智能助手')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5003, help='端口号 (默认: 5003)')
    parser.add_argument('--ngrok', action='store_true', help='启用Ngrok隧道')

    args = parser.parse_args()

    print("美纳里尼合规报销智能助手")
    print("=" * 50)
    print("正在启动Web应用...")
    print(f"本地访问地址: http://localhost:{args.port}")
    print(f"外部访问地址: http://0.0.0.0:{args.port}")
    print("=" * 50)

    if args.ngrok:
        from start_with_ngrok import main as ngrok_main
        ngrok_main()
    else:
        from web_app_final import app
        app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()