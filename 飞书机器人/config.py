import os

# 飞书配置（优先从环境变量读取，否则使用默认值）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_aa8b6d69b4f95bec")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh")
FEISHU_CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_c0a8434e665e3fe113a4e82de30959c0")

# Claude API配置（优先从环境变量读取，否则使用默认值）
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "tp-c9k8raekucbxv5hp3fxxk8t19stqmbyuqmvmiw17yr48eaih")
CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL", "https://token-plan-cn.xiaomimimo.com/anthropic")

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

# 飞书验证Token（用于验证请求来源）
FEISHU_VERIFICATION_TOKEN = os.getenv("FEISHU_VERIFICATION_TOKEN", "2YUBlsn1eqmbsv7VLcqXLpfxRGfkRJaYk")

# 飞书加密Key（可选，用于解密加密消息）
FEISHU_ENCRYPT_KEY = os.getenv("FEISHU_ENCRYPT_KEY", "")
