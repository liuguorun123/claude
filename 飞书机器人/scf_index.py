"""
腾讯云函数 - 飞书机器人（单文件版本）
入口函数: index.main_handler
"""
import os
import json
import time
import requests
import anthropic
from datetime import datetime

# ============ 配置 ============
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "cli_aa8b6d69b4f95bec")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh")
FEISHU_CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_c0a8434e665e3fe113a4e82de30959c0")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "tp-c9k8raekucbxv5hp3fxxk8t19stqmbyuqmvmiw17yr48eaih")
CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL", "https://token-plan-cn.xiaomimimo.com/anthropic")
FEISHU_VERIFICATION_TOKEN = os.getenv("FEISHU_VERIFICATION_TOKEN", "2YUBlsn1eqmbsv7VLcqXLpfxRGfkRJaYk")

# ============ Agent 配置 ============
AGENTS = {
    "新闻Z": {"role": "新闻助理", "prompt": "你是新闻Z，负责获取AI新闻并生成简报。请用简洁的中文回复。"},
    "天气Z": {"role": "天气助理", "prompt": "你是天气Z，负责查询天气并给出出行建议。请用简洁的中文回复。"},
    "办公Z": {"role": "办公助理", "prompt": "你是办公Z，负责制定工作计划。请用简洁的中文回复。"},
    "整理Z": {"role": "整理助理", "prompt": "你是整理Z，负责安排时间和标注注意事项。请用简洁的中文回复。"},
    "日报Z": {"role": "日报助理", "prompt": "你是日报Z，负责生成工作日报。请用简洁的中文回复。"},
    "反思Z": {"role": "反思助理", "prompt": "你是反思Z，负责深度反思和规划明日。请用简洁的中文回复。"}
}

DEFAULT_AGENT = {"role": "通用助理", "prompt": "你是刘总的AI办公助理，可以帮助处理各种工作事务。请用简洁的中文回复。"}

COMMAND_MAP = {
    "获取新闻": "新闻Z", "新闻": "新闻Z",
    "今天天气": "天气Z", "天气": "天气Z", "天气怎么样": "天气Z",
    "制定计划": "办公Z", "工作计划": "办公Z", "计划": "办公Z", "安排": "办公Z", "日程": "办公Z", "会议": "办公Z",
    "整理安排": "整理Z", "整理": "整理Z",
    "写日报": "日报Z", "日报": "日报Z",
    "工作结束": "反思Z", "反思": "反思Z",
    "查看安排": "办公Z", "今天安排": "办公Z", "今天有什么": "办公Z"
}

# 日程识别关键词
SCHEDULE_KEYWORDS = [
    "安排", "计划", "日程", "会议", "开会", "提醒",
    "明天", "今天", "上午", "下午", "早上", "晚上",
    "点", "点半", "分", "小时"
]

# ============ 飞书 Token 缓存 ============
_token_cache = {"tenant_access_token": None, "expire_time": 0}


# ============ 飞书函数 ============
def get_tenant_access_token():
    global _token_cache
    if _token_cache["tenant_access_token"] and time.time() < _token_cache["expire_time"]:
        return _token_cache["tenant_access_token"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    data = resp.json()

    if data.get("code") == 0:
        _token_cache["tenant_access_token"] = data["tenant_access_token"]
        _token_cache["expire_time"] = time.time() + data.get("expire", 7200) - 300
        return _token_cache["tenant_access_token"]
    raise Exception(f"获取token失败: {data.get('msg')}")


def send_message(chat_id, content, msg_type="text"):
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    msg_content = json.dumps({"text": content}) if msg_type == "text" else content
    payload = {"receive_id": chat_id, "msg_type": msg_type, "content": msg_content}
    resp = requests.post(url, headers=headers, json=payload, params={"receive_id_type": "chat_id"})
    data = resp.json()
    return {"success": data.get("code") == 0, "message_id": data.get("data", {}).get("message_id"), "error": data.get("msg")}


def reply_message(message_id, content, msg_type="text"):
    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    msg_content = json.dumps({"text": content}) if msg_type == "text" else content
    payload = {"msg_type": msg_type, "content": msg_content}
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()
    return {"success": data.get("code") == 0, "error": data.get("msg")}


# ============ Claude 函数 ============
def get_agent_by_command(message):
    for command, agent_name in COMMAND_MAP.items():
        if command in message:
            return {"name": agent_name, **AGENTS[agent_name]}
    return {"name": "助理Z", **DEFAULT_AGENT}


def call_claude(message, agent=None):
    if agent is None:
        agent = {"name": "助理Z", **DEFAULT_AGENT}

    try:
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY, base_url=CLAUDE_BASE_URL)
        system_prompt = f"""{agent['prompt']}

当前角色：{agent['name']}
当前用户：刘总

【重要规则】
1. 严禁编造内容：只基于用户明确提供的信息回复
2. 信息不足时询问：不要自行补充
3. 忠实记录：只能整理用户已明确说明的内容
4. 简洁回复：用简洁的中文回复"""

        response = client.messages.create(
            model="mimo-v2.5-pro",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )
        return response.content[0].text
    except Exception as e:
        return f"抱歉，处理消息时出现错误：{str(e)}"


