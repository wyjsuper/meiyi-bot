#!/usr/bin/env python3
"""
美易机器人GitHub完整设置 - wyjsuper专属
一键完成所有GitHub配置
"""

import os
import subprocess
import sys
from datetime import datetime

def run_cmd(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return None

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def check_git_installed():
    """检查Git是否安装"""
    print("🔍 检查Git安装...")
    result = run_cmd(['git', '--version'])
    if result and result.returncode == 0:
        print("✅ Git已安装")
        print(f"版本: {result.stdout.strip()}")
        return True
    else:
        print("❌ Git未安装")
        print("请先安装Git for Windows: https://git-scm.com/download/win")
        return False

def initialize_git_repo():
    """初始化Git仓库"""
    print("🔧 初始化Git仓库...")

    if os.path.exists('.git'):
        print("✅ Git仓库已存在")
        return True

    result = run_cmd(['git', 'init'])
    if result and result.returncode == 0:
        print("✅ Git仓库初始化成功")

        # 配置用户
        run_cmd(['git', 'config', 'user.name', 'wyjsuper'])
        run_cmd(['git', 'config', 'user.email', 'wyjsuper@example.com'])

        # 首次提交
        run_cmd(['git', 'add', '.'])
        run_cmd(['git', 'commit', '-m', 'Initial commit: 美易机器人在线答疑系统'])

        return True
    else:
        print("❌ Git仓库初始化失败")
        return False

def add_github_remote():
    """添加GitHub远程仓库"""
    print("🔗 添加GitHub远程仓库...")

    repo_url = "https://github.com/wyjsuper/meiyi-bot.git"

    result = run_cmd(['git', 'remote', 'add', 'origin', repo_url])
    if result and result.returncode == 0:
        print(f"✅ 添加远程仓库成功: {repo_url}")
        return True
    elif result and 'already exists' in result.stderr:
        print("⚠️ 远程仓库已存在")

        # 尝试推送到现有仓库
        print("🚀 尝试连接到GitHub...")
        result = run_cmd(['git', 'push', 'origin', 'main'])
        if result and result.returncode == 0:
            print("✅ 连接成功，仓库已同步")
            return True
        else:
            print("⚠️ 连接失败，可能需要认证")
            print("\n请认证后运行:")
            print("git push origin main")
            return True
    else:
        print(f"❌ 添加远程仓库失败")
        print(f"请手动添加: git remote add origin {repo_url}")
        return False

def setup_github_pages():
    """设置GitHub Pages配置"""
    print("📄 创建GitHub Pages配置文件...")

    # 创建docs目录（如果不存在）
    os.makedirs('docs', exist_ok=True)

    # 创建index.html
    index_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美易在线答疑</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .info {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>🤖 美易在线答疑</h1>

    <div class="info">
        <h2>系统说明</h2>
        <p>这是一个基于RAG技术的智能问答系统，用于美纳里尼中国的合规和报销咨询。</p>

        <h2>功能特点</h2>
        <ul>
            <li>智能问答：基于知识库自动回答问题</li>
            <li>多答案显示：显示所有相关答案</li>
            <li>模糊搜索：支持同义词扩展</li>
            <li>分类浏览：按类别查看常见问题</li>
        </ul>

        <h2>使用方法</h2>
        <p>1. 克隆仓库到本地</p>
        <p>2. 运行: streamlit run ultimate_app.py</p>
        <p>3. 访问: http://localhost:8501</p>
    </div>

    <div class="info">
        <p><strong>最后更新：</strong> {date}</p>
        <p><strong>作者：</strong> wyjsuper</p>
        <p><strong>GitHub：</strong> <a href="https://github.com/wyjsuper/meiyi-bot">https://github.com/wyjsuper/meiyi-bot</a></p>
    </div>
</body>
</html>
"""

    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(index_content.format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # 创建.gitignore
    if not os.path.exists('.gitignore'):
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/

# Logs
*.log
logs/

# Temporary files
*.tmp
temp/
test_github_sync.txt
"""
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)

    print("✅ GitHub Pages配置文件创建成功")
    return True

def create_readme():
    """创建README文件"""
    print("📝 创建README文件...")

    readme_content = """# 美易在线答疑系统

基于RAG（检索增强生成）的智能问答系统，用于美纳里尼中国的合规和报销咨询。

## 🌟 系统特点

- 🤖 **智能问答**：基于知识库自动回答合规和报销相关问题
- 🔍 **多答案显示**：显示所有相关的答案，而不只是最相似的
- 📂 **分类浏览**：按类别查看常见问题
- 💡 **智能推荐**：根据关键词推荐相关问题
- 📊 **统计分析**：实时显示搜索统计和历史记录

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Git

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/wyjsuper/meiyi-bot.git
   cd meiyi-bot
   ```

2. **安装依赖**
   ```bash
   pip install streamlit python-docx
   ```

3. **启动应用**
   ```bash
   streamlit run ultimate_app.py
   ```

4. **访问应用**
   打开浏览器访问: http://localhost:8501

## 📊 知识库

根据 `C:\\Users\\jj\\Desktop\\RAG\\QA.docx` 解析结果：
- **总问答对**：122个
- **密码相关**：6个
- **报销相关**：75个
- **登录相关**：5个
- **系统问题**：10个
- **其他**：26个

## 🔧 GitHub同步

### 推送到GitHub
```bash
# 一键同步
python push_to_wyjsuper.py

# 或者分步执行
python sync_to_github.py full-sync
```

### 自动化
项目已配置：
- GitHub Actions自动同步
- Windows计划任务支持
- Git钩子自动提交

## 📱 界面展示

### 主界面
1. **智能问答**：主要交互界面
2. **分类浏览**：按类别查看问题
3. **统计信息**：系统使用统计

### 功能特性
- 关键词高亮显示
- 智能问题推荐
- 实时搜索统计
- 多答案展示

## 🛠️ 技术栈

- **前端框架**：Streamlit
- **文档解析**：python-docx
- **搜索算法**：增强的模糊匹配算法
- **分类系统**：自动问答分类
- **高亮显示**：HTML关键词高亮

## 🔄 更新日志

### v2.0 (终极版)
- ✅ 添加多选项卡界面
- ✅ 实现分类浏览功能
- ✅ 添加统计信息面板
- ✅ 优化搜索算法

### v1.5 (增强版)
- ✅ 支持多答案显示
- ✅ 添加模糊搜索功能
- ✅ 关键词高亮显示

### v1.0 (基础版)
- ✅ 基础问答功能
- ✅ 文档解析
- ✅ 简单搜索

## 📞 联系支持

- **开发团队**：美纳里尼中国IT部门
- **GitHub**：https://github.com/wyjsuper/meiyi-bot
- **作者**：wyjsuper

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**最后更新**: {date}

**GitHub Pages**: https://wyjsuper.github.io/meiyi-bot/
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content.format(date=datetime.now().strftime('%Y-%m-%d')))

    print("✅ README文件创建成功")
    return True

def commit_and_push():
    """提交并推送到GitHub"""
    print("\n🔄 提交并推送到GitHub...")

    # 添加所有文件
    result = run_cmd(['git', 'add', '.'])
    if result is None or result.returncode != 0:
        print("❌ 添加文件失败")
        return False

    # 提交
    commit_msg = f"GitHub初始化配置: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    result = run_cmd(['git', 'commit', '-m', commit_msg])

    if result and result.returncode == 0:
        print("✅ 提交成功")
    else:
        print("⚠️ 提交可能有问题，但继续推送")

    # 推送
    print("🚀 推送到GitHub...")
    result = run_cmd(['git', 'push', 'origin', 'main'])

    if result and result.returncode == 0:
        print("\n🎉 推送成功！")
        print("📍 仓库地址: https://github.com/wyjsuper/meiyi-bot")
        return True
    else:
        print("\n⚠️ 推送失败")
        print("请检查认证和网络连接")
        return False

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "=" * 60)
    print("🎉 设置完成！")
    print("=" * 60)

    print("\n📍 您的GitHub仓库:")
    print("https://github.com/wyjsuper/meiyi-bot")

    print("\n🔧 使用方法:")
    print("1. 运行应用: streamlit run ultimate_app.py")
    print("2. 一键同步: python push_to_wyjsuper.py")
    print("3. 双击同步: 推送到wyjsuper.bat")

    print("\n📖 相关文档:")
    print("- SETUP_GUIDE.md: 详细设置指南")
    print("- README_GITHUB_SYNC.md: GitHub同步说明")
    print("- README.md: 项目说明")

    print("\n🚀 下一步:")
    print("1. 访问GitHub仓库查看代码")
    print("2. 配置GitHub Pages（可选）")
    print("3. 邀请协作者（可选）")
    print("4. 设置自动化定时任务")

def main():
    """主函数"""
    print("🤖 美易机器人GitHub完整设置 - wyjsuper专属")
    print("一键完成所有GitHub配置")

    # 检查Git
    if not check_git_installed():
        return

    # 初始化仓库
    if not initialize_git_repo():
        return

    # 添加远程仓库
    if not add_github_remote():
        return

    # 设置GitHub Pages
    setup_github_pages()

    # 创建README
    create_readme()

    # 提交并推送
    success = commit_and_push()

    # 显示后续步骤
    show_next_steps()

if __name__ == "__main__":
    main()