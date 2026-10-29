#!/usr/bin/env python3
"""
美易机器人GitHub自动同步工具
自动提交代码并推送到GitHub仓库
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

class GitAutoSync:
    """Git自动同步工具"""

    def __init__(self, repo_path: str = ".", git_user: str = "美纳里尼IT", git_email: str = "it.menarini@menarini.com"):
        self.repo_path = repo_path
        self.git_user = git_user
        self.git_email = git_email
        self.branch = "main"

    def run_command(self, cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """运行Git命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result
        except Exception as e:
            raise Exception(f"命令执行失败: {cmd}\n错误: {e}")

    def initialize_repo(self) -> bool:
        """初始化Git仓库"""
        if os.path.exists(os.path.join(self.repo_path, '.git')):
            print("✅ Git仓库已存在")
            return True

        print("🔄 初始化Git仓库...")
        result = self.run_command(['git', 'init'])
        if result.returncode != 0:
            raise Exception("初始化Git仓库失败")

        # 配置Git用户
        self.run_command(['git', 'config', 'user.name', self.git_user])
        self.run_command(['git', 'config', 'user.email', self.git_email])

        # 创建初始提交
        self.run_command(['git', 'add', '.'])
        result = self.run_command(['git', 'commit', '-m', 'Initial commit: 美易机器人在线答疑系统'])

        print("✅ Git仓库初始化完成")
        return True

    def add_remote(self, remote_url: str) -> bool:
        """添加远程仓库"""
        try:
            self.run_command(['git', 'remote', 'add', 'origin', remote_url])
            print(f"✅ 添加远程仓库: {remote_url}")
            return True
        except Exception as e:
            if "already exists" in str(e):
                print("⚠️ 远程仓库已存在")
                return True
            raise

    def create_and_push_branch(self, branch_name: str) -> bool:
        """创建并推送分支"""
        try:
            # 检查分支是否存在
            result = self.run_command(['git', 'branch', '-a'])

            if branch_name in result.stdout or f'* {branch_name}' in result.stdout:
                print(f"⚠️ 分支 {branch_name} 已存在，切换到该分支")
                self.run_command(['git', 'checkout', branch_name])
            else:
                # 创建新分支
                self.run_command(['git', 'checkout', '-b', branch_name])
                print(f"✅ 创建新分支: {branch_name}")

            # 推送分支到远程
            self.run_command(['git', 'push', '-u', 'origin', branch_name])
            print(f"✅ 推送分支 {branch_name} 到远程")
            return True
        except Exception as e:
            raise Exception(f"分支创建和推送失败: {e}")

    def auto_commit(self, commit_message: str = None, files: List[str] = None) -> bool:
        """自动提交更改"""
        if commit_message is None:
            commit_message = f"自动更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        try:
            # 检查是否有更改
            result = self.run_command(['git', 'status', '--porcelain'])
            if not result.stdout.strip():
                print("ℹ️ 没有需要提交的更改")
                return True

            # 添加文件
            if files:
                for file in files:
                    self.run_command(['git', 'add', file])
            else:
                self.run_command(['git', 'add', '.'])

            # 提交
            result = self.run_command(['git', 'commit', '-m', commit_message])
            if result.returncode == 0:
                print(f"✅ 提交成功: {commit_message}")
                return True
            else:
                # 尝试处理非UTF-8编码问题
                try:
                    # 使用escape参数处理编码问题
                    result = self.run_command(['git', 'commit', '-m', commit_message.encode('utf-8', 'ignore').decode('utf-8', 'ignore')])
                    if result.returncode == 0:
                        print(f"✅ 提交成功: {commit_message}")
                        return True
                except:
                    pass

                print("⚠️ 提交可能存在问题，请检查编码")
                return True
        except Exception as e:
            print(f"⚠️ 提交失败: {e}")
            return False

    def push_to_remote(self, branch: str = None) -> bool:
        """推送到远程仓库"""
        if branch is None:
            branch = self.branch

        try:
            # 获取当前分支
            if branch is None:
                result = self.run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
                if result.returncode == 0:
                    branch = result.stdout.strip()

            # 推送
            result = self.run_command(['git', 'push', 'origin', branch])
            if result.returncode == 0:
                print(f"✅ 推送到远程成功: {branch}")
                return True
            else:
                print("⚠️ 推送到远程可能存在问题")
                return True
        except Exception as e:
            print(f"⚠️ 推送失败: {e}")
            return False

    def commit_all_changes(self, commit_message: str = None) -> bool:
        """提交所有更改"""
        if commit_message is None:
            commit_message = f"自动提交: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        success = True

        # 尝试提交
        for attempt in range(2):
            try:
                # 检查更改
                result = self.run_command(['git', 'status', '--porcelain'])
                if not result.stdout.strip():
                    print("ℹ️ 没有需要提交的更改")
                    return True

                # 尝试添加并提交
                self.run_command(['git', 'add', '.'])

                # 处理commit message编码
                try:
                    commit_bytes = commit_message.encode('utf-8')
                    result = self.run_command(['git', 'commit', '-m', commit_bytes])
                except UnicodeEncodeError:
                    # 如果UTF-8编码失败，尝试使用escape
                    commit_escaped = commit_message.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
                    result = self.run_command(['git', 'commit', '-m', commit_escaped])

                if result.returncode == 0:
                    print(f"✅ 提交成功: {commit_message}")
                else:
                    print("⚠️ 提交可能有问题，继续尝试推送")

                # 推送
                self.push_to_remote()
                return True

            except UnicodeEncodeError as e:
                if attempt == 0:
                    print(f"⚠️ 编码问题，尝试修复: {e}")
                    # 使用更简单的消息
                    simple_msg = "Auto commit " + datetime.now().strftime('%Y%m%d')
                    self.run_command(['git', 'add', '.'])
                    self.run_command(['git', 'commit', '-m', simple_msg])
                    self.push_to_remote()
                    return True
                else:
                    print(f"❌ 编码问题无法解决: {e}")
                    return False
            except Exception as e:
                if attempt == 0:
                    print(f"⚠️ 第一次尝试失败，重试: {e}")
                    continue
                else:
                    print(f"❌ 提交失败: {e}")
                    return False

