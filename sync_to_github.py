#!/usr/bin/env python3
"""
美易机器人同步到个人GitHub仓库
用户: wyjsuper
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

def init_repo():
    """初始化Git仓库"""
    print("🔧 初始化Git仓库...")

    if os.path.exists('.git'):
        print("✅ Git仓库已存在")
        return True

    result = run_command(['git', 'init'])
    if result and result.returncode == 0:
        print("✅ Git仓库初始化成功")

        # 配置用户
        run_command(['git', 'config', 'user.name', 'wyjsuper'])
        run_command(['git', 'config', 'user.email', 'wyjsuper@example.com'])

        # 首次提交
        run_command(['git', 'add', '.'])
        run_command(['git', 'commit', '-m', 'Initial commit: 美易机器人在线答疑系统'])

        return True
    else:
        print("❌ Git仓库初始化失败")
        return False

def add_wyjsuper_remote():
    """添加wyjsuper的远程仓库"""
    repo_urls = [
        "https://github.com/wyjsuper/meiyi-bot.git",
        "git@github.com:wyjsuper/meiyi-bot.git"
    ]

    for url in repo_urls:
        print(f"🔗 尝试添加远程仓库: {url}")
        result = run_command(['git', 'remote', 'add', 'origin', url])
        if result and result.returncode == 0:
            print("✅ 远程仓库添加成功")
            return True
        elif result and 'already exists' in result.stderr:
            print("⚠️ 远程仓库已存在")

            # 尝试推送
            print("🚀 尝试推送到现有仓库...")
            result = run_command(['git', 'push', 'origin', 'main'])
            if result and result.returncode == 0:
                print("✅ 推送成功")
                return True
            else:
                print("⚠️ 推送失败，可能需要认证")
                return True

    print("❌ 无法添加远程仓库，请手动创建GitHub仓库")
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

    # 尝试提交
    try:
        result = run_command(['git', 'commit', '-m', message])
        if result and result.returncode == 0:
            print("✅ 提交成功")
            return True
        else:
            print("⚠️ 直接提交可能有问题")

            # 使用简短消息重试
            short_msg = f"Auto update {datetime.now().strftime('%Y%m%d')}"
            result = run_command(['git', 'commit', '-m', short_msg])
            if result and result.returncode == 0:
                print("✅ 使用简短消息提交成功")
                return True
            else:
                print("❌ 提交失败")
                return False
    except UnicodeEncodeError:
        short_msg = f"Auto update {datetime.now().strftime('%Y%m%d')}"
        result = run_command(['git', 'commit', '-m', short_msg])
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

        # 尝试推送
        result = run_command(['git', 'push', 'origin', branch])
        if result and result.returncode == 0:
            print("✅ 推送成功")
            return True
        else:
            print("⚠️ 推送失败，可能需要以下操作：")
            print("1. 检查网络连接")
            print("2. 确认GitHub认证")
            print("3. 检查远程仓库是否存在")
            return False
    else:
        print("❌ 获取分支失败")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = 'full-sync'

    print("🤖 美易机器人同步到 wyjsuper 的 GitHub")
    print("=" * 50)

    if command == 'init':
        init_repo()
    elif command == 'add-remote':
        add_wyjsuper_remote()
    elif command == 'commit':
        if check_git_status():
            auto_commit()
    elif command == 'push':
        push_to_github()
    elif command == 'full-sync':
        print("🔄 开始完整同步...")
        init_repo()
        add_wyjsuper_remote()
        if check_git_status():
            auto_commit()
            push_to_github()
    elif command == 'status':
        check_git_status()
    else:
        print("可用命令:")
        print("  init              - 初始化Git仓库")
        print("  add-remote        - 添加wyjsuper的远程仓库")
        print("  commit            - 提交更改")
        print("  push              - 推送到GitHub")
        print("  full-sync         - 完整同步（默认）")
        print("  status            - 查看状态")

if __name__ == "__main__":
    main()