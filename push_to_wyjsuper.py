#!/usr/bin/env python3
"""
一键推送到wyjsuper的GitHub仓库
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

def main():
    print("🚀 美易机器人推送到 wyjsuper 的 GitHub")
    print("=" * 50)

    # 检查Git状态
    print("📁 检查代码状态...")
    result = run_cmd(['git', 'status', '--porcelain'])

    if result is None or result.returncode != 0:
        print("❌ Git状态检查失败")
        return

    has_changes = bool(result.stdout.strip())

    if not has_changes:
        print("✅ 没有需要提交的更改")
        # 仍然尝试推送，可能有未推送的提交
        goto_push()
        return

    print("📋 发现以下更改:")
    print(result.stdout)
    print()

    # 确认提交
    confirm = input("是否提交这些更改？(Y/N): ").upper()
    if confirm != 'Y':
        print("取消提交")
        return

    # 提交
    print("\n🔄 正在提交...")
    run_cmd(['git', 'add', '.'])

    # 尝试提交
    commit_msg = f"自动更新 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    result = run_cmd(['git', 'commit', '-m', commit_msg])

    if result and result.returncode == 0:
        print("✅ 提交成功")
    else:
        print("⚠️ 提交可能有问题，但继续推送")

    # 推送到GitHub
    goto_push()

def goto_push():
    """推送到GitHub"""
    print("\n🚀 推送到GitHub...")

    # 获取当前分支
    branch_result = run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if branch_result and branch_result.returncode == 0:
        branch = branch_result.stdout.strip()
        print(f"当前分支: {branch}")
    else:
        branch = 'main'
        print(f"使用默认分支: {branch}")

    # 推送
    push_result = run_cmd(['git', 'push', 'origin', branch])

    if push_result and push_result.returncode == 0:
        print("\n🎉 推送成功！")
        print("\n✅ 代码已同步到 https://github.com/wyjsuper/meiyi-bot")
    else:
        print("\n⚠️ 推送失败")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 确认已创建GitHub仓库: https://github.com/wyjsuper/meiyi-bot")
        print("3. 配置GitHub认证:")
        print("   - 使用HTTPS: 在GitHub设置中生成Personal Access Token")
        print("   - 使用SSH: 配置SSH密钥")
        print("\n首次使用命令:")
        print("git remote add origin https://github.com/wyjsuper/meiyi-bot.git")
        print("git push -u origin main")

if __name__ == "__main__":
    main()