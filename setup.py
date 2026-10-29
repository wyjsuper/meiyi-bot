#!/usr/bin/env python3
"""
美易机器人初始化脚本
安装依赖、下载模型、创建必要的目录结构
"""

import os
import sys
import subprocess


def print_section(title):
    """打印分节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def check_python():
    """检查Python版本"""
    print_section("1. 检查Python环境")

    version = sys.version
    print(f"Python版本: {version}")

    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        sys.exit(1)

    print("✓ Python环境正常")


def install_dependencies():
    """安装Python依赖"""
    print_section("2. 安装Python依赖")

    requirements_file = "requirements.txt"

    if not os.path.exists(requirements_file):
        print(f"❌ 错误: 未找到 {requirements_file}")
        return False

    try:
        print("正在安装依赖包...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def install_embedding_model():
    """安装sentence-transformers模型"""
    print_section("3. 下载embedding模型")

    try:
        from sentence_transformers import SentenceTransformer

        model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
        print(f"正在下载模型: {model_name}")
        print("这可能需要几分钟时间...")

        model = SentenceTransformer(model_name)

        print("✓ 模型下载完成")
        return True

    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        print("提示: 可以在后续使用时手动安装: pip install sentence-transformers")
        return False


def check_ollama():
    """检查Ollama服务"""
    print_section("4. 检查Ollama服务")

    try:
        import ollama

        models = ollama.list()
        print("✓ Ollama服务正在运行")

        # 检查是否已安装glm4-flash
        model_names = [model.get('name', '') for model in models.get('models', [])]

        if 'glm4-flash' in model_names:
            print("✓ GLM-4.7 Flash模型已安装")
        else:
            print("⚠️  GLM-4.7 Flash模型未安装")
            print("正在下载模型...")
            try:
                subprocess.check_call(["ollama", "pull", "glm4-flash"])
                print("✓ 模型下载完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ 模型下载失败: {e}")
                print("请手动安装: ollama pull glm4-flash")
                return False

        return True

    except Exception as e:
        print(f"❌ 无法连接到Ollama服务: {e}")
        print("\n请确保Ollama正在运行:")
        print("  1. 下载并安装Ollama: https://ollama.ai")
        print("  2. 运行 ollama serve 启动服务")
        print("  3. 下载模型: ollama pull glm4-flash")
        return False


def create_directories():
    """创建必要的目录"""
    print_section("5. 创建目录结构")

    directories = [
        "data",
        "data/chroma_db",
        "data/knowledge_base"
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ 创建目录: {directory}")
        except Exception as e:
            print(f"❌ 创建目录失败 {directory}: {e}")
            return False

    return True


def test_system():
    """测试系统组件"""
    print_section("6. 测试系统组件")

    all_passed = True

    # 测试Excel解析器
    try:
        from utils.document_parser import ExcelParser
        print("✓ Excel解析器导入成功")
    except Exception as e:
        print(f"❌ Excel解析器导入失败: {e}")
        all_passed = False

    # 测试向量存储
    try:
        from utils.vector_store import VectorStore
        print("✓ 向量存储模块导入成功")
    except Exception as e:
        print(f"❌ 向量存储模块导入失败: {e}")
        all_passed = False

    # 测试LLM客户端
    try:
        from utils.llm_client import GLM4Client
        print("✓ LLM客户端模块导入成功")
    except Exception as e:
        print(f"❌ LLM客户端模块导入失败: {e}")
        all_passed = False

    return all_passed


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  🤖 美易机器人 - 系统初始化")
    print("=" * 60)

    try:
        # 1. 检查Python
        check_python()

        # 2. 安装依赖
        if not install_dependencies():
            sys.exit(1)

        # 3. 创建目录
        if not create_directories():
            sys.exit(1)

        # 4. 下载embedding模型
        install_embedding_model()

        # 5. 检查Ollama
        if not check_ollama():
            print("\n⚠️  警告: Ollama服务未正确配置，请按照提示配置后重新运行")
            sys.exit(1)

        # 6. 测试系统
        if not test_system():
            print("\n⚠️  警告: 部分组件测试失败，请检查错误信息")

        # 完成
        print_section("初始化完成")
        print("\n✓ 美易机器人已准备就绪!")
        print("\n启动命令:")
        print("  streamlit run app.py")
        print("\n访问地址: http://localhost:8501")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
