#!/bin/bash

echo "🤖 美易机器人 - 启动脚本"
echo "========================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python，请先安装Python 3.7+"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"
echo ""

# 检查streamlit是否安装
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 正在安装依赖包..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 启动应用..."
streamlit run app.py --server.port 8501
