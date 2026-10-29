
// 聊天应用主逻辑
class ChatApp {
    constructor() {
        this.messagesContainer = document.getElementById('messages');
        this.chatForm = document.getElementById('chatForm');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.statusBadge = document.getElementById('statusBadge');
        this.isTyping = false;

        this.init();
    }

    init() {
        // 检查连接状态
        this.checkStatus();
        setInterval(() => this.checkStatus(), 5000);

        // 绑定事件
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 快捷问题点击
        document.querySelectorAll('.quick-question').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.textContent;
                this.userInput.value = question;
                this.sendMessage();
            });
        });

        // 页面加载完成后聚焦输入框
        document.addEventListener('DOMContentLoaded', () => {
            this.userInput.focus();
        });
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            if (data.status === 'ok') {
                this.statusBadge.innerHTML = `
                    <span class="status-dot"></span>
                    <span>在线 (${data.qa_pairs_count}个问答)</span>
                `;
                this.statusBadge.classList.add('online');
                this.statusBadge.classList.remove('offline');
            }
        } catch (error) {
            this.statusBadge.innerHTML = `
                <span class="status-dot"></span>
                <span>离线</span>
            `;
            this.statusBadge.classList.add('offline');
            this.statusBadge.classList.remove('online');
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">${content}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-header">
                    <span>🤖 合规助手</span>
                    <span>${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message-content"></div>
            `;
            messageDiv.querySelector('.message-content').innerHTML = content;
        }

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // 添加动画效果
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.style.opacity = '1';
        }, 100);
    }

    showTyping() {
        if (this.isTyping) return;
        this.isTyping = true;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typingMessage';
        typingDiv.innerHTML = `
            <div class="message-header">
                <span>🤖 合规助手</span>
                <span>${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
                <small style="margin-left: 10px; color: #6c757d;">正在搜索知识库...</small>
            </div>
        `;

        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTyping() {
        const typingMessage = document.getElementById('typingMessage');
        if (typingMessage) {
            typingMessage.remove();
        }
        this.isTyping = false;
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isTyping) return;

        // 添加用户消息
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.sendBtn.disabled = true;

        // 显示输入状态
        this.showTyping();

        try {
            // 调用API
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message })
            });

            const data = await response.json();

            // 移除输入状态
            this.removeTyping();

            // 添加回答
            if (data.success) {
                this.displayAnswers(data);
            } else {
                this.addMessage(data.message, 'assistant');
            }

        } catch (error) {
            this.removeTyping();
            this.addMessage('抱歉，服务暂时不可用。请稍后重试。', 'assistant');
        } finally {
            this.sendBtn.disabled = false;
            this.userInput.focus();
        }
    }

    displayAnswers(data) {
        const answersHtml = [];

        if (data.high_similarity && data.high_similarity.length > 0) {
            answersHtml.push('<div class="answers-section"><h4>🎯 精准匹配</h4>');

            data.high_similarity.forEach((answer, index) => {
                answersHtml.push(`
                    <div class="answer-card high">
                        <div class="answer-title high">
                            <div class="answer-title-icon">✓</div>
                            <span>答案 ${answer.id}</span>
                            <span class="similarity-badge high">${Math.round(answer.similarity * 100)}%</span>
                        </div>
                        <div>${answer.answer}</div>
                    </div>
                `);
            });

            answersHtml.push('</div>');
        }

        if (data.low_similarity && data.low_similarity.length > 0) {
            answersHtml.push('<div class="answers-section"><h4>🔍 相关参考</h4>');

            data.low_similarity.forEach((answer, index) => {
                answersHtml.push(`
                    <div class="answer-card medium">
                        <div class="answer-title medium">
                            <div class="answer-title-icon">💡</div>
                            <span>参考 ${answer.id}</span>
                            <span class="similarity-badge medium">${Math.round(answer.similarity * 100)}%</span>
                        </div>
                        <div>${answer.answer}</div>
                    </div>
                `);
            });

            answersHtml.push('</div>');
        }

        const finalHtml = answersHtml.join('');
        this.addMessage(finalHtml, 'assistant');

        // 如果有关键词，显示提示
        if (data.keywords && data.keywords.length > 0) {
            setTimeout(() => {
                const keywordsHtml = `
                    <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 10px;">
                        <small style="color: #6c757d;">
                            🔍 关键词：${data.keywords.join('、')}
                        </small>
                    </div>
                `;
                const lastMessage = this.messagesContainer.lastElementChild;
                if (lastMessage && lastMessage.classList.contains('assistant')) {
                    lastMessage.querySelector('.message-content').insertAdjacentHTML('beforeend', keywordsHtml);
                }
            }, 500);
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
