import streamlit as st
import os

# 页面配置
st.set_page_config(
    page_title="美易机器人 - IT资产管理系统",
    page_icon="🤖",
    layout="wide"
)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# 标题和说明
st.title("🤖 美易机器人 - IT资产管理系统")
st.markdown("""
美纳里尼中国IT资产管理智能助手

**功能：**
- 📚 智能问答：基于知识库自动回答IT资产和报销相关问题
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

                    # 这里可以添加实际的解析逻辑
                    st.success(f"文件已保存: {uploaded_file.name}")
                    st.session_state.initialized = True

                except Exception as e:
                    st.error(f"解析失败: {e}")

    st.divider()
    st.caption("系统状态")
    if st.session_state.initialized:
        st.success("✓ 已初始化")
    else:
        st.warning("⚠️ 未初始化")

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
            # 这里可以添加实际的问答逻辑
            answer = f"您的问题是：{prompt}\n\n这是一个模拟回答。实际使用时需要配置API和知识库。"
            st.markdown(answer)

            # 如果没有初始化，提示用户上传知识库
            if not st.session_state.initialized:
                st.warning("⚠️ 请先上传知识库文件")

    # 保存AI回答到历史
    st.session_state.messages.append({"role": "assistant", "content": answer})

# 页脚
st.divider()
st.caption("""
🤖 美易机器人 - 基于RAG技术的智能问答系统
美纳里尼中国IT资产管理系统 | 2024
""")