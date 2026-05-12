"""
腾讯云函数入口 - 飞书机器人 HTTP 回调模式
"""
import json
import hashlib
from claude_handler import call_claude, get_agent_by_command
from feishu_handler import send_message, reply_message
from schedule_handler import is_schedule_message, process_schedule_message
from config import FEISHU_VERIFICATION_TOKEN, FEISHU_ENCRYPT_KEY


def main_handler(event, context):
    """云函数入口"""
    try:
        # 解析请求体
        if isinstance(event, str):
            body = json.loads(event)
        elif isinstance(event, dict):
            body = event.get("body", event)
            if isinstance(body, str):
                body = json.loads(body)
        else:
            return {"statusCode": 400, "body": "Invalid request"}

        print(f"收到请求: {json.dumps(body, ensure_ascii=False)[:500]}")

        # 处理飞书 URL 验证
        if "challenge" in body:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"challenge": body["challenge"]})
            }

        # 处理消息事件
        header = body.get("header", {})
        event_type = header.get("event_type", "")

        if event_type == "im.message.receive_v1":
            return handle_message(body.get("event", {}))

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        print(f"处理异常: {str(e)}")
        return {"statusCode": 500, "body": str(e)}


def handle_message(event_data):
    """处理飞书消息"""
    try:
        message = event_data.get("message", {})
        message_id = message.get("message_id")
        chat_id = message.get("chat_id")
        content = message.get("content", "{}")

        # 解析消息内容
        try:
            content_data = json.loads(content)
            text = content_data.get("text", "")
        except:
            text = content

        # 移除@机器人标签
        if "@_user_" in text:
            text = text.replace("@_user_", "").strip()

        if not text:
            return {"statusCode": 200, "body": "empty message"}

        print(f"收到消息: {text}")

        # 检查是否是日程消息
        if is_schedule_message(text):
            print("识别为日程消息")
            schedule_response = process_schedule_message(text)
            if schedule_response:
                response = schedule_response
            else:
                agent = get_agent_by_command(text)
                response = call_claude(text, agent)
        else:
            agent = get_agent_by_command(text)
            print(f"调用Agent: {agent['name']}")
            response = call_claude(text, agent)

        # 发送回复
        result = reply_message(message_id, response)
        if not result.get("success"):
            send_message(chat_id, response)

        print(f"回复完成: {response[:100]}...")

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        print(f"处理消息异常: {str(e)}")
        return {"statusCode": 500, "body": str(e)}
