# 美易机器人GitHub设置指南 - wyjsuper 专属

## 🎯 目标
将美易机器人项目自动同步到您的GitHub仓库：https://github.com/wyjsuper

## 📋 使用步骤

### 方法一：一键同步脚本（推荐）

1. **运行一键脚本**
   ```bash
   # Windows用户
   双击 "推送到wyjsuper.bat"
   
   # 或者命令行运行
   python push_to_wyjsuper.py
   ```

2. **脚本功能**
   - 自动检测代码更改
   - 自动提交更改
   - 自动推送到GitHub
   - 错误提示和解决方案

### 方法二：分步执行

#### 1. 首次设置（如果还没有Git仓库）

```bash
# 初始化Git仓库
python sync_to_github.py init

# 添加您的GitHub仓库
python sync_to_github.py add-remote
```

#### 2. 日常同步

```bash
# 查看状态
python sync_to_github.py status

# 提交并推送
python sync_to_github.py full-sync

# 或者只提交不推送
python sync_to_github.py commit

# 或者只推送不提交
python sync_to_github.py push
```

## 🔧 GitHub设置

### 1. 创建GitHub仓库

如果还没有创建仓库，请：

1. 访问 [github.com](https://github.com)
2. 登录您的账户 (wyjsuper)
3. 点击 "New repository"
4. 填写：
   - Repository name: `meiyi-bot`
   - Description: `美易机器人在线答疑系统`
   - 选择 Public（免费）或 Private
5. 点击 "Create repository"

### 2. 配置认证

#### 方法A: Personal Access Token（推荐）

```bash
# 在GitHub设置中生成Token
# 1. 进入 Settings > Developer settings > Personal access tokens
# 2. 点击 "Generate new token"
# 3. 选择 scopes: repo (full control of private repositories)
# 4. 生成Token并复制

# 使用Token推送
git push https://wyjsuper@github.com/wyjsuper/meiyi-bot.git
# 输入您的GitHub密码和Token
```

#### 方法B: SSH密钥

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "wyjsuper@example.com"

# 启动SSH agent
eval "$(ssh-agent -s)"

# 添加密钥
ssh-add ~/.ssh/id_ed25519

# 复制公钥到剪贴板
cat ~/.ssh/id_ed25519.pub

# 在GitHub设置中添加公钥
# 1. 进入 Settings > SSH and GPG keys
# 2. 点击 "New SSH key"
# 3. 粘贴公钥内容
```

### 3. 配置Git用户信息

```bash
git config --global user.name "wyjsuper"
git config --global user.email "wyjsuper@example.com"
```

## 🚀 自动化配置

### 1. GitHub Actions自动同步

项目已配置自动同步工作流：

1. 打开 `.github/workflows/auto-sync.yml`
2. 确认仓库URL正确
3. 推送代码后，Actions会自动运行

### 2. Windows计划任务

创建定时自动同步：

```powershell
# 管理员身份运行PowerShell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\meiyi-bot\push_to_wyjsuper.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MeiyiBotAutoSync"
```

## 📝 提交规范

### 提交消息格式
```
类型: 简短描述

详细说明（可选）

- 功能1
- 功能2
- 修复1

Co-Authored-By: Claude Code <noreply@anthropic.com>
```

### 提交类型示例
- `feat: 添加密码搜索优化功能`
- `fix: 修复GitHub同步问题`
- `docs: 更新README文档`
- `refactor: 重构搜索算法`
- `test: 添加单元测试`

## 🔍 故障排除

### 常见错误

1. **认证失败**
   ```
   remote: Authentication failed
   解决: 使用Personal Access Token或配置SSH
   ```

2. **仓库不存在**
   ```
   remote: Repository not found
   解决: 确保已创建仓库：https://github.com/wyjsuper/meiyi-bot
   ```

3. **权限被拒绝**
   ```
   Permission denied (publickey)
   解决: 检查SSH密钥配置或使用HTTPS
   ```

4. **网络问题**
   ```
   Failed to connect to github.com
   解决: 检查网络，使用代理或VPN
   ```

### 调试命令

```bash
# 检查Git配置
git config --list

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline -5

# 查看分支
git branch -a

# 查看状态
git status

# 查看具体更改
git diff
```

## 💡 最佳实践

1. **频繁提交**：小的改动及时提交
2. **清晰消息**：使用描述性的提交消息
3. **定期推送**：不要在本地堆积过多提交
4. **备份重要代码**：GitHub作为远程备份
5. **使用分支**：新功能在分支上开发

## 🎉 完成后的操作

1. **访问GitHub仓库**
   - 打开 https://github.com/wyjsuper/meiyi-bot
   - 查看您的代码
   - Star ⭐ 和 Watch 👀 仓库

2. **配置GitHub Pages**（可选）
   - 在仓库设置中启用GitHub Pages
   - 选择main分支
   - 访问您的网站

3. **邀请协作者**（如果需要）
   - 进入仓库 > Settings > Collaborators
   - 添加团队成员

---

**提示**: 定期检查 Actions 页面，确保自动同步正常工作。