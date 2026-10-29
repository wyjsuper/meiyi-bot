# 美易机器人 - IT资产管理系统

基于RAG（检索增强生成）技术的智能问答助手，为美纳里尼中国员工提供IT资产管理和报销相关问题的自动解答。

## 功能特点

- 🤖 **智能问答**：基于知识库自动检索并生成准确回答
- 📚 **知识库管理**：支持Excel文件上传和解析
- 🔍 **实时检索**：自动从知识库中查找相关内容
- 📝 **人工兜底**：知识库无答案时转人工客服
- 🎯 **关键词高亮**：智能高亮显示匹配的关键词
- 📊 **参考来源**：显示答案的原始文档和来源

## 技术栈

- **前端框架**：Streamlit
- **AI模型**：GLM-4.7 Flash（智谱AI API）
- **RAG框架**：LangChain + ChromaDB
- **文档解析**：openpyxl
- **向量嵌入**：sentence-transformers（多语言模型）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置GLM API Key

编辑 `.env` 文件，设置你的智谱AI API Key：

```
GLM_API_KEY=your_api_key_here
```

获取API Key：
- 访问 https://open.bigmodel.cn/
- 注册并获取API Key

### 3. 启动应用

```bash
streamlit run app.py
```

访问 http://localhost:8501

## 知识库格式

Excel文件应包含以下格式（支持自动识别列）：

| 问题 | 答案 |
|------|------|
| 我的IT资产如何报销？ | 请按照以下流程办理... |
| 固定资产折旧方法是什么？ | 公司采用直线法进行折旧... |

**支持的格式：**
- 第A列 = 问题
- 第B列 = 答案
- 表头可以在任意位置（默认从第2行开始）
- 支持多Sheet

## 配置说明

主要配置项在 `.env` 文件中：

- `OLLAMA_MODEL`: Ollama模型名称
- `SIMILARITY_THRESHOLD`: 相似度阈值（0-1）
- `SEARCH_TOP_K`: 检索返回的文档数量
- `TEMPERATURE`: 生成温度（0-1），越低越确定

## 项目结构

```
meiyi-bot/
├── app.py                      # Streamlit主应用
├── requirements.txt            # Python依赖
├── .env                        # 环境配置
├── README.md                   # 项目说明
├── utils/                      # 工具模块
│   ├── document_parser.py      # Excel解析器
│   ├── vector_store.py         # 向量数据库管理
│   ├── llm_client.py           # LLM客户端
│   └── highlighter.py          # 关键词高亮工具
└── data/                       # 数据目录
    ├── chroma_db/              # 向量数据库存储
    └── knowledge_base/         # 知识库文件
```

## 使用指南

### 上传知识库

1. 点击侧边栏的"上传知识库"
2. 选择Excel文件
3. 点击"解析并更新知识库"
4. 等待解析完成

### 提问

1. 在主对话框中输入问题
2. 系统会自动从知识库检索相关内容
3. AI生成回答并显示参考来源
4. 如果知识库无答案，显示人工客服信息

### 人工介入

当以下情况发生时，系统会提示联系人工客服：
- 知识库中没有检索到相关内容
- 所有检索结果的相似度低于阈值

## 常见问题

### Q: Ollama服务无法连接怎么办？

A: 确保 Ollama 正在运行：
```bash
ollama serve
```

### Q: API调用失败怎么办？

A: 请检查：
1. `.env`文件中的`GLM_API_KEY`是否正确
2. 网络连接是否正常
3. API key是否有足够的余额
4. 是否超过了调用频率限制

### Q: 如何重新加载知识库？

A: 上传新的Excel文件，系统会自动解析并更新向量数据库。

### Q: 如何提高回答准确性？

A:
- 确保知识库内容准确完整
- 调整相似度阈值（在代码中修改）
- 优化Prompt工程

### Q: 支持哪些文档格式？

A: 当前支持Excel文件（.xlsx, .xls），未来计划支持PDF、Word等格式。

## 开发计划

- [ ] 支持PDF文档解析
- [ ] 支持Word文档解析
- [ ] 多轮对话上下文管理
- [ ] 知识库搜索和过滤
- [ ] 用户历史记录
- [ ] 实时客服系统集成

## 联系方式

如有问题或建议，请联系：
- 客服热线：400-XXX-XXXX
- 客服邮箱：support@meiyibot.com

## 许可证

内部使用
