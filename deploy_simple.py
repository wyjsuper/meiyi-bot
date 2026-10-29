#!/usr/bin/env python3
"""
美易机器人简单外网部署方案
使用Python内置HTTP服务器
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os
import sys
from urllib.parse import urlparse, parse_qs

class SimpleAppHandler(http.server.SimpleHTTPRequestHandler):
    """简单的HTTP处理器"""

    def __init__(self, *args, **kwargs):
        # 设置目录为当前目录
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        # 解析URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # 如果是根路径，重定向到应用
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            # 生成HTML页面
            html_content = self.generate_html_page()
            self.wfile.write(html_content.encode('utf-8'))

        # 处理API请求
        elif path.startswith('/api/'):
            self.handle_api_request(parsed_path)

        else:
            # 默认处理静态文件
            super().do_GET()

    def generate_html_page(self):
        """生成主页面HTML"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美易在线答疑</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .chat-container {
            padding: 30px;
            height: 500px;
            display: flex;
            flex-direction: column;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 80%;
        }

        .message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }

        .message.assistant {
            background: #e9ecef;
            color: #333;
        }

        .input-container {
            display: flex;
            gap: 10px;
        }

        .input-container input {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }

        .input-container input:focus {
            border-color: #667eea;
        }

        .input-container button {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .input-container button:hover {
            background: #5a67d8;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }

        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 美易在线答疑</h1>
            <p>美纳里尼中国合规智能助手</p>
        </div>

        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message assistant">
                    您好！我是美易机器人，可以帮您解答合规和报销相关问题。请输入您的问题，比如：
                    <br>- 为什么重置密码的邮件一直收不到？
                    <br>- 报销流程是什么？
                    <br>- 如何登录系统？
                </div>
            </div>

            <div class="input-container">
                <input type="text" id="userInput" placeholder="请输入您的问题..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">发送</button>
            </div>
        </div>
    </div>

    <script>
        const messagesContainer = document.getElementById('messages');
        const userInput = document.getElementById('userInput');

        function addMessage(content, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = content;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function showLoading() {
            addMessage('<div class="loading"><div class="spinner"></div> 正在搜索知识库...</div>', 'assistant');
        }

        function removeLoading() {
            const messages = messagesContainer.querySelectorAll('.message');
            const lastMessage = messages[messages.length - 1];
            if (lastMessage && lastMessage.innerHTML.includes('spinner')) {
                lastMessage.remove();
            }
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // 添加用户消息
            addMessage(message, 'user');
            userInput.value = '';

            // 显示加载状态
            showLoading();

            try {
                // 调用后端API
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: message })
                });

                const data = await response.json();

                // 移除加载状态
                removeLoading();

                // 添加回答
                add(data.answer, 'assistant');

            } catch (error) {
                removeLoading();
                add('抱歉，服务暂时不可用。请稍后重试。', 'assistant');
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
    </script>
</body>
</html>'''

    def handle_api_request(self, parsed_path):
        """处理API请求"""
        # 这里可以添加API处理逻辑
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

        # 返回简单的JSON响应
        response = {
            "status": "ok",
            "message": "API is working"
        }

        import json
        self.wfile.write(json.dumps(response).encode('utf-8'))

def start_server(port=8080):
    """启动HTTP服务器"""
    handler = SimpleAppHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server started at http://localhost:{port}")
        print(f"External URL: http://0.0.0.0:{port}")
        print("Press Ctrl+C to stop the server")

        try:
            # 自动打开浏览器
            webbrowser.open(f"http://localhost:{port}")

            # 启动服务器
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            httpd.shutdown()

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='美易机器人简单HTTP服务器')
    parser.add_argument('--port', type=int, default=8080, help='端口号 (默认: 8080)')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')

    args = parser.parse_args()

    if not args.no_browser:
        print("浏览器将自动打开...")

    start_server(args.port)

if __name__ == "__main__":
    main()