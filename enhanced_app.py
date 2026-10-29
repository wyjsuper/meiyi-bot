import streamlit as st
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

    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

# 初始化
init_session_state()

# 优化的搜索类
class EnhancedSearch:
    """增强的搜索类"""

    def __init__(self):
        pass

    def parse_word_enhanced(self, file_path: str) -> List[Dict[str, Any]]:
        """增强的Word文档解析"""
        try:
            from docx import Document
            doc = Document(file_path)
            qa_pairs = []

            # 从段落提取QA对
            for i in range(len(doc.paragraphs) - 1):
                para1 = doc.paragraphs[i]
                para2 = doc.paragraphs[i + 1]

                text1 = para1.text.strip()
                text2 = para2.text.strip()

                # 检查第一个段落是否是问题
                if text1 and ('？' in text1 or '?' in text1) and len(text1) > 5:
                    # 第二个段落作为答案
                    if text2 and len(text2) > 5:
                        qa_pairs.append({
                            'id': len(qa_pairs) + 1,
                            'question': text1,
                            'answer': text2,
                            'source': os.path.basename(file_path),
                            'index': i + 1
                        })

            return qa_pairs
        except Exception as e:
            print(f"解析失败: {e}")
            return []

    def search_multiple_answers(self, query: str, qa_pairs: List[Dict[str, Any]], max_answers: int = 5) -> List[Dict[str, Any]]:
        """搜索并返回多个相关答案"""
        query_lower = query.lower()
        results = []

        for qa in qa_pairs:
            score = 0
            q_text = qa['question'].lower()
            a_text = qa['answer'].lower()

            # 1. 完全匹配问题 (最高分)
            if query_lower == q_text:
                score = 1.0
            # 2. 问题关键词匹配
            elif any(word in q_text for word in query_lower.split()):
                score = sum(1 for word in query_lower.split() if word in q_text) / len(query_lower.split())
            # 3. 查询词包含在问题中
            elif query_lower in q_text:
                score = 0.8
            # 4. 答案包含查询词
            elif query_lower in a_text:
                score = 0.5
            # 5. 部分匹配
            else:
                # 计算共同词汇
                query_words = set(query_lower.split())
                q_words = set(q_text.split())
                a_words = set(a_text.split())

                # 问题中的共同词
                q_overlap = len(query_words & q_words)
                # 答案中的共同词
                a_overlap = len(query_words & a_words)

                if q_overlap > 0 or a_overlap > 0:
                    score = (q_overlap + a_overlap * 0.5) / len(query_words)

            if score > 0:
                results.append({
                    'id': qa['id'],
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'source': qa['source'],
                    'similarity': score,
                    'index': qa.get('index', 0)
                })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_answers]

# 关键词高亮器
class SimpleHighlighter:
    """简单的关键词高亮器"""

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
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        keywords = []
        for word in words:
            if len(word) >= 2 and word not in stopwords and word not in keywords:
                keywords.append(word)
        return keywords[:5]

# 自动加载知识库
def load_knowledge_base():
    """自动加载知识库"""
    if not st.session_state.initialized:
        try:
            # 尝试解析RAG目录
            rag_dir = r'C:\Users\jj\Desktop\RAG'
            search_engine = EnhancedSearch()

            for file in os.listdir(rag_dir):
                if file == 'QA.docx':
                    file_path = os.path.join(rag_dir, file)
                    st.session_state.qa_pairs = search_engine.parse_word_enhanced(file_path)
                    st.session_state.initialized = True
                    st.session_state.last_update = time.time()
                    print(f"从QA.docx加载了 {len(st.session_state.qa_pairs)} 个问答对")
                    break
        except Exception as e:
            print(f"加载知识库失败: {e}")

# 页面标题
st.title("🤖 美易在线答疑")
st.markdown("""
美纳里尼中国合规智能助手

**功能：**
- 📚 智能问答：基于知识库自动回答合规和报销相关问题
- 🔍 多答案显示：显示所有相关的答案而不只是最相似的
- 📝 人工兜底：知识库无答案时转人工客服
- 📊 知识库管理：自动加载和更新知识库
""")

# 加载知识库
load_knowledge_base()

