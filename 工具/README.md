# 飞书MCP工具使用说明

## 配置步骤

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置Claude Code

在Claude Code的设置中添加MCP server配置。有两种方式：

#### 方式一：项目级配置（推荐）

在项目根目录创建 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "feishu": {
      "command": "python",
      "args": ["工具/feishu-mcp.py"],
      "env": {
        "FEISHU_APP_ID": "cli_aa8b6d69b4f95bec",
        "FEISHU_APP_SECRET": "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh",
        "FEISHU_CHAT_ID": "oc_c0a8434e665e3fe113a4e82de30959c0"
      }
    }
  }
}
```

#### 方式二：用户级配置

在 `~/.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "feishu": {
      "command": "python",
      "args": ["C:\\Users\\lenovo\\Desktop\\agent\\工具\\feishu-mcp.py"],
      "env": {
        "FEISHU_APP_ID": "cli_aa8b6d69b4f95bec",
        "FEISHU_APP_SECRET": "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh",
        "FEISHU_CHAT_ID": "oc_c0a8434e665e3fe113a4e82de30959c0"
      }
    }
  }
}
```

### 3. 重启Claude Code

配置完成后，重启Claude Code以加载MCP server。

## 使用方法

配置完成后，Claude Code会自动获得 `send_feishu_message` 工具。

### 发送文本消息

```
请发送消息到飞书：今天的新闻简报已生成
```

### 发送富文本消息

Agent会自动将Markdown文档转换为富文本格式发送。

## 文件说明

- `feishu.py` - 独立的飞书API工具脚本
- `feishu-mcp.py` - MCP server实现
- `mcp-config.json` - MCP配置参考

## 注意事项

1. 飞书应用需要已发布并获得相应权限
2. 机器人需要已被添加到流星群
3. 如果发送失败，检查应用权限和群设置
