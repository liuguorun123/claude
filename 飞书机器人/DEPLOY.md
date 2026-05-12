# 飞书机器人 Render 部署指南

## 快速部署

### 1. 准备 GitHub 仓库

```bash
cd C:\Users\lenovo\Desktop\agent
git init
git add .
git commit -m "飞书机器人"
git remote add origin https://github.com/你的用户名/agent.git
git push -u origin main
```

### 2. 在 Render 创建服务

1. 访问 [render.com](https://render.com) 并注册/登录
2. 点击 **New +** → **Web Service**
3. 连接你的 GitHub 仓库
4. 配置：
   - **Name**: feishu-bot
   - **Runtime**: Python
   - **Build Command**: `pip install -r 飞书机器人/requirements.txt`
   - **Start Command**: `cd 飞书机器人 && python ws_client_v4.py`

### 3. 添加持久化存储

在 Render 服务的 **Disks** 选项卡中：
- **Name**: data
- **Mount Path**: /data
- **Size**: 1 GB (免费额度)

### 4. 设置环境变量

在 **Environment** 选项卡中添加：

| Key | Value |
|-----|-------|
| `CLAUDE_API_KEY` | `tp-c9k8raekucbxv5hp3fxxk8t19stqmbyuqmvmiw17yr48eaih` |
| `CLAUDE_BASE_URL` | `https://token-plan-cn.xiaomimimo.com/anthropic` |
| `FEISHU_APP_ID` | `cli_aa8b6d69b4f95bec` |
| `FEISHU_APP_SECRET` | `1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh` |
| `FEISHU_CHAT_ID` | `oc_c0a8434e665e3fe113a4e82de30959c0` |
| `STORAGE_PATH` | `/data` |

### 5. 部署

点击 **Create Service**，Render 会自动部署。

---

## 存储结构

部署后，日报文件会存储在：

```
/data/
└── 日报/
    ├── 2026-05-12/
    │   ├── 新闻简报.md
    │   ├── 天气建议.md
    │   └── 工作计划.md
    ├── 2026-05-13/
    │   └── ...
    └── ...
```

## 使用方式

### 在飞书中使用

- @助手 发送 "获取新闻" → 自动生成新闻简报
- @助手 发送 "写日报" → 自动生成工作日报
- @助手 发送 "查看今天的日报" → 读取并展示日报内容

### 查看存储的日报

在 Render 控制台：
1. 进入你的服务
2. 点击 **Shell** 选项卡
3. 运行 `ls /data/日报/` 查看所有日报

---

## 本地开发

本地开发时，日报会存储在项目目录下的 `日报/` 文件夹。

运行机器人：
```bash
cd 飞书机器人
python ws_client_v4.py
```

---

## 注意事项

1. **免费额度限制**
   - 持久化存储：1 GB 免费
   - 超出后：$0.25/GB/月

2. **数据备份**
   - 建议定期备份重要日报
   - 可以通过 Render Shell 下载文件

3. **服务休眠**
   - 免费服务 15 分钟无请求后会休眠
   - 首次请求可能需要 30 秒唤醒

4. **日志查看**
   - 在 Render 控制台的 **Logs** 选项卡查看
