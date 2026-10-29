# 美纳里尼合规报销智能助手

一个基于RAG（检索增强生成）的智能问答系统，专为美纳里尼中国员工设计，用于解答合规和报销相关问题。

## 🌟 功能特性

### 核心功能
- **智能问答**：基于知识库的智能检索和回答
- **关键词高亮**：搜索结果中的关键词自动高亮显示
- **相似度匹配**：智能计算问题与知识库的相似度
- **配置灵活**：可调整显示答案数和相似度阈值
- **知识库管理**：支持上传.docx文件更新知识库

### 界面特点
- **现代化设计**：使用Bootstrap 5和CSS3动画
- **响应式布局**：支持手机和电脑访问
- **直观操作**：快捷问题按钮、配置面板
- **实时反馈**：输入状态指示、在线状态显示

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 依赖包：Flask, python-docx

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/wyjsuper/meiyi-bot.git
   cd meiyi-bot
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **准备知识库**
   - 将QA文档放在 `C:\Users\jj\Desktop\RAG\QA.docx`
   - 或通过Web界面上传新文档

4. **启动应用**
   ```bash
   # 本地访问
   python web_app_final.py --port 5003
   
   # 或使用Ngrok（外网访问）
   python start_with_ngrok.py --ngrok --port 5003
   ```

5. **访问应用**
   - 本地：http://localhost:5003
   - 外网：Ngrok生成的URL

## 📁 项目结构

```
meiyi-bot/
├── web_app_final.py      # 最终优化版（推荐）
├── web_app_v2.py         # 第二版本
├── app_optimized.py      # 精简优化版
├── start_with_ngrok.py   # Ngrok启动脚本
├── templates/           # HTML模板
│   ├── index_final.html  # 最终版模板
│   └── index_v2.html     # 第二版模板
├── static/              # 静态文件
│   ├── css/
│   └── js/
├── requirements.txt     # 依赖列表
└── README.md           # 项目说明
```

## ⚙️ 配置说明

### 主要参数
- **最大显示答案数**：默认2个（1-10可调）
- **相似度阈值**：默认40%（0-100%可调）
- **知识库路径**：`C:\Users\jj\Desktop\RAG\QA.docx`

### API接口
- `GET /api/status` - 获取服务状态
- `POST /api/ask` - 问答接口
- `GET/POST /api/config` - 配置管理
- `POST /api/upload` - 上传知识库

## 🔧 部署选项

### 1. 本地部署
```bash
python web_app_final.py --host 0.0.0.0 --port 5003
```

### 2. 使用Ngrok（外网访问）
```bash
pip install pyngrok
python start_with_ngrok.py --ngrok --port 5003
```

### 3. 云服务器部署
建议使用Docker部署，参考部署文档。

## 📋 知识库格式

### 文档要求
- **格式**：Word文档 (.docx)
- **内容**：问答对，格式为"问题-答案"
- **示例**：
  ```
  问题：为什么重置密码的邮件一直收不到？
  答案：请检查垃圾邮件箱，或联系IT部门重新发送。
  ```

### 自动解析
系统会自动解析文档中的问答对，识别包含问号的行为问题，下一行作为答案。

## 🎯 使用场景

1. **员工咨询**：解答报销流程、系统登录等问题
2. **合规支持**：提供合规政策和流程指导
3. **自助服务**：减少人工客服压力
4. **知识管理**：集中管理和更新FAQ

## 🛠️ 开发说明

### 版本区别
- **web_app_final.py**：功能完整，推荐使用
- **app_optimized.py**：代码精简，适合轻量部署
- **web_app_v2.py**：中间版本，保留完整功能

### 扩展开发
- 添加更多文档格式支持（PDF、Excel）
- 实现用户认证和历史记录
- 集成外部API增强回答
- 添加多语言支持

## 📞 技术支持

如有问题，请通过以下方式联系：
- GitHub Issues：提交问题报告
- 邮件：通过公司内部通讯系统联系IT支持团队

## 📄 许可证

本项目仅供美纳里尼中国内部使用。

---

**Co-Authored-By**: Claude Code <noreply@anthropic.com>