# ============ 日程函数 ============
def is_schedule_message(message):
    keyword_count = sum(1 for keyword in SCHEDULE_KEYWORDS if keyword in message)
    if keyword_count >= 2:
        return True
    time_patterns = ["点开会", "点会议", "点有", "点要", "提醒我"]
    return any(pattern in message for pattern in time_patterns)


def process_schedule_message(message):
    try:
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY, base_url=CLAUDE_BASE_URL)
        today = datetime.now().strftime("%Y-%m-%d")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]

        system_prompt = f"""你是一个日程解析助手。从用户消息中提取日程信息。
当前日期：{today}（{weekday}）
返回 JSON 格式：
{{"has_schedule": true/false, "date": "YYYY-MM-DD", "schedules": [{{"time": "时间", "event": "事件", "location": "地点"}}], "summary": "摘要"}}
只提取用户明确提到的日程，不要编造。"""

        response = client.messages.create(
            model="mimo-v2.5-pro",
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )

        result = response.content[0].text
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]

        schedule_data = json.loads(result.strip())

        if not schedule_data.get("has_schedule"):
            return None

        # 格式化回复
        date_str = schedule_data.get("date", today)
        resp = f"✅ 日程已记录！\n\n📅 日期：{date_str}\n📋 摘要：{schedule_data.get('summary', '')}\n\n详细安排：\n"
        for item in schedule_data.get("schedules", []):
            resp += f"• {item.get('time', '待定')} - {item.get('event', '')}"
            if item.get("location"):
                resp += f"（{item['location']}）"
            resp += "\n"
        return resp

    except Exception as e:
        print(f"日程处理异常: {str(e)}")
        return None


# ============ 云函数入口 ============
def main_handler(event, context):
    try:
        if isinstance(event, str):
            body = json.loads(event)
        elif isinstance(event, dict):
            body = event.get("body", event)
            if isinstance(body, str):
                body = json.loads(body)
        else:
            return {"statusCode": 400, "body": "Invalid request"}

        print(f"收到请求: {json.dumps(body, ensure_ascii=False)[:500]}")

        # URL 验证
        if "challenge" in body:
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"challenge": body["challenge"]})}

        # 处理消息
        header = body.get("header", {})
        if header.get("event_type") == "im.message.receive_v1":
            event_data = body.get("event", {})
            message = event_data.get("message", {})
            message_id = message.get("message_id")
            chat_id = message.get("chat_id")
            content = message.get("content", "{}")

            try:
                text = json.loads(content).get("text", "")
            except:
                text = content

            if "@_user_" in text:
                text = text.replace("@_user_", "").strip()

            if not text:
                return {"statusCode": 200, "body": "empty"}

            print(f"消息: {text}")

            # 处理消息
            if is_schedule_message(text):
                response = process_schedule_message(text)
                if not response:
                    agent = get_agent_by_command(text)
                    response = call_claude(text, agent)
            else:
                agent = get_agent_by_command(text)
                response = call_claude(text, agent)

            # 回复
            result = reply_message(message_id, response)
            if not result.get("success"):
                send_message(chat_id, response)

            print(f"回复: {response[:100]}...")

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        print(f"异常: {str(e)}")
        return {"statusCode": 500, "body": str(e)}
