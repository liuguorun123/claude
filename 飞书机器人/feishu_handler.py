import requests
import json
import time
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID


# Token缓存
_token_cache = {
    "tenant_access_token": None,
    "expire_time": 0
}


def get_tenant_access_token() -> str:
    """获取飞书tenant_access_token"""
    global _token_cache

    # 检查缓存是否有效
    if _token_cache["tenant_access_token"] and time.time() < _token_cache["expire_time"]:
        return _token_cache["tenant_access_token"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()

        if data.get("code") == 0:
            token = data.get("tenant_access_token")
            expire = data.get("expire", 7200)

            # 更新缓存
            _token_cache["tenant_access_token"] = token
            _token_cache["expire_time"] = time.time() + expire - 300  # 提前5分钟刷新

            return token
        else:
            raise Exception(f"获取token失败: {data.get('msg')}")

    except Exception as e:
        raise Exception(f"获取token异常: {str(e)}")


def send_message(chat_id: str, content: str, msg_type: str = "text") -> dict:
    """发送消息到飞书群"""
    token = get_tenant_access_token()

    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 构建消息体
    if msg_type == "text":
        msg_content = json.dumps({"text": content})
    else:
        msg_content = content

    payload = {
        "receive_id": chat_id,
        "msg_type": msg_type,
        "content": msg_content
    }

    params = {"receive_id_type": "chat_id"}

    try:
        response = requests.post(url, headers=headers, json=payload, params=params)
        data = response.json()

        if data.get("code") == 0:
            return {"success": True, "message_id": data["data"]["message_id"]}
        else:
            return {"success": False, "error": data.get("msg")}

    except Exception as e:
        return {"success": False, "error": str(e)}


def reply_message(message_id: str, content: str, msg_type: str = "text") -> dict:
    """回复飞书消息"""
    token = get_tenant_access_token()

    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 构建消息体
    if msg_type == "text":
        msg_content = json.dumps({"text": content})
    else:
        msg_content = content

    payload = {
        "msg_type": msg_type,
        "content": msg_content
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if data.get("code") == 0:
            return {"success": True, "message_id": data["data"]["message_id"]}
        else:
            return {"success": False, "error": data.get("msg")}

    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_message(event: dict) -> dict:
    """解析飞书消息事件"""
    message = event.get("message", {})
    sender = event.get("sender", {})

    return {
        "message_id": message.get("message_id"),
        "chat_id": message.get("chat_id"),
        "chat_type": message.get("chat_type"),
        "message_type": message.get("message_type"),
        "content": message.get("content"),
        "sender_id": sender.get("sender_id", {}).get("open_id"),
        "sender_type": sender.get("sender_type")
    }
