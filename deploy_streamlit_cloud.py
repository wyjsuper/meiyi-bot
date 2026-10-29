#!/usr/bin/env python3
"""
美易机器人部署到Streamlit Cloud指南
"""

import os
import json

def create_streamlit_cloud_config():
    """创建Streamlit Cloud配置文件"""

    # 创建.streamlit目录
    os.makedirs('.streamlit', exist_ok=True)

    # 创建config.toml
    config_content = """
[server]
headless = true
port = 8501
address = "0.0.0.0"
enableCORS = true
maxMessageSize = 200
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = 8501
"""

    with open('.streamlit/config.toml', 'w', encoding='utf-8') as f:
        f.write(config_content)

    print("Streamlit Cloud config file created successfully")

def create_requirements():
    """创建requirements.txt"""
    requirements_content = """streamlit>=1.28.0
python-docx>=0.8.11
requests>=2.28.0
"""

    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)

    print("requirements.txt created successfully")

def create_app_py():
    """创建简化版应用，适合部署"""

    app_content = '''import streamlit as st
import os
import json
import re
from typing import List, Dict, Any
import time

# 设置环境变量禁用邮件收集
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# 页面配置
st.set_page_config(
    page_title="美易在线答疑 - 合规报销系统",
    page_icon="🤖",
    layout="wide"
)

# 初始化会话状态
def init_session_state():
    """初始化所有会话状态变量"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'qa_pairs' not in st.session_state:
        st.session_state.qa_pairs = []

    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

# 初始化
init_session_state()

# 高级搜索类
class SimpleSearchEngine:
    """简化的搜索引擎"""

    def __init__(self):
        pass

    def parse_qa_pairs(self) -> List[Dict[str, Any]]:
        """解析QA对"""
        try:
            from docx import Document
            doc = Document("C:\\\\Users\\\\jj\\\\Desktop\\\\RAG\\\\QA.docx")
            qa_pairs = []

            for i in range(len(doc.paragraphs) - 1):
                para1 = doc.paragraphs[i]
                para2 = doc.paragraphs[i + 1]

                text1 = para1.text.strip()
                text2 = para2.text.strip()

                if text1 and ('？' in text1 or '?' in text1) and len(text1) > 5:
                    if text2 and len(text2) > 5:
                        qa = {
                            'id': len(qa_pairs) + 1,
                            'question': text1,
                            'answer': text2,
                            'index': i + 1
                        }
                        qa_pairs.append(qa)

            return qa_pairs
        except Exception as e:
            print(f"解析失败: {e}")
            return []

    def search_with_fuzzy(self, query: str, qa_pairs: List[Dict[str, Any]], max_answers: int = 5) -> List[Dict[str, Any]]:
        """模糊搜索"""
        query_lower = query.lower()
        results = []

        # 定义同义词词典
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

        # 如果没有找到同义词，使用原查询
        if not expanded_terms:
            expanded_terms.add(query_lower)

        for qa in qa_pairs:
            score = 0
            q_text = qa['question'].lower()
            a_text = qa['answer'].lower()

            # 计算每个扩展词的匹配度
            for term in expanded_terms:
                if term in q_text:
                    score += 1.0
                elif term in a_text:
                    score += 0.7
                else:
                    # 部分匹配
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
                    f'<mark style="background-color: #ffff00; padding: 2px 4px; border-radius: 3px;">{keyword}</mark>',
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

# 加载知识库
def load_knowledge_base():
    """自动加载知识库"""
    if not st.session_state.initialized:
        try:
            # 尝试解析RAG目录
            search_engine = SimpleSearchEngine()
            qa_pairs = search_engine.parse_qa_pairs()

            if qa_pairs:
                st.session_state.qa_pairs = qa_pairs
                st.session_state.initialized = True
                st.session_state.last_update = time.time()
                print(f"加载了 {len(qa_pairs)} 个问答对")
        except Exception as e:
            print(f"加载知识库失败: {e}")

# 页面标题
st.title("🤖 美易在线答疑")
st.markdown("""
美纳里尼中国合规智能助手

**功能：**
- 📚 智能问答：基于知识库自动回答合规和报销相关问题
- 🔍 多答案显示：显示所有相关的答案而不只是最相似的
- 💡 智能推荐：根据关键词推荐相关问题
- 📝 人工兜底：知识库无答案时转人工客服
- 📊 知识库管理：自动加载和更新知识库
""")

# 加载知识库
load_knowledge_base()

# 侧边栏设置
with st.sidebar:
    st.header("🔍 搜索设置")
    threshold = st.slider("相似度阈值", 0.0, 0.9, 0.2, 0.1)
    max_answers = st.slider("最大显示答案数", 1, 10, 5, 1)

    st.divider()
    st.header("💡 快捷问题")
    if st.session_state.initialized and st.session_state.qa_pairs:
        common_questions = [
            "为什么重置密码的邮件一直收不到?",
            "报销流程是什么?",
            "如何登录系统?",
            "发票要求有哪些?"
        ]

        for q in common_questions:
            if st.button(q, key=f"q_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})

    st.divider()
    # 系统信息
    doc_count = len(st.session_state.qa_pairs)
    st.caption("系统信息")
    st.text(f"问答对数量: {doc_count}")

# 主聊天界面
st.header("💬 智能问答")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示处理中状态
    with st.chat_message("assistant"):
        with st.spinner("正在搜索知识库并生成回答..."):
            try:
                if not st.session_state.initialized:
                    st.warning("⚠️ 请先更新知识库")
                    answer = "系统尚未初始化，请先在侧边栏更新知识库。"
                else:
                    # 使用高级搜索
                    search_engine = SimpleSearchEngine()

                    # 搜索相关文档
                    results = search_engine.search_with_fuzzy(prompt, st.session_state.qa_pairs, max_answers)

                    if results:
                        # 提取关键词
                        keywords = search_engine.extract_keywords(prompt)

                        # 构建回答
                        answer_parts = []

                        # 按相似度分组显示
                        high_similarity = [r for r in results if r['similarity'] >= threshold]
                        low_similarity = [r for r in results if r['similarity'] < threshold and r['similarity'] > 0]

                        if high_similarity:
                            answer_parts.append("### 🎯 高相关答案")
                            for i, result in enumerate(high_similarity, 1):
                                answer_parts.append(f"**答案{i}**（相似度: {result['similarity']:.2%}）：\\n{result['answer']}")

                        if low_similarity and len(results) > len(high_similarity):
                            answer_parts.append("\\n### 🔍 相关参考答案")
                            for i, result in enumerate(low_similarity[:3], 1):
                                answer_parts.append(f"**参考{i}**（相似度: {result['similarity']:.2%}）：\\n{result['answer']}")

                        answer = "\\n\\n".join(answer_parts)

                        # 高亮关键词
                        answer = search_engine.highlight_keywords(answer, keywords)

                        # 添加提示
                        if len(results) > max_answers:
                            answer += f"\\n\\n💡 共找到 {len(results)} 个相关答案，仅显示前 {max_answers} 个。"
                    else:
                        answer = """很抱歉，我在知识库中没有找到与您问题相关的信息。

📝 建议：
1. 请检查问题表述是否清晰
2. 尝试使用不同的关键词描述您的问题
3. 如果仍需帮助，请联系人工客服

📞 客服联系方式：请通过公司内部通讯系统联系IT支持团队"""

                    # 显示回答
                    st.markdown(answer)

                    # 保存AI回答到历史
                    st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"处理过程中发生错误: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 页脚
st.divider()
st.caption("""
🤖 美易在线答疑 - 云端版智能问答系统
美纳里尼中国合规报销系统 | 2024
""")
'''

    with open('app_cloud.py', 'w', encoding='utf-8') as f:
        f.write(app_content)

    print("Cloud app file created successfully")

def main():
    """主函数"""
    print("Creating Streamlit Cloud deployment files...")

    create_streamlit_cloud_config()
    create_requirements()
    create_app_py()

    print("\nDeployment files created successfully!")
    print("\nStreamlit Cloud deployment steps:")
    print("1. Visit https://streamlit.io/cloud")
    print("2. Login or register an account")
    print("3. Click 'New app'")
    print("4. Connect to GitHub repository")
    print("5. Select branch and app_cloud.py")
    print("6. Click 'Deploy!'")
    print("\nAfter deployment, you will get a public URL")

if __name__ == "__main__":
    main()