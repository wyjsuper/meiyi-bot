#!/usr/bin/env python3
"""
测试GitHub同步功能
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

def test_git_setup():
    """测试Git基本设置"""
    print("🔧 测试Git基本设置...")

    # 检查Git是否安装
    result = run_command(['git', '--version'])
    if result and result.returncode == 0:
        print("✅ Git已安装")
        print(f"版本: {result.stdout.strip()}")
    else:
        print("❌ Git未安装")
        return False

    # 检查是否在Git仓库
    if os.path.exists('.git'):
        print("✅ 当前目录是Git仓库")
    else:
        print("⚠️ 当前目录不是Git仓库，需要初始化")
        return False

    # 检查用户配置
    result = run_command(['git', 'config', 'user.name'])
    if result and result.returncode == 0:
        print(f"✅ Git用户名: {result.stdout.strip()}")
    else:
        print("⚠️ 未配置Git用户名")

    result = run_command(['git', 'config', 'user.email'])
    if result and result.returncode == 0:
        print(f"✅ Git邮箱: {result.stdout.strip()}")
    else:
        print("⚠️ 未配置Git邮箱")

    return True

def test_remote_repo():
    """测试远程仓库"""
    print("\n🔗 测试远程仓库...")

    result = run_command(['git', 'remote', '-v'])
    if result and result.returncode == 0:
        print("✅ 远程仓库配置:")
        print(result.stdout)

        # 检查是否包含wyjsuper
        if 'wyjsuper' in result.stdout:
            print("✅ 找到wyjsuper的仓库")
            return True
        else:
            print("⚠️ 未找到wyjsuper的仓库")
            print("建议添加: https://github.com/wyjsuper/meiyi-bot.git")
            return False
    else:
        print("❌ 未配置远程仓库")
        return False

def test_git_status():
    """测试Git状态"""
    print("\n📁 测试Git状态...")

    result = run_command(['git', 'status', '--porcelain'])
    if result and result.returncode == 0:
        if result.stdout.strip():
            print("📋 发现未提交的更改:")
            print(result.stdout)
            return True
        else:
            print("✅ 没有未提交的更改")
            return True
    else:
        print("❌ 无法获取Git状态")
        return False

def test_push_ability():
    """测试推送能力"""
    print("\n🚀 测试推送能力...")

    # 获取当前分支
    result = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if result and result.returncode == 0:
        branch = result.stdout.strip()
        print(f"当前分支: {branch}")

        # 检查远程分支是否存在
        result = run_command(['git', 'ls-remote', '--heads', 'origin', branch])
        if result and result.returncode == 0:
            if result.stdout.strip():
                print(f"✅ 远程分支 {branch} 存在")
                return True
            else:
                print(f"⚠️ 远程分支 {branch} 不存在")
                return False
        else:
            print(f"❌ 无法检查远程分支 {branch}")
            return False
    else:
        print("❌ 无法获取当前分支")
        return False

def test_file_changes():
    """创建测试文件更改"""
    print("\n📝 创建测试文件...")

    # 创建测试文件
    test_content = f"""# 测试文件
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
这是一个测试文件，用于验证GitHub同步功能。

包含的内容：
- 测试提交
- 验证同步
- 检查功能

作者: wyjsuper
"""

    with open('test_github_sync.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)

    print("✅ 创建测试文件: test_github_sync.txt")
    return True

def main():
    """主函数"""
    print("🧪 测试GitHub同步功能")
    print("=" * 50)

    tests = [
        ("Git基本设置", test_git_setup),
        ("远程仓库配置", test_remote_repo),
        ("Git状态检查", test_git_status),
        ("推送能力测试", test_push_ability),
    ]

    results = {}

    for name, test_func in tests:
        print(f"\n{'-' * 20}")
        print(f"测试: {name}")
        print(f"{'-' * 20}")
        results[name] = test_func()

    # 创建测试文件
    test_file = test_file_changes()

    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)

    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print(f"\n测试文件: {'✅ 已创建' if test_file else '❌ 创建失败'}")

    if all_passed:
        print("\n🎉 所有测试通过！可以开始同步。")
        print("\n推荐操作:")
        print("1. 运行: python push_to_wyjsuper.py")
        print("2. 或者双击: 推送到wyjsuper.bat")
    else:
        print("\n⚠️ 部分测试失败，请先解决问题。")
        print("\n需要解决的问题:")
        for name, passed in results.items():
            if not passed:
                print(f"- {name}")

        print("\n参考文档: SETUP_GUIDE.md")

if __name__ == "__main__":
    main()