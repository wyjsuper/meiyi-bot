# 美易机器人GitHub自动同步指南

本指南说明如何将美易机器人项目自动同步到GitHub仓库。

## 🚀 快速开始

### 1. 首次设置

```bash
# 1. 初始化Git仓库
python auto_commit_push.py init

# 2. 添加远程仓库（替换为您的GitHub仓库URL）
python auto_commit_push.py add-remote https://github.com/您的用户名/meiyi-bot.git

# 3. 提交初始代码
python auto_commit_push.py commit-push
```

### 2. 日常使用

```bash
# 提交并推送所有更改
python auto_commit_push.py

# 或者提交特定消息
python auto_commit_push.py commit-push "修复了密码搜索问题"

# 只提交不推送
python auto_commit_push.py commit

# 只推送不提交
python auto_commit_push.py push

# 查看状态
python auto_commit_push.py status
```

## 🔧 PowerShell用户（Windows）

```powershell
# 执行PowerShell脚本
.\git-sync.ps1

# 或者指定命令
.\git-sync.ps1 commit-push

# 添加远程仓库
.\git-sync.ps1 add-remote https://github.com/您的用户名/meiyi-bot.git
```

## 📁 创建GitHub仓库步骤

### 方法1: 网页端创建
1. 访问 [github.com](https://github.com)
2. 点击 "New repository"
3. 填写仓库名称（如：meiyi-bot）
4. 设置为Public（免费）或Private
5. 点击 "Create repository"

### 方法2: 命令行创建
```bash
# 使用gh CLI（需要先安装）
gh repo create meiyi-bot --public --source=. --remote=origin --push
```

## 🔄 自动化选项

### 1. GitHub Actions自动同步

项目已配置GitHub Actions工作流（`.github/workflows/auto-sync.yml`）：
- 每天早上8点自动运行
- 推送更改到GitHub
- 使用GitHub Action Token认证

### 2. Windows计划任务

```powershell
# 创建计划任务（管理员权限）
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\meiyi-bot\auto_commit_push.py commit-push"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MeiyiBotAutoSync"
```

### 3. Git钩子自动提交

项目已配置pre-commit钩子：
- 每次提交前自动检查更改
- 自动提交未跟踪的文件

## ⚙️ 高级配置

### 自定义Git用户
```bash
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱"
```

### 配置SSH密钥（推荐）
```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "您的邮箱"

# 添加到SSH agent
ssh-add ~/.ssh/id_ed25519

# 复制公钥到GitHub
cat ~/.ssh/id_ed25519.pub
```

### 配置Git代理
```bash
# 如果使用代理
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy https://proxy.example.com:8080
```

## 🔍 故障排除

### 常见问题

1. **Git命令未找到**
   ```
   错误: git: command not found
   解决: 安装Git for Windows
   ```

2. **认证失败**
   ```
   错误: remote: Repository not found
   解决: 检查远程URL是否正确，确认仓库存在
   ```

3. **编码问题**
   ```
   错误: fatal: bad commit message
   解决: 使用简短的英文字符消息
   ```

4. **权限被拒绝**
   ```
   错误: Permission denied (publickey)
   解决: 配置SSH密钥或使用Personal Access Token
   ```

### 调试命令

```bash
# 检查Git配置
git config --list

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline

# 查看分支
git branch -a

# 查看状态
git status
```

## 📋 提交规范

### 提交消息格式
```
类型: 简短描述

详细说明（可选）

- 改动1
- 改动2
- 改动3

Co-Authored-By: Claude Code <noreply@anthropic.com>
```

### 提交类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建或辅助工具变动

## 🎯 推荐工作流

1. **开发阶段**
   ```bash
   # 开发代码
   # 测试功能
   git add .
   git commit -m "feat: 添加新功能"
   git push
   ```

2. **修复阶段**
   ```bash
   # 修复bug
   git add .
   git commit -m "fix: 修复搜索算法问题"
   git push
   ```

3. **发布阶段**
   ```bash
   # 创建标签
   git tag -a v1.0.0 -m "版本1.0.0"
   git push origin v1.0.0
   ```

## 📊 自动同步状态监控

### 查看同步状态
```bash
# 检查最后一次提交
git log -1 --oneline

# 查看远程分支
git branch -r

# 检查工作区状态
git status
```

### GitHub Actions状态
- 访问 [GitHub仓库页面](https://github.com/您的用户名/meiyi-bot)
- 点击 "Actions" 标签
- 查看 "Auto Commit and Push" 工作流

---

**提示**: 建议定期推送代码到GitHub，这样可以：
1. 备份代码
2. 便于团队协作
3. 记录开发历史
4. 便于版本回滚