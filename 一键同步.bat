@echo off
chcp 65001 >nul
echo ========================================
echo      美易机器人GitHub一键同步工具
echo ========================================
echo.

:: 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装，请先安装Git for Windows
    echo 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git已安装
echo.

:: 检查是否有未提交的更改
echo 🔍 检查代码状态...
git status --porcelain >nul 2>&1
if errorlevel 1 (
    echo ❌ 当前目录不是Git仓库或Git配置有问题
    pause
    exit /b 1
)

git status --porcelain > temp_status.txt
findstr /c:" M " temp_status.txt >nul
findstr /c:"??" temp_status.txt >nul

if errorlevel 1 (
    echo ✅ 没有需要提交的更改
    echo.
    goto push_only
)

echo 📁 检测到以下更改:
type temp_status.txt
echo.

:confirm_commit
set /p confirm=确认要提交这些更改吗？(Y/N):
if /i "%confirm%"=="Y" goto do_commit
if /i "%confirm%"=="N" goto push_only
echo 请输入Y或N
goto confirm_commit

:do_commit
echo.
echo 🔄 正在提交代码...
echo 提交消息：自动更新 %date% %time%

:: 尝试提交
git add .
if errorlevel 1 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)

:: 尝试使用简短消息提交
git commit -m "Auto update %date:~0,4%%date:~5,2%%date:~8,2%"
if errorlevel 1 (
    echo ⚠️ 提交可能有问题，但继续推送
) else (
    echo ✅ 提交成功
)
del temp_status.txt
echo.

:push_only
echo 🚀 正在推送到GitHub...
git push
if errorlevel 1 (
    echo ⚠️ 推送失败，请检查：
    echo 1. 是否已添加远程仓库
    echo 2. 网络是否正常
    echo 3. GitHub认证是否正确
    echo.
    echo 如果是首次推送，请先执行：
    echo python auto_commit_push.py add-remote https://github.com/您的用户名/meiyi-bot.git
) else (
    echo ✅ 推送成功！
)

echo.
echo ========================================
echo 同步完成！
echo ========================================
pause