import streamlit as st
import os
import time
import json
import logging
from datetime import datetime

# 导入自定义模块
from utils.document_parser import DocumentParser
from utils.robust_parser import RobustParser
from utils.vector_store import VectorStore
from utils.llm_client import LLMClient
from utils.highlighter import Highlighter

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()

    if 'llm_client' not in st.session_state:
        try:
            st.session_state.llm_client = LLMClient()
        except Exception as e:
            st.error(f"LLM客户端初始化失败: {e}")
            st.session_state.llm_client = None

    if 'document_parser' not in st.session_state:
        st.session_state.document_parser = DocumentParser()
        st.session_state.robust_parser = RobustParser()

    if 'highlighter' not in st.session_state:
        st.session_state.highlighter = Highlighter()

    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

# 初始化
init_session_state()

# 自动初始化知识库
if not st.session_state.initialized:
    try:
        # 检查是否有初始化文件
        if os.path.exists("initialized_qa_pairs.json"):
            with open("initialized_qa_pairs.json", "r", encoding="utf-8") as f:
                qa_pairs = json.load(f)

            if qa_pairs:
                # 添加到向量存储
                st.session_state.vector_store.clear_collection()
                st.session_state.vector_store.add_documents(qa_pairs)
                st.session_state.initialized = True
                st.session_state.last_update = datetime.now()
                print(f"自动加载了 {len(qa_pairs)} 个问答对")
    except Exception as e:
        print(f"自动初始化失败: {e}")

# 页面标题
st.title("🤖 美易在线答疑")
st.markdown("""
美纳里尼中国合规智能助手

**功能：**
- 📚 智能问答：基于知识库自动回答合规和报销相关问题
- 🔍 自动检索：从知识库中检索相关内容并生成回答
- 📝 人工兜底：知识库无答案时转人工客服
- 📊 知识库管理：自动加载和更新知识库
""")

# 侧边栏
with st.sidebar:
    st.header("📚 知识库管理")

    # 显示知识库状态
    doc_count = st.session_state.vector_store.get_document_count()
    st.subheader("知识库状态")
    st.metric("文档总数", doc_count)

    # 知识库来源配置
    st.subheader("知识库来源")
    rag_directory = st.text_input(
        "知识库目录",
        value="C:\\Users\\jj\\Desktop\\RAG",
        help="包含Excel知识库文件的目录"
    )

    # 更新知识库按钮
    if st.button("更新知识库", type="primary"):
        with st.spinner("正在更新知识库..."):
            try:
                # 首先尝试使用健壮解析器
                qa_pairs = st.session_state.robust_parser.parse_excel_safe(rag_directory + "\\报销.xlsx")

                # 如果没有找到问答对，尝试使用普通解析器解析目录
                if not qa_pairs:
                    qa_pairs = st.session_state.document_parser.parse_directory(rag_directory)

                if qa_pairs:
                    # 清空现有向量存储
                    st.session_state.vector_store.clear_collection()

                    # 添加新文档
                    st.session_state.vector_store.add_documents(qa_pairs)

                    # 更新状态
                    st.session_state.initialized = True
                    st.session_state.last_update = datetime.now()

                    st.success(f"成功更新知识库！共添加 {len(qa_pairs)} 个问答对")
                else:
                    st.warning("未找到任何有效的问答对")

            except Exception as e:
                st.error(f"更新知识库失败: {e}")

    # 显示上次更新时间
    if st.session_state.last_update:
        st.caption(f"上次更新: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    st.divider()

    # 系统设置
    st.subheader("系统设置")
    threshold = st.slider("相似度阈值", 0.1, 0.9, 0.3, 0.1)
    max_tokens = st.slider("回答长度", 100, 2000, 1024, 100)
    temperature = st.slider("回答多样性", 0.1, 1.0, 0.7, 0.1)

    st.divider()

    # 系统信息
    st.caption("系统信息")
    st.text(f"向量存储: {st.session_state.vector_store.persist_directory}")
    st.text(f"文档数量: {doc_count}")

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
                    # 搜索相关文档
                    matched_docs = st.session_state.vector_store.search(
                        query=prompt,
                        k=3,
                        threshold=0.3
                    )

                    if matched_docs:
                        # 提取上下文
                        context = "\n\n".join([
                            f"问题: {doc['question']}\n答案: {doc['answer']}"
                            for doc in matched_docs
                        ])

                        # 提取关键词
                        keywords = st.session_state.highlighter.extract_keywords_from_question(
                            prompt, context
                        )

                        # 生成回答
                        system_prompt = """你是一个美纳里尼中国的合规和报销智能助手。请基于提供的知识库信息回答用户问题。
回答要求：
1. 准确、简洁地回答问题
2. 如果知识库中有相关信息，请基于该信息回答
3. 如果知识库中没有相关信息，请说明无法回答并建议联系人工客服
4. 保持专业、友好的语调"""

                        answer = st.session_state.llm_client.generate_response(
                            prompt=prompt,
                            context=context,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            system_prompt=system_prompt
                        )

                        # 格式化回答，添加引用和高亮
                        answer = st.session_state.highlighter.format_response_with_references(
                            answer, matched_docs, keywords
                        )

                        # 添加到会话状态
                        st.session_state.messages.append({"role": "assistant", "content": answer})

                    else:
                        # 没有找到相关文档
                        answer = """很抱歉，我在知识库中没有找到与您问题相关的信息。

📝 建议：
1. 请检查问题表述是否清晰
2. 尝试使用不同的关键词描述您的问题
3. 如果仍需帮助，请联系人工客服获取进一步支持

📞 客服联系方式：请通过公司内部通讯系统联系IT支持团队"""

                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_msg = f"处理过程中发生错误: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 页脚
st.divider()
st.caption("""
🤖 美易在线答疑 - 基于RAG技术的智能问答系统
美纳里尼中国合规报销系统 | 2024
""")