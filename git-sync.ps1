# 美易机器人Git同步脚本
# PowerShell版本

param(
    [string]$Command = "commit-push",
    [string]$RemoteUrl,
    [string]$Message = "自动更新: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Test-GitInstalled {
    try {
        git --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Initialize-GitRepo {
    Write-Log "初始化Git仓库..."

    if (Test-Path ".git") {
        Write-Log "Git仓库已存在"
        return $true
    }

    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ Git仓库初始化失败"
        return $false
    }

    # 配置Git用户
    git config user.name "美纳里尼IT"
    git config user.email "it.menarini@menarini.com"

    # 首次提交
    git add .
    git commit -m "Initial commit: 美易机器人在线答疑系统"

    Write-Log "✅ Git仓库初始化成功"
    return $true
}

function Add-GitRemote {
    param([string]$Url)

    if (-not $Url) {
        Write-Log "❌ 请提供远程仓库URL"
        return $false
    }

    Write-Log "添加远程仓库: $Url"

    git remote add origin $Url
    if ($LASTEXITCODE -ne 0) {
        if ($LASTEXITCODE -eq 128) {
            Write-Log "⚠️ 远程仓库已存在"
        } else {
            Write-Log "❌ 添加远程仓库失败"
            return $false
        }
    } else {
        Write-Log "✅ 远程仓库添加成功"
    }

    return $true
}

function Get-GitStatus {
    $status = git status --porcelain
    if ($status) {
        Write-Log "📁 检测到以下更改:"
        $status | ForEach-Object { Write-Log "  $_" }
        return $true
    } else {
        Write-Log "✅ 没有需要提交的更改"
        return $false
    }
}

function Commit-GitChanges {
    param([string]$Message)

    if (-not $Message) {
        $Message = "自动更新: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }

    Write-Log "🔄 提交消息: $Message"

    # 尝试使用UTF-8编码提交
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Message)
        $encodedMessage = [System.Text.Encoding]::UTF8.GetString($bytes)
        git add .
        git commit -m $encodedMessage
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ 提交成功"
            return $true
        }
    }
    catch {
        Write-Log "⚠️ 直接提交失败，尝试使用简短消息..."
    }

    # 使用简短消息重试
    $shortMessage = "Auto update $(Get-Date -Format 'yyyyMMdd')"
    git add .
    git commit -m $shortMessage
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ 使用简短消息提交成功"
        return $true
    } else {
        Write-Log "❌ 提交失败"
        return $false
    }
}

function Push-ToGitHub {
    Write-Log "🚀 推送到GitHub..."

    # 获取当前分支
    $branch = git rev-parse --abbrev-ref HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Log "❌ 获取分支失败"
        return $false
    }

    Write-Log "当前分支: $branch"

    # 推送
    git push origin $branch
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ 推送成功"
        return $true
    } else {
        Write-Log "⚠️ 推送可能有问题，但继续执行"
        return $true
    }
}

function Show-Help {
    Write-Host "美易机器人Git同步工具 - PowerShell版本"
    Write-Host "使用方法:"
    Write-Host "  .\git-sync.ps1 [命令] [参数]"
    Write-Host ""
    Write-Host "可用命令:"
    Write-Host "  init              - 初始化Git仓库"
    Write-Host "  add-remote <URL>  - 添加远程仓库"
    Write-Host "  commit [消息]     - 提交更改"
    Write-Host "  push              - 推送到GitHub"
    Write-Host "  commit-push [消息] - 提交并推送（默认）"
    Write-Host "  status            - 查看状态"
}

# 主程序
Write-Log "🤖 美易机器人自动同步工具"
Write-Log "=" * 40

# 检查Git是否安装
if (-not (Test-GitInstalled)) {
    Write-Log "❌ Git未安装，请先安装Git"
    exit 1
}

# 根据命令执行相应操作
switch ($Command.ToLower()) {
    "init" {
        Initialize-GitRepo
    }
    "add-remote" {
        Add-GitRemote -Url $RemoteUrl
    }
    "commit" {
        if (Get-GitStatus) {
            Commit-GitChanges -Message $Message
        }
    }
    "push" {
        Push-ToGitHub
    }
    "commit-push" {
        if (Get-GitStatus) {
            if (Commit-GitChanges -Message $Message) {
                Push-ToGitHub
            }
        }
    }
    "status" {
        Get-GitStatus
    }
    "help" {
        Show-Help
    }
    default {
        Write-Log "❌ 未知命令: $Command"
        Show-Help
    }
}