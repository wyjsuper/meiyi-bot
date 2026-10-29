#!/usr/bin/env python3
"""
美纳里尼合规报销智能助手 - 优化精简版
"""

from flask import Flask, request, jsonify
import os
import re
from typing import List, Dict, Any
from datetime import datetime

app = Flask(__name__)

# 配置参数
MAX_ANSWERS = 2
SIMILARITY_THRESHOLD = 0.4

# 知识库数据
qa_pairs = []
initialized = False

class SearchEngine:
    """搜索引擎"""

    def __init__(self):
        pass

    def parse_qa_pairs(self) -> List[Dict[str, Any]]:
        """解析QA对"""
        try:
            from docx import Document
            doc = Document("C:\\\\Users\\\\jj\\\\Desktop\\\\RAG\\\\QA.docx")
            qa_pairs = []

            for i in range(len(doc.paragraphs) - 1):
                para1 = doc.paragraphs[i].text.strip()
                para2 = doc.paragraphs[i + 1].text.strip()

                if para1 and ('？' in para1 or '?' in para1) and len(para1) > 5:
                    if para2 and len(para2) > 5:
                        qa = {
                            'id': len(qa_pairs) + 1,
                            'question': para1,
                            'answer': para2,
                            'index': i + 1
                        }
                        qa_pairs.append(qa)

            return qa_pairs
        except Exception as e:
            print(f"解析失败: {e}")
            return []

    def search_with_fuzzy(self, query: str, qa_pairs: List[Dict[str, Any]], max_answers: int = MAX_ANSWERS) -> List[Dict[str, Any]]:
        """模糊搜索"""
        query_lower = query.lower()
        results = []

        # 同义词词典
        synonyms = {
            '重置密码': ['重置密码', '重置口令', '找回密码', '修改密码'],
            '邮箱': ['邮箱', '电子邮箱', 'email', '邮件'],
            '收不到': ['收不到', '未收到', '没有收到', '没收到'],
            '登录': ['登录', '登入', 'signin', 'log in'],
            '报销': ['报销', '报销流程', '报销申请', '报销系统']
        }

        # 扩展查询词
        expanded_terms = set()
        for term, synonyms_list in synonyms.items():
            if term in query_lower:
                expanded_terms.update(synonyms_list)

        if not expanded_terms:
            expanded_terms.add(query_lower)

        # 计算相似度
        for qa in qa_pairs:
            score = 0
            q_text = qa['question'].lower()
            a_text = qa['answer'].lower()

            for term in expanded_terms:
                if term in q_text:
                    score += 1.0
                elif term in a_text:
                    score += 0.7
                else:
                    words = term.split()
                    match_count = sum(1 for word in words if word in q_text or word in a_text)
                    if match_count > 0:
                        score += match_count / len(words) * 0.5

            if score > 0:
                results.append({
                    'id': qa['id'],
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'similarity': score / len(expanded_terms),
                    'index': qa.get('index', 0)
                })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_answers]

    def highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """高亮关键词"""
        if not keywords:
            return text

        for keyword in keywords:
            if keyword:
                text = re.sub(
                    re.escape(keyword),
                    f'<mark style="background: linear-gradient(120deg, #f6d365 0%, #fda085 100%); color: white; padding: 2px 6px; border-radius: 4px; font-weight: 500;">{keyword}</mark>',
                    text,
                    flags=re.IGNORECASE
                )
        return text

    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'[\\u4e00-\\u9fff]+|[a-zA-Z]+', text)
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        keywords = []
        for word in words:
            if len(word) >= 2 and word not in stopwords and word not in keywords:
                keywords.append(word)
        return keywords[:5]

# 全局搜索引擎实例
search_engine = SearchEngine()

def load_knowledge_base():
    """加载知识库"""
    global qa_pairs, initialized
    if not initialized:
        qa_pairs = search_engine.parse_qa_pairs()
        initialized = True
        print(f"知识库加载成功，共 {len(qa_pairs)} 个问答对")