def create_auto_sync_script():
    """创建自动同步脚本"""

    # 创建同步脚本
    sync_script = """#!/usr/bin/env python3
"""

    # 读取自动同步代码
    with open('github_auto_sync.py', 'r', encoding='utf-8') as f:
        sync_code = f.read()

    # 写入完整的同步脚本
    with open('auto_sync_complete.py', 'w', encoding='utf-8') as f:
        f.write(sync_code)
        f.write("\n\n")

        # 添加主函数
        f.write("""
def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='美易机器人自动同步工具')
    parser.add_argument('--repo-path', default='.', help='仓库路径')
    parser.add_argument('--remote-url', help='远程仓库URL')
    parser.add_argument('--branch', default='main', help='分支名称')
    parser.add_argument('--message', help='提交信息')
    parser.add_argument('--init', action='store_true', help='初始化仓库')
    parser.add_argument('--add-remote', action='store_true', help='添加远程仓库')
    parser.add_argument('--commit-all', action='store_true', help='提交所有更改')
    parser.add_argument('--push', action='store_true', help='推送到远程')
    parser.add_argument('--create-branch', help='创建并推送新分支')

    args = parser.parse_args()

    # 创建同步工具实例
    sync = GitAutoSync(repo_path=args.repo_path)

    if args.init:
        sync.initialize_repo()

    if args.add_remote and args.remote_url:
        sync.add_remote(args.remote_url)

    if args.create_branch:
        sync.create_and_push_branch(args.create_branch)

    if args.commit_all:
        sync.commit_all_changes(args.message)

    if args.push:
        sync.push_to_remote(args.branch)

if __name__ == '__main__':
    main()
""")

def setup_github_workflow():
    """设置GitHub Actions工作流"""

    # 创建.github/workflows目录
    os.makedirs('.github/workflows', exist_ok=True)

    # 创建工作流文件
    workflow_content = """name: Auto Commit and Push

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    # 每天早上8点自动运行（北京时间）
    - cron: '0 0 8 * * *'

jobs:
  auto-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install python-docx requests

      - name: Run auto commit
        run: |
          python auto_sync_complete.py --commit-all --message "自动更新: $(date)"
        env:
          STREAMLIT_BROWSER_GATHER_USAGE_STATS: false

      - name: Commit and push changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A
          git commit -m "Auto update: $(date)" || exit 0
          git push
"""

    with open('.github/workflows/auto-sync.yml', 'w', encoding='utf-8') as f:
        f.write(workflow_content)

