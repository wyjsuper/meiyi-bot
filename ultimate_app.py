import streamlit as st
import os
import json
import re
from typing import List, Dict, Any, Tuple
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

    if 'categories' not in st.session_state:
        st.session_state.categories = {}

    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = {}

    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

# 初始化
init_session_state()

# 高级搜索类
class UltimateSearch:
    """终极搜索功能"""

    def __init__(self):
        pass

    def parse_word_with_categories(self, file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """解析Word文档并分类"""
        try:
            from docx import Document
            doc = Document(file_path)
            qa_pairs = []
            categories = {
                '密码相关': [],
                '报销相关': [],
                '登录相关': [],
                '系统问题': [],
                '其他': []
            }

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
                        qa = {
                            'id': len(qa_pairs) + 1,
                            'question': text1,
                            'answer': text2,
                            'source': os.path.basename(file_path),
                            'index': i + 1
                        }
                        qa_pairs.append(qa)

                        # 分类
                        if any(keyword in text1.lower() or keyword in text2.lower()
                               for keyword in ['密码', '重置', '邮箱']):
                            categories['密码相关'].append(qa)
                        elif any(keyword in text1.lower() or keyword in text2.lower()
                                for keyword in ['报销', '发票', '财务', '申请']):
                            categories['报销相关'].append(qa)
                        elif any(keyword in text1.lower() or keyword in text2.lower()
                                for keyword in ['登录', '账号', '账户']):
                            categories['登录相关'].append(qa)
                        elif any(keyword in text1.lower() or keyword in text2.lower()
                                for keyword in ['系统', '平台', '网站']):
                            categories['系统问题'].append(qa)
                        else:
                            categories['其他'].append(qa)

            return qa_pairs, categories
        except Exception as e:
            print(f"解析失败: {e}")
            return [], {}

    def search_with_fuzzy(self, query: str, qa_pairs: List[Dict[str, Any]],
                         max_answers: int = 10) -> List[Dict[str, Any]]:
        """模糊搜索，支持同义词扩展"""
        query_lower = query.lower()
        results = []

        # 定义同义词词典
        synonyms = {
            '重置密码': ['重置密码', '重置口令', '找回密码', '修改密码'],
            '邮箱': ['邮箱', '电子邮箱', 'email', '邮件'],
            '收不到': ['收不到', '未收到', '没有收到', '没收到'],
            '登录': ['登录', '登入', ' signin', 'log in'],
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
                    'source': qa['source'],
                    'similarity': score / len(expanded_terms),
                    'index': qa.get('index', 0)
                })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_answers]

    def get_suggested_questions(self, keywords: List[str], qa_pairs: List[Dict[str, Any]],
                               max_suggestions: int = 5) -> List[str]:
        """根据关键词获取建议问题"""
        suggestions = set()

        for qa in qa_pairs:
            for keyword in keywords:
                if keyword.lower() in qa['question'].lower():
                    suggestions.add(qa['question'])
                    if len(suggestions) >= max_suggestions:
                        return list(suggestions)

        return list(suggestions)

    def search_by_category(self, category: str, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按类别搜索"""
        if category == '全部':
            return qa_pairs
        elif category in st.session_state.categories:
            return st.session_state.categories[category]
        return []

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
            # 尝试从文件加载
            if os.path.exists("enhanced_knowledge_base.json"):
                with open("enhanced_knowledge_base.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    st.session_state.qa_pairs = data['qa_pairs']
                    st.session_state.categories = data['categories']
                    st.session_state.suggestions = data['suggestions']
                    st.session_state.initialized = True
                    st.session_state.last_update = time.time()
                    print(f"从文件加载了 {len(st.session_state.qa_pairs)} 个问答对")
                    return

            # 尝试解析RAG目录
            rag_dir = r'C:\Users\jj\Desktop\RAG'
            search_engine = UltimateSearch()

            for file in os.listdir(rag_dir):
                if file == 'QA.docx':
                    file_path = os.path.join(rag_dir, file)
                    qa_pairs, categories = search_engine.parse_word_with_categories(file_path)

                    # 生成建议问题
                    common_questions = {
                        '密码相关': ['重置密码', '登录问题', '邮箱验证'],
                        '报销相关': ['报销流程', '发票要求', '报销周期'],
                        '登录相关': ['无法登录', '账号问题', '密码错误'],
                        '系统问题': ['系统使用', '平台功能', '网站问题']
                    }

                    suggestions = {}
                    for category, keywords in common_questions.items():
                        suggestions[category] = search_engine.get_suggested_questions(
                            keywords, qa_pairs, max_suggestions=3
                        )

                    # 保存数据
                    st.session_state.qa_pairs = qa_pairs
                    st.session_state.categories = categories
                    st.session_state.suggestions = suggestions
                    st.session_state.initialized = True
                    st.session_state.last_update = time.time()

                    # 保存到文件
                    data = {
                        'qa_pairs': qa_pairs,
                        'categories': categories,
                        'suggestions': suggestions,
                        'last_updated': time.time()
                    }
                    with open("enhanced_knowledge_base.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    print(f"从QA.docx加载了 {len(qa_pairs)} 个问答对")
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
- 📂 分类浏览：按类别查看常见问题
- 💡 智能推荐：根据关键词推荐相关问题
- 📝 人工兜底：知识库无答案时转人工客服
- 📊 知识库管理：自动加载和更新知识库
""")

