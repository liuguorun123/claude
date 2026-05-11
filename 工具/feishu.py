#!/usr/bin/env python3
"""飞书API工具 - 发送消息到飞书群"""

import requests
import json
import sys

# 飞书配置
APP_ID = "cli_aa8b6d69b4f95bec"
APP_SECRET = "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh"
CHAT_ID = "oc_c0a8434e665e3fe113a4e82de30959c0"

def get_tenant_access_token():
    """获取tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        raise Exception(f"获取token失败: {data}")

def send_message(content, msg_type="text"):
    """发送消息到飞书群"""
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if msg_type == "text":
        payload = {
            "receive_id": CHAT_ID,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }
    elif msg_type == "post":
        # 富文本消息
        payload = {
            "receive_id": CHAT_ID,
            "msg_type": "post",
            "content": json.dumps(content)
        }
    else:
        raise ValueError(f"不支持的消息类型: {msg_type}")

    params = {"receive_id_type": "chat_id"}
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()

def send_markdown(title, content):
    """发送Markdown格式的消息（使用富文本）"""
    post_content = {
        "zh_cn": {
            "title": title,
            "content": [
                [{"tag": "text", "text": content}]
            ]
        }
    }
    return send_message(post_content, msg_type="post")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python feishu.py <消息内容>")
        sys.exit(1)

    message = sys.argv[1]
    result = send_message(message)
    print(json.dumps(result, ensure_ascii=False, indent=2))
