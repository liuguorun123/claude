# 飞书机器人 Replit 部署指南

## 快速部署

### 1. Fork 仓库

1. 访问 GitHub 仓库页面
2. 点击右上角 **Fork** 按钮
3. 将仓库 Fork 到你的账号

### 2. 在 Replit 创建项目

1. 访问 [replit.com](https://replit.com) 并注册/登录
2. 点击 **Create Repl**
3. 选择 **Import from GitHub**
4. 粘贴你 Fork 的仓库地址
5. 点击 **Import from GitHub**

### 3. 设置环境变量

在 Replit 项目中，点击左侧 **Secrets** (锁图标)，添加以下环境变量：

| Key | Value |
|-----|-------|
| `CLAUDE_API_KEY` | `tp-c9k8raekucbxv5hp3fxxk8t19stqmbyuqmvmiw17yr48eaih` |
| `CLAUDE_BASE_URL` | `https://token-plan-cn.xiaomimimo.com/anthropic` |
| `FEISHU_APP_ID` | `cli_aa8b6d69b4f95bec` |
| `FEISHU_APP_SECRET` | `1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh` |
| `FEISHU_CHAT_ID` | `oc_c0a8434e665e3fe113a4e82de30959c0` |
| `STORAGE_PATH` | `/home/runner/agent` |

### 4. 安装依赖

在 Replit 的 Shell 中运行：

```bash
pip install -r 飞书机器人/requirements.txt
```

### 5. 点击 Run

点击顶部的 **Run** 按钮启动机器人。

---

## 存储结构

部署后，日报文件会存储在项目目录下：

```
/home/runner/agent/
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

在 Replit 的 Shell 中运行：
```bash
ls 日报/
```

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
   - Replit 免费版有使用时间限制
   - 建议升级到 Hacker 计划获得更好体验

2. **数据备份**
   - Replit 项目会自动保存到 GitHub
   - 日报文件会随项目一起备份

3. **Always On**
   - 免费版不支持 Always On
   - 如需 24 小时运行，需要升级计划或使用外部保活服务

4. **日志查看**
   - 在 Replit 控制台的 **Console** 区域查看