# 加载知识库
load_knowledge_base()

# 选项卡布局
tab1, tab2, tab3 = st.tabs(["💬 智能问答", "📂 分类浏览", "📊 统计信息"])

# 选项卡1：智能问答
with tab1:
    # 侧边栏设置
    with st.sidebar:
        st.header("🔍 搜索设置")
        threshold = st.slider("相似度阈值", 0.0, 0.9, 0.1, 0.1)
        max_answers = st.slider("最大显示答案数", 1, 10, 5, 1)

        st.divider()
        st.header("💡 快捷问题")
        if st.session_state.initialized and st.session_state.suggestions:
            for category, questions in st.session_state.suggestions.items():
                if questions:
                    with st.expander(category):
                        for q in questions:
                            if st.button(q, key=f"q_{q}"):
                                # 模拟点击问题
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
                        search_engine = UltimateSearch()
                        highlighter = SimpleHighlighter()

                        # 搜索相关文档
                        results = search_engine.search_with_fuzzy(prompt, st.session_state.qa_pairs, max_answers)

                        if results:
                            # 提取关键词
                            keywords = highlighter.extract_keywords(prompt)

                            # 构建回答
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

                    # 保存AI回答到历史
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    error_msg = f"处理过程中发生错误: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 选项卡2：分类浏览
with tab2:
    st.header("📂 分类浏览")

    if not st.session_state.initialized:
        st.warning("⚠️ 请先在智能问答页面加载知识库")
    else:
        # 分类选择
        categories = list(st.session_state.categories.keys())
        categories.insert(0, '全部')
        selected_category = st.selectbox("选择分类", categories)

        # 显示分类下的问答
        if selected_category == '全部':
            qa_list = st.session_state.qa_pairs
        else:
            qa_list = st.session_state.categories[selected_category]

        st.write(f"共找到 {len(qa_list)} 个问答")

        # 显示问答列表
        for qa in qa_list[:50]:  # 限制显示数量
            with st.expander(f"Q: {qa['question'][:50]}..."):
                st.write(f"**问题:** {qa['question']}")
                st.write(f"**答案:** {qa['answer']}")

                # 快速提问按钮
                if st.button("快速提问", key=f"ask_{qa['id']}"):
                    st.session_state.messages.append({"role": "user", "content": qa['question']})
                    st.experimental_rerun()

# 选项卡3：统计信息
with tab3:
    st.header("📊 统计信息")

    if not st.session_state.initialized:
        st.warning("⚠️ 请先在智能问答页面加载知识库")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("知识库统计")
            st.metric("总问答对", len(st.session_state.qa_pairs))

            # 分类统计
            st.write("分类统计:")
            for category, qas in st.session_state.categories.items():
                st.write(f"- {category}: {len(qas)} 个")

        with col2:
            st.subheader("搜索统计")

            # 显示热门搜索词（模拟）
            search_history = []
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    search_history.append(msg['content'])

            if search_history:
                from collections import Counter
                word_counts = Counter()
                for text in search_history:
                    words = re.findall(r'[\u4e00-\u9fff]+', text)
                    for word in words:
                        if len(word) >= 2:
                            word_counts[word] += 1

                st.write("热门搜索词:")
                for word, count in word_counts.most_common(5):
                    st.write(f"- {word}: {count} 次")

            # 历史消息统计
            user_msgs = len([m for m in st.session_state.messages if m['role'] == 'user'])
            ai_msgs = len([m for m in st.session_state.messages if m['role'] == 'assistant'])
            st.metric("用户提问数", user_msgs)
            st.metric("系统回答数", ai_msgs)

# 页脚
st.divider()
st.caption("""
🤖 美易在线答疑 - 终极版智能问答系统
美纳里尼中国合规报销系统 | 2024
""")