# 侧边栏
with st.sidebar:
    st.header("📚 知识库管理")

    # 显示知识库状态
    doc_count = len(st.session_state.qa_pairs)
    st.subheader("知识库状态")
    st.metric("文档总数", doc_count)

    # 知识库来源配置
    st.subheader("知识库来源")
    rag_dir = st.text_input(
        "知识库目录",
        value="C:\\Users\\jj\\Desktop\\RAG",
        help="包含Excel和Word知识库文件的目录"
    )

    # 更新知识库按钮
    if st.button("更新知识库", type="primary"):
        with st.spinner("正在更新知识库..."):
            try:
                parser = EnhancedSearch()
                qa_pairs = []

                # 解析Word文档
                for file in os.listdir(rag_dir):
                    if file == 'QA.docx':
                        file_path = os.path.join(rag_dir, file)
                        qa_pairs = parser.parse_word_enhanced(file_path)
                        break

                if qa_pairs:
                    st.session_state.qa_pairs = qa_pairs
                    st.session_state.initialized = True
                    st.session_state.last_update = time.time()

                    st.success(f"成功更新知识库！共添加 {len(qa_pairs)} 个问答对")
                else:
                    st.warning("未找到任何有效的问答对")

            except Exception as e:
                st.error(f"更新知识库失败: {e}")

    # 显示上次更新时间
    if st.session_state.last_update:
        st.caption(f"上次更新: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.last_update))}")

    st.divider()

    # 系统设置
    st.subheader("系统设置")
    threshold = st.slider("相似度阈值", 0.0, 0.9, 0.1, 0.1)  # 降低默认阈值
    max_answers = st.slider("最大显示答案数", 1, 10, 5, 1)

    st.divider()

    # 系统信息
    st.caption("系统信息")
    st.text(f"问答对数量: {doc_count}")

# 主聊天界面
st.header("💬 智能问答")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的合规或报销相关问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示处理中状态
    with st.chat_message("assistant"):
        with st.spinner("正在搜索知识库并生成回答..."):
            try:
                # 检查是否已初始化
                if not st.session_state.initialized:
                    st.warning("⚠️ 请先更新知识库")
                    answer = "系统尚未初始化，请先在侧边栏更新知识库。"
                else:
                    # 使用增强搜索
                    search_engine = EnhancedSearch()
                    highlighter = SimpleHighlighter()

                    # 搜索相关文档
                    results = search_engine.search_multiple_answers(prompt, st.session_state.qa_pairs, max_answers)

                    if results:
                        # 提取关键词
                        keywords = highlighter.extract_keywords(prompt)

                        # 构建回答 - 显示所有相关答案
                        answer_parts = []

                        # 按相似度分组显示
                        high_similarity = [r for r in results if r['similarity'] >= threshold]
                        low_similarity = [r for r in results if r['similarity'] < threshold and r['similarity'] > 0]

                        if high_similarity:
                            answer_parts.append("### 🎯 高相关答案")
                            for i, result in enumerate(high_similarity, 1):
                                answer_parts.append(f"**答案{i}**（相似度: {result['similarity']:.2%}）：\n{result['answer']}")

                        if low_similarity and len(results) > len(high_similarity):
                            answer_parts.append("\n### 🔍 相关参考答案")
                            for i, result in enumerate(low_similarity[:3], 1):
                                answer_parts.append(f"**参考{i}**（相似度: {result['similarity']:.2%}）：\n{result['answer']}")

                        answer = "\n\n".join(answer_parts)

                        # 高亮关键词
                        answer = highlighter.highlight_keywords(answer, keywords)

                        # 添加提示
                        if len(results) > max_answers:
                            answer += f"\n\n💡 共找到 {len(results)} 个相关答案，仅显示前 {max_answers} 个。"
                    else:
                        answer = """很抱歉，我在知识库中没有找到与您问题相关的信息。

📝 建议：
1. 请检查问题表述是否清晰
2. 尝试使用不同的关键词描述您的问题
3. 如果仍需帮助，请联系人工客服

📞 客服联系方式：请通过公司内部通讯系统联系IT支持团队"""

                # 显示回答
                st.markdown(answer)

                # 如果没有初始化，提示用户上传知识库
                if not st.session_state.initialized:
                    st.warning("⚠️ 请先上传知识库文件")

                # 保存AI回答到历史
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"处理过程中发生错误: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 页脚
st.divider()
st.caption("""
🤖 美易在线答疑 - 基于增强搜索的智能问答系统
美纳里尼中国合规报销系统 | 2024
""")