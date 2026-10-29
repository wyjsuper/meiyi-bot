@echo off
echo 启动美易在线答疑系统...
echo ==========================

REM 设置环境变量
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_SERVER_ADDRESS=0.0.0.0
set STREAMLIT_SERVER_PORT=8501

REM 启动应用
echo 正在启动应用...
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

echo.
echo 应用已停止