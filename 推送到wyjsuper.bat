@echo off
chcp 65001 >nul
title 美易机器人推送到 wyjsuper 的 GitHub

echo ========================================
echo     美易机器人推送到 wyjsuper 的 GitHub
echo ========================================
echo.

:: 检查Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git已安装
echo.

:: 检查状态
echo 🔍 检查代码状态...
git status --porcelain > temp_status.txt

findstr /c:" M " temp_status.txt >nul
findstr /c:"??" temp_status.txt >nul

if errorlevel 1 (
    echo ✅ 没有需要提交的更改
    goto push_code
) else (
    echo 📁 发现以下更改:
    type temp_status.txt
    echo.

    set /p confirm=是否提交这些更改？(Y/N):
    if /i not "%confirm%"=="Y" goto push_code

    echo.
    echo 🔄 正在提交...
    git add .

    :: 尝试提交
    git commit -m "自动更新 %date% %time%"
    if errorlevel 1 (
        echo ⚠️ 提交可能有问题，但继续推送
    ) else (
        echo ✅ 提交成功
    )
)

:push_code
echo.
echo 🚀 推送到GitHub...
echo GitHub仓库: https://github.com/wyjsuper/meiyi-bot

:: 检查是否有远程仓库
git remote -v >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到远程仓库，请先添加:
    echo git remote add origin https://github.com/wyjsuper/meiyi-bot.git
    pause
    exit /b 1
)

:: 推送
git push
if errorlevel 1 (
    echo.
    echo ❌ 推送失败！请检查:
    echo 1. 是否已创建GitHub仓库: https://github.com/wyjsuper/meiyi-bot
    echo 2. 网络连接是否正常
    echo 3. GitHub认证是否配置正确
    echo.
    echo 认证方法:
    echo a. HTTPS: 在GitHub设置生成Personal Access Token
    echo b. SSH: 配置SSH密钥到GitHub
    echo.
    echo 首次设置命令:
    echo git remote add origin https://github.com/wyjsuper/meiyi-bot.git
    echo git push -u origin main
) else (
    echo.
    echo 🎉 推送成功！
    echo 📍 仓库地址: https://github.com/wyjsuper/meiyi-bot
)

:: 清理
del temp_status.txt 2>nul

echo.
pause