"""
飞书长连接客户端 - 使用官方SDK
"""
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from claude_handler import call_claude, get_agent_by_command
from feishu_handler import send_message, reply_message
from schedule_handler import is_schedule_message, process_schedule_message
from config import FEISHU_APP_ID, FEISHU_APP_SECRET

# 消息去重缓存
processed_messages = set()


def do_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """处理接收到的消息"""
    try:
        message = data.event.message
        message_id = message.message_id
        chat_id = message.chat_id
        content = message.content

        # 消息去重
        if message_id in processed_messages:
            return
        processed_messages.add(message_id)

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
            return

        print(f"\n收到消息: {text}")

        # 首先检查是否是日程消息
        if is_schedule_message(text):
            print("识别为日程消息，调用日程处理器...")
            schedule_response = process_schedule_message(text)
            if schedule_response:
                response = schedule_response
                print(f"日程回复: {response[:100]}...")
            else:
                # 如果日程处理器没有返回，继续正常流程
                agent = get_agent_by_command(text)
                print(f"调用Agent: {agent['name']}")
                response = call_claude(text, agent)
                print(f"回复: {response[:100]}...")
        else:
            # 识别Agent并调用Claude
            agent = get_agent_by_command(text)
            print(f"调用Agent: {agent['name']}")
            response = call_claude(text, agent)
            print(f"回复: {response[:100]}...")

        # 发送回复
        result = reply_message(message_id, response)
        if not result.get("success"):
            send_message(chat_id, response)
            print("已通过群消息回复")
        else:
            print("已回复消息")

    except Exception as e:
        print(f"处理消息异常: {str(e)}")


def main():
    """启动长连接客户端"""
    print("=" * 50)
    print("飞书长连接客户端 v4")
    print("=" * 50)
    print(f"App ID: {FEISHU_APP_ID}")
    print("模式: WebSocket长连接")
    print("=" * 50)

    # 注册事件处理器
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(do_im_message_receive_v1) \
        .build()

    # 创建客户端
    cli = lark.ws.Client(
        FEISHU_APP_ID,
        FEISHU_APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.DEBUG
    )

    print("\n正在连接飞书服务...")
    cli.start()


if __name__ == "__main__":
    main()