# API路由
@app.route('/')
def index():
    """主页"""
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美纳里尼合规报销智能助手</title>
    <style>
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .header h1 {
            color: var(--primary);
            font-size: 2.2rem;
            margin-bottom: 5px;
        }

        .header p {
            color: #6c757d;
            font-size: 1rem;
        }

        .chat-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            min-height: 500px;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding-right: 10px;
        }

        .messages::-webkit-scrollbar {
            width: 6px;
        }

        .messages::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }

        .messages::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 3px;
        }

        .message {
            padding: 15px;
            border-radius: 10px;
            max-width: 80%;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            background: var(--primary);
            color: white;
            margin-left: auto;
        }

        .message.assistant {
            background: #f8f9fa;
            color: #333;
            border-left: 3px solid var(--primary);
        }

        .input-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .input-group {
            display: flex;
            gap: 10px;
        }

        .form-control {
            flex: 1;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            padding: 12px 20px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
        }

        .btn-primary {
            border-radius: 25px;
            padding: 12px 30px;
            background: var(--primary);
            color: white;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }

        .quick-question {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 0.9rem;
            color: #495057;
            cursor: pointer;
            transition: all 0.3s;
        }

        .quick-question:hover {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        .answers-section {
            margin: 10px 0;
        }

        .answers-section h4 {
            color: var(--primary);
            margin-bottom: 10px;
            font-size: 1.1rem;
        }

        .answer-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 3px solid;
        }

        .answer-card.high {
            border-left-color: #28a745;
        }

        .answer-card.medium {
            border-left-color: #ffc107;
        }

        .answer-title {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .similarity-badge {
            background: var(--primary);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }

        .similarity-badge.high {
            background: #28a745;
        }

        .similarity-badge.medium {
            background: #ffc107;
            color: #212529;
        }

        .status {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .status.online {
            color: #28a745;
        }

        .config-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--primary);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: all 0.3s;
        }

        .config-btn:hover {
            transform: scale(1.1);
        }

        .config-panel {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            z-index: 1000;
            min-width: 350px;
        }

        .config-panel h4 {
            margin-bottom: 20px;
            color: var(--primary);
        }

        .config-panel .mb-3 {
            margin-bottom: 15px;
        }

        .config-panel label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }

        .config-panel input[type="number"],
        .config-panel input[type="range"] {
            width: 100%;
        }

        .config-panel .btn {
            width: 100%;
            border-radius: 25px;
        }
    </style>