def create_commit_hook():
    """创建Git钩子文件"""
    os.makedirs('.git/hooks', exist_ok=True)

    # 创建pre-commit钩子
    hook_content = """#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from github_auto_sync import GitAutoSync

    # 自动提交更改
    sync = GitAutoSync()

    # 检查是否有更改
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        print("检测到文件更改，自动提交...")
        sync.commit_all_changes("自动提交: Git钩子触发")

except Exception as e:
    print(f"自动提交失败: {e}")
"""

    hook_path = '.git/hooks/pre-commit'
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    # 设置执行权限
    os.chmod(hook_path, 0o755)

def create_batch_script():
    """创建Windows批处理脚本"""

    batch_content = """@echo off
echo 美易机器人自动同步工具
echo =========================

echo 1. 初始化Git仓库
echo 2. 添加远程仓库
echo 3. 提交所有更改
echo 4. 推送到GitHub
echo 5. 创建新分支并推送
echo 6. 设置定时自动同步
echo 7. 完整自动同步
echo 8. 退出

set /p choice=请选择操作 (1-8):

if "%choice%"=="1" goto init
if "%choice%"=="2" goto remote
if "%choice%"=="3" goto commit
if "%choice%"=="4" goto push
if "%choice%"=="5" goto branch
if "%choice%"=="6" goto schedule
if "%choice%"=="7" goto full_sync
if "%choice%"=="8" goto exit

:init
echo 初始化Git仓库...
python auto_sync_complete.py --init
pause
goto menu

:remote
echo 请输入GitHub仓库URL:
set /p url=
python auto_sync_complete.py --add-remote --remote-url "%url%"
pause
goto menu

:commit
echo 提交所有更改...
python auto_sync_complete.py --commit-all --message "自动更新: %date% %time%"
pause
goto menu

:push
echo 推送到GitHub...
python auto_sync_complete.py --push
pause
goto menu

:branch
echo 请输入新分支名称:
set /p branch=
python auto_sync_complete.py --create-branch "%branch%"
pause
goto menu

:schedule
echo 设置Windows计划任务...
echo 请手动创建计划任务，运行:
echo python auto_sync_complete.py --commit-all --message "自动更新: %date%"
pause
goto menu

:full_sync
echo 执行完整自动同步...
python auto_sync_complete.py --init
python auto_sync_complete.py --add-remote --remote-url "请替换为您的GitHub仓库URL"
python auto_sync_complete.py --commit-all --message "初始提交: 美易机器人系统"
python auto_sync_complete.py --push
echo 自动同步完成！
pause
goto menu

:exit
exit

:menu
call "%~f0"
"""

    with open('auto_sync.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)

def main():
    """主函数"""
    print("🚀 设置美易机器人GitHub自动同步...")

    try:
        # 创建自动同步脚本
        create_auto_sync_script()
        print("✅ 自动同步脚本创建成功")

        # 设置GitHub Actions工作流
        setup_github_workflow()
        print("✅ GitHub Actions工作流设置成功")

        # 创建Git钩子
        create_commit_hook()
        print("✅ Git钩子创建成功")

        # 创建Windows批处理脚本
        create_batch_script()
        print("✅ Windows批处理脚本创建成功")

        print("\n🎉 设置完成！")
        print("\n使用说明:")
        print("1. 首次使用运行: python auto_sync_complete.py --init")
        print("2. 添加远程仓库: python auto_sync_complete.py --add-remote --remote-url 'https://github.com/your-username/meiyi-bot.git'")
        print("3. 提交更改: python auto_sync_complete.py --commit-all")
        print("4. 推送到GitHub: python auto_sync_complete.py --push")
        print("\n或者直接运行批处理文件: auto_sync.bat")

    except Exception as e:
        print(f"❌ 设置失败: {e}")

if __name__ == "__main__":
    main()