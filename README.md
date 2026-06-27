# ImAge - Image Exhibition Website

一个基于 Flask 的图片展览网站，支持图片上传、展览创建、阿里云 OSS 存储。

## 功能

- 🔐 用户注册/登录（密码加密）
- 👤 个人主页（头像上传、简介编辑）
- 📸 图片上传（拖拽上传、多文件上传，10GB 总容量限制）
- 🖼️ 社区画廊（分页浏览）
- 🎨 展览系统（创建展览、添加图片、拖拽排序）
- 📺 幻灯片查看器（键盘方向键控制）
- ☁️ 阿里云 OSS 云存储支持
- 🌙 暗色主题

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行
python3 run.py

# 3. 打开浏览器访问
# http://localhost:5001
```

## 配置阿里云 OSS（可选）

```bash
# 编辑 set_oss_env.sh 填入你的配置，然后运行：
source set_oss_env.sh
python3 run.py
```

## 部署到云平台

### ❌ Cloudflare Pages（不支持）
Cloudflare Pages 只支持**静态网站**，不能运行 Python/Flask。

### ✅ 推荐：Render.com（免费）
1. 在 https://render.com 注册账号（GitHub 登录）
2. 点击 "New +" → "Web Service"
3. 连接 GitHub 仓库 `HarryCQ/ImAge`
4. 填写配置：
   - **Name**: `image`
   - **Region**: 选 Singapore（亚洲速度最快）
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:10000 run:app`
   - **Instance Type**: Free
5. 在 "Environment" 中添加环境变量（如果需要 OSS）
6. 点击 "Create Web Service"

### ✅ 备选：Railway.app
1. 在 https://railway.app 注册
2. "New Project" → "Deploy from GitHub repo"
3. 选择 `HarryCQ/ImAge`
4. 设置 Start Command: `gunicorn -w 4 -b 0.0.0.0:8000 run:app`
5. 部署完成

### ✅ 备选：Fly.io
1. 安装 flyctl: `brew install flyctl`
2. 登录: `fly auth login`
3. 部署: `fly launch`
