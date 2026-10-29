import streamlit as st
import os
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
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# 标题和说明
st.title("🤖 美易在线答疑")
st.markdown("""
美纳里尼中国合规智能助手

**功能：**
- 📚 智能问答：基于知识库自动回答合规和报销相关问题
- 📤 文档上传：支持Excel知识库文件上传
- 🔍 实时检索：自动从知识库中检索相关内容
- 📝 人工兜底：知识库无答案时转人工客服
""")

# 侧边栏
with st.sidebar:
    st.header("📚 知识库管理")
    st.subheader("上传知识库")
    uploaded_file = st.file_uploader(
        "选择Excel文件",
        type=['xlsx', 'xls'],
        help="上传包含问答对的Excel文件"
    )

    if uploaded_file is not None:
        if st.button("解析并更新知识库", type="primary"):
            with st.spinner("正在解析文件..."):
                try:
                    # 保存文件
                    file_path = os.path.join('data', 'knowledge_base', uploaded_file.name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())

                    # 尝试导入模块
                    try:
                        from utils.document_parser import ExcelParser
                        parser = ExcelParser(file_path)
                        documents = parser.parse_excel()

                        if documents:
                            # 显示前几条结果
                            st.success(f"成功解析 {len(documents)} 条问答对！")
                            # 显示前3条
                            with st.expander("预览解析结果"):
                                for i, doc in enumerate(documents[:3], 1):
                                    st.write(f"**{i}. 问题:** {doc['question']}")
                                    st.write(f"**答案:** {doc['answer'][:100]}...")
                                    st.write("---")
                            st.session_state.initialized = True
                        else:
                            st.warning("未找到有效的问答对")

                    except Exception as e:
                        st.error(f"解析模块加载失败: {e}")
                        st.info(f"文件已保存，但无法解析内容。错误: {e}")

                except Exception as e:
                    st.error(f"文件保存失败: {e}")

    st.divider()
    st.caption("系统状态")
    if st.session_state.initialized:
        st.success("✓ 知识库已加载")
    else:
        st.warning("⚠️ 请上传知识库文件")

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
        with st.spinner("正在思考..."):
            # 模拟AI回答
            if st.session_state.initialized:
                answer = f"您的问题是：{prompt}\n\n" \
                         f"这是一个模拟回答。实际使用时，系统会：\n" \
                         f"1. 从知识库检索相关合规和报销内容\n" \
                         f"2. 使用GLM-4.7 Flash API生成回答\n" \
                         f"3. 显示参考来源\n" \
                         f"4. 如果没有相关内容，会建议联系人工客服"
            else:
                answer = f"您的问题是：{prompt}\n\n" \
                         f"⚠️ 请先上传知识库文件后才能使用问答功能。"

            st.markdown(answer)

    # 保存AI回答到历史
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # 清理历史消息，避免太长
    if len(st.session_state.messages) > 20:
        st.session_state.messages = st.session_state.messages[-10:]

# 页脚
st.divider()
st.caption("""
🤖 美易在线答疑 - 基于RAG技术的智能问答系统
美纳里尼中国合规报销系统 | 2024
""")