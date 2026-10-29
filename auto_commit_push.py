#!/usr/bin/env python3
"""
美易机器人自动提交和推送工具
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """运行Git命令"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result
    except Exception as e:
        print(f"命令执行失败: {e}")
        return None

def check_git_status():
    """检查Git状态"""
    result = run_command(['git', 'status', '--porcelain'])
    if result and result.stdout.strip():
        print("📁 检测到以下更改:")
        print(result.stdout)
        return True
    else:
        print("✅ 没有需要提交的更改")
        return False

def auto_commit(message=None):
    """自动提交"""
    if message is None:
        message = f"自动更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print(f"🔄 提交消息: {message}")

    # 添加所有文件
    result = run_command(['git', 'add', '.'])
    if result is None or result.returncode != 0:
        print("❌ 添加文件失败")
        return False

    # 提交
    try:
        # 尝试直接提交
        result = run_command(['git', 'commit', '-m', message])
        if result and result.returncode == 0:
            print("✅ 提交成功")
            return True
        else:
            print("⚠️ 直接提交可能有问题，尝试修复编码...")

            # 使用简短的提交消息
            short_message = f"Auto update {datetime.now().strftime('%Y%m%d')}"
            result = run_command(['git', 'commit', '-m', short_message])
            if result and result.returncode == 0:
                print("✅ 使用简短消息提交成功")
                return True
            else:
                print("❌ 提交失败")
                return False
    except UnicodeEncodeError:
        # 处理编码错误
        short_message = f"Auto update {datetime.now().strftime('%Y%m%d')}"
        result = run_command(['git', 'commit', '-m', short_message])
        if result and result.returncode == 0:
            print("✅ 修复编码后提交成功")
            return True
        else:
            print("❌ 编码修复后仍提交失败")
            return False

def push_to_github():
    """推送到GitHub"""
    print("🚀 推送到GitHub...")

    # 获取当前分支
    result = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if result and result.returncode == 0:
        branch = result.stdout.strip()
        print(f"当前分支: {branch}")

        # 推送
        result = run_command(['git', 'push', 'origin', branch])
        if result and result.returncode == 0:
            print("✅ 推送成功")
            return True
        else:
            print("⚠️ 推送可能有问题，但继续执行")
            return True
    else:
        print("❌ 获取分支失败")
        return False

def init_git_repo():
    """初始化Git仓库"""
    print("🔧 初始化Git仓库...")

    # 检查是否已初始化
    if os.path.exists('.git'):
        print("✅ Git仓库已存在")
        return True

    # 初始化
    result = run_command(['git', 'init'])
    if result and result.returncode == 0:
        print("✅ Git仓库初始化成功")

        # 配置用户
        run_command(['git', 'config', 'user.name', '美纳里尼IT'])
        run_command(['git', 'config', 'user.email', 'it.menarini@menarini.com'])

        # 首次提交
        run_command(['git', 'add', '.'])
        run_command(['git', 'commit', '-m', 'Initial commit: 美易机器人在线答疑系统'])

        return True
    else:
        print("❌ Git仓库初始化失败")
        return False

def add_remote(remote_url):
    """添加远程仓库"""
    print(f"🔗 添加远程仓库: {remote_url}")

    result = run_command(['git', 'remote', 'add', 'origin', remote_url])
    if result and result.returncode == 0:
        print("✅ 远程仓库添加成功")
        return True
    else:
        print("⚠️ 远程仓库可能已存在或添加失败")
        return True

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = 'commit-push'

    print("🤖 美易机器人自动同步工具")
    print("=" * 40)

    if command == 'init':
        init_git_repo()
    elif command == 'add-remote':
        if len(sys.argv) > 2:
            remote_url = sys.argv[2]
            add_remote(remote_url)
        else:
            print("❌ 请提供远程仓库URL")
            print("用法: python auto_commit_push.py add-remote <URL>")
    elif command == 'commit':
        if check_git_status():
            auto_commit()
    elif command == 'push':
        push_to_github()
    elif command == 'commit-push':
        if check_git_status():
            if auto_commit():
                push_to_github()
    elif command == 'status':
        check_git_status()
    else:
        print("可用命令:")
        print("  init              - 初始化Git仓库")
        print("  add-remote <URL>  - 添加远程仓库")
        print("  commit            - 提交更改")
        print("  push              - 推送到GitHub")
        print("  commit-push       - 提交并推送（默认）")
        print("  status            - 查看状态")

if __name__ == "__main__":
    main()