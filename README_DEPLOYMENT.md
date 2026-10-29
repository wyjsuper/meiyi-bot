# 美易机器人外网部署指南

本指南说明如何将美易机器人部署到外网，让任何人都可以访问。

## 🚀 部署方案对比

### 方案1：Streamlit Cloud（推荐）
- ✅ 免费
- ✅ 无需服务器
- ✅ 自动部署
- ✅ HTTPS支持
- ✅ 全球访问
- ❌ 需要GitHub仓库
- ❌ 有使用限制

### 方案2：PythonAnywhere
- ✅ 免费版可用
- ✅ 支持自定义域名
- ✅ 定时任务支持
- ❌ 需要注册
- ❌ 免费版有广告

### 方案3：Heroku
- ✅ 免费额度
- ✅ Docker支持
- ❌ 需要配置
- ❌ 2023年起停止免费服务

### 方案4：Render
- ✅ 免费额度
- ✅ GitHub集成
- ✅ 自动构建部署
- ❌ 需要配置Web服务

## 🌟 Streamlit Cloud 部署（推荐）

### 步骤1：准备代码
```bash
# 1. 确保已创建GitHub仓库
# 仓库地址：https://github.com/wyjsuper/meiyi-bot

# 2. 上传代码到GitHub
cd "C:\Users\jj\meiyi-bot"
git add .
git commit -m "Add cloud deployment files"
git push origin master
```

### 步骤2：部署到Streamlit Cloud
1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 点击 "Sign up" 或 "Login"
3. 点击 "New app"
4. 选择 "GitHub"
5. 选择您的仓库 `wyjsuper/meiyi-bot`
6. 选择主分支和 `app_cloud.py` 文件
7. 点击 "Deploy!"

### 步骤3：访问应用
部署成功后，您将获得一个类似这样的URL：
```
https://your-name-meiyi-bot.streamlit.app
```

## 🔧 PythonAnywhere 部署

### 步骤1：注册账户
1. 访问 [PythonAnywhere](https://www.pythonanywhere.com/)
2. 点击 "Sign up"
3. 使用邮箱注册免费账户

### 步骤2：上传代码
1. 登录后，点击 "Files"
2. 点击 "Upload a file"
3. 上传 `app_cloud.py` 文件
4. 创建 `requirements.txt` 文件并上传

### 步骤3：配置Web应用
1. 点击 "Web"
2. 点击 "Add a new web app"
3. 选择 "Python Flask"
4. 选择Python版本（推荐3.8或3.9）
5. 点击 "Next"

### 步骤4：配置代码
1. 在 "Source code" 中选择 `/home/yourusername/meiyi_bot/app_cloud.py`
2. 在 "WSGI configuration file" 中点击 "Enter configuration here"
3. 修改为：

```python
import sys

# Add your project directory to the Python path
sys.path.append('/home/yourusername/meiyi_bot')

# Import your app
from app_cloud import app as application

application.debug = True
```

### 步骤5：安装依赖
1. 点击 "Console" > "Bash"
2. 运行：
```bash
pip install streamlit python-docx requests
```

## 🐳 Docker 部署

### 步骤1：创建Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app_cloud.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 步骤2：构建和运行
```bash
# 构建镜像
docker build -t meiyi-bot .

# 运行容器
docker run -p 8501:8501 meiyi-bot
```

## 🌐 使用Nginx反向代理

### 步骤1：安装Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 步骤2：配置Nginx
创建 `/etc/nginx/sites-available/meiyi-bot`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 步骤3：启用配置
```bash
sudo ln -s /etc/nginx/sites-available/meiyi-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 安全配置

### 1. 防火墙设置
```bash
# 只开放必要端口
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 22    # SSH
sudo ufw enable
```

### 2. HTTPS配置（推荐）
使用Let's Encrypt：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 监控和日志

### Streamlit Cloud监控
- 在Streamlit Cloud控制台查看应用状态
- 查看访问日志和错误

### PythonAnywhere日志
- 在Web应用页面查看访问日志
- 使用Bash查看应用日志

### 自定义监控
```python
# 在应用中添加监控
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 在关键位置记录日志
logging.info(f"User query: {prompt}")
logging.info(f"Search results: {len(results)}")
```

## 🔄 更新部署

### Streamlit Cloud更新
1. 修改代码并推送到GitHub
2. Streamlit Cloud会自动检测更新
3. 或者在控制台手动重新部署

### PythonAnywhere更新
1. 更新代码文件
2. 重启Web应用

## 🎉 部署完成！

无论选择哪种方案，部署成功后：

1. 访问应用URL
2. 测试基本功能
3. 分享给团队成员
4. 设置监控和日志

**推荐方案**：Streamlit Cloud + GitHub，简单易用且免费！