</head>
<body>
    <div class="status" id="status">检测中...</div>

    <div class="container">
        <div class="header">
            <h1>美纳里尼合规报销智能助手</h1>
            <p>输入问题，智能解答合规和报销相关问题</p>
        </div>

        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message assistant">
                    <strong>欢迎使用！</strong><br><br>
                    我可以帮您解答合规和报销相关问题。请输入您的问题，比如：
                    <br>• 为什么重置密码的邮件一直收不到？
                    <br>• 报销流程是什么？
                    <br>• 如何登录系统？
                    <br><br>
                    <div class="quick-questions">
                        <button class="quick-question" onclick="askQuestion('为什么重置密码的邮件一直收不到?')">为什么重置密码的邮件一直收不到?</button>
                        <button class="quick-question" onclick="askQuestion('报销流程是什么?')">报销流程是什么?</button>
                        <button class="quick-question" onclick="askQuestion('如何登录系统?')">如何登录系统?</button>
                    </div>
                </div>
            </div>

            <div class="input-container">
                <form id="chatForm" class="input-group">
                    <input type="text" class="form-control" id="userInput" placeholder="请输入您的问题..." required>
                    <button type="submit" class="btn btn-primary" id="sendBtn">发送</button>
                </form>
            </div>
        </div>
    </div>

    <button class="config-btn" onclick="toggleConfig()">
        <i>⚙️</i>
    </button>

    <script>
        let isTyping = false;
        let config = { maxAnswers: 2, similarityThreshold: 0.4 };

        // 检查状态
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('status').textContent = `在线 (${data.qa_pairs_count}个问答)`;
                document.getElementById('status').classList.add('online');
            } catch (error) {
                document.getElementById('status').textContent = '离线';
                document.getElementById('status').classList.remove('online');
            }
        }

        checkStatus();
        setInterval(checkStatus, 5000);

        // 添加消息
        function addMessage(content, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = content;
            document.getElementById('messages').appendChild(messageDiv);
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }

        // 显示输入中
        function showTyping() {
            if (isTyping) return;
            isTyping = true;
            addMessage('<div style="display: flex; align-items: center; gap: 10px;">
                <span style="height: 8px; width: 8px; background: #667eea; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite;"></span>
                <span style="height: 8px; width: 8px; background: #667eea; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite 0.2s;"></span>
                <span style="height: 8px; width: 8px; background: #667eea; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite 0.4s;"></span>
                <small style="color: #6c757d;">正在搜索...</small>
            </div>', 'assistant');
        }

        // 隐藏输入中
        function hideTyping() {
            isTyping = false;
        }

        // 发送问题
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message || isTyping) return;

            addMessage(message, 'user');
            input.value = '';
            document.getElementById('sendBtn').disabled = true;

            showTyping();

            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question, maxAnswers: config.maxAnswers, similarityThreshold: config.similarityThreshold })
                });

                const data = await response.json();
                hideTyping();

                if (data.success) {
                    let answerHtml = '';

                    if (data.high_similarity && data.high_similarity.length > 0) {
                        answerHtml += '<div class="answers-section"><h4>🎯 精准匹配</h4>';
                        data.high_similarity.forEach(answer => {
                            answerHtml += `<div class="answer-card high">
                                <div class="answer-title">
                                    <span>答案 ${answer.id}</span>
                                    <span class="similarity-badge high">${Math.round(answer.similarity * 100)}%</span>
                                </div>
                                <div>${answer.answer}</div>
                            </div>`;
                        });
                        answerHtml += '</div>';
                    }

                    if (data.low_similarity && data.low_similarity.length > 0) {
                        answerHtml += '<div class="answers-section"><h4>🔍 相关参考</h4>';
                        data.low_similarity.forEach(answer => {
                            answerHtml += `<div class="answer-card medium">
                                <div class="answer-title">
                                    <span>参考 ${answer.id}</span>
                                    <span class="similarity-badge medium">${Math.round(answer.similarity * 100)}%</span>
                                </div>
                                <div>${answer.answer}</div>
                            </div>`;
                        });
                        answerHtml += '</div>';
                    }

                    addMessage(answerHtml, 'assistant');
                } else {
                    addMessage(data.message, 'assistant');
                }
            } catch (error) {
                hideTyping();
                addMessage('抱歉，服务暂时不可用。请稍后重试。', 'assistant');
            } finally {
                document.getElementById('sendBtn').disabled = false;
                input.focus();
            }
        }

        // 快速提问
        function askQuestion(question) {
            document.getElementById('userInput').value = question;
            sendMessage();
        }

        // 切换配置面板
        function toggleConfig() {
            const panel = document.getElementById('configPanel');
            if (panel.style.display === 'none' || !panel) {
                showConfigPanel();
            } else {
                panel.remove();
            }
        }

        // 显示配置面板
        function showConfigPanel() {
            const panel = document.createElement('div');
            panel.id = 'configPanel';
            panel.className = 'config-panel';
            panel.innerHTML = `
                <h4>系统配置</h4>
                <div class="mb-3">
                    <label>最大显示答案数</label>
                    <input type="number" id="maxAnswersInput" min="1" max="10" value="${config.maxAnswers}">
                </div>
                <div class="mb-3">
                    <label>相似度阈值 (${Math.round(config.similarityThreshold * 100)}%)</label>
                    <input type="range" id="similarityInput" min="0" max="100" value="${Math.round(config.similarityThreshold * 100)}">
                </div>
                <button class="btn btn-primary" onclick="saveConfig()">保存配置</button>
                <button class="btn btn-secondary" onclick="toggleConfig()" style="margin-top: 10px;">取消</button>
            `;
            document.body.appendChild(panel);
        }

        // 保存配置
        async function saveConfig() {
            config.maxAnswers = parseInt(document.getElementById('maxAnswersInput').value);
            config.similarityThreshold = parseInt(document.getElementById('similarityInput').value) / 100;

            try {
                await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });
                alert('配置保存成功！');
                toggleConfig();
            } catch (error) {
                alert('配置保存失败！');
            }
        }

        // 表单提交
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage();
        });

        // 初始化
        document.getElementById('userInput').focus();
    </script>
</body>
</html>'''

    return html

@app.route('/api/ask', methods=['POST'])
def ask():
    """问答API"""
    try:
        data = request.json
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'error': '请输入问题'}), 400

        # 获取配置
        config_max_answers = data.get('maxAnswers', MAX_ANSWERS)
        config_threshold = data.get('similarityThreshold', SIMILARITY_THRESHOLD)

        # 加载知识库
        if not initialized:
            load_knowledge_base()

        if not initialized:
            return jsonify({'error': '知识库未加载'}), 500

        # 搜索答案
        results = search_engine.search_with_fuzzy(question, qa_pairs, max_answers=config_max_answers)

        if results:
            # 提取关键词
            keywords = search_engine.extract_keywords(question)

            # 按相似度分组
            high_similarity = [r for r in results if r['similarity'] >= config_threshold]
            low_similarity = [r for r in results if r['similarity'] < config_threshold and r['similarity'] > 0]

            # 构建回答
            response_data = {
                'success': True,
                'high_similarity': [],
                'low_similarity': [],
                'keywords': keywords
            }

            for result in high_similarity:
                answer = search_engine.highlight_keywords(result['answer'], keywords)
                response_data['high_similarity'].append({
                    'id': result['id'],
                    'answer': answer,
                    'similarity': result['similarity']
                })

            for result in low_similarity:
                answer = search_engine.highlight_keywords(result['answer'], keywords)
                response_data['low_similarity'].append({
                    'id': result['id'],
                    'answer': answer,
                    'similarity': result['similarity']
                })

            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'message': '''很抱歉，我在知识库中没有找到相关答案。

📝 建议：
1. 请检查问题表述是否清晰
2. 尝试使用不同的关键词描述您的问题
3. 如果仍需帮助，请联系IT支持团队'''
            })

    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """配置API"""
    global MAX_ANSWERS, SIMILARITY_THRESHOLD
    if request.method == 'GET':
        return jsonify({
            'maxAnswers': MAX_ANSWERS,
            'similarityThreshold': SIMILARITY_THRESHOLD
        })
    else:
        try:
            data = request.json
            if 'maxAnswers' in data:
                MAX_ANSWERS = int(data['maxAnswers'])
            if 'similarityThreshold' in data:
                SIMILARITY_THRESHOLD = float(data['similarityThreshold'])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/api/status')
def status():
    """状态API"""
    load_knowledge_base()
    return jsonify({
        'status': 'ok',
        'initialized': initialized,
        'qa_pairs_count': len(qa_pairs),
        'timestamp': datetime.now().isoformat()
    })

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='美纳里尼合规报销智能助手')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='端口号 (默认: 5000)')

    args = parser.parse_args()

    print("Starting web application...")
    print("Local access: http://localhost:%d" % args.port)
    print("External access: http://%s:%d" % (args.host, args.port))
    print("Knowledge base Q&A pairs: %d" % len(qa_pairs))
    print("Press Ctrl+C to stop server")

    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()