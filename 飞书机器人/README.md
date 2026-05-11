# 飞书机器人 - AI办公助理

## 功能介绍

通过飞书群直接命令AI办公助理团队，支持以下Agent：

| 命令 | Agent | 功能 |
|------|-------|------|
| 获取新闻 / 新闻 | 新闻Z | 获取AI新闻并生成简报 |
| 今天天气 / 天气 | 天气Z | 查询天气并给出出行建议 |
| 制定计划 / 工作计划 | 办公Z | 制定工作计划 |
| 整理安排 / 整理 | 整理Z | 安排时间和标注注意事项 |
| 写日报 / 日报 | 日报Z | 生成工作日报 |
| 工作结束 / 反思 | 反思Z | 深度反思和规划明日 |

## 使用方式

在飞书群中：
```
@助理Z 获取新闻
@助理Z 今天天气怎么样
@助理Z 制定今天的工作计划
```

## 启动方法

```cmd
cd C:\Users\lenovo\Desktop\agent\飞书机器人
python ws_client_v4.py
```

## 文件结构

```
飞书机器人/
├── ws_client_v4.py     # 长连接客户端（最终版）
├── config.py           # 配置文件
├── claude_handler.py   # AI模型处理
├── feishu_handler.py   # 飞书消息处理
├── requirements.txt    # Python依赖
└── README.md           # 说明文档
```

## 配置说明

- 飞书App ID: cli_aa8b6d69b4f95bec
- AI模型: mimo-v2.5-pro（小米MIMO）
- 连接方式: WebSocket长连接（无需公网IP）
