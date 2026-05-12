"""
日程管理模块
- 识别用户输入的日程信息
- 解析日程内容和时间
- 存储到日报文件
"""
import json
import anthropic
from datetime import datetime
from storage import save_report, read_report
from config import CLAUDE_API_KEY, CLAUDE_BASE_URL

# 日程识别关键词
SCHEDULE_KEYWORDS = [
    "安排", "计划", "日程", "会议", "开会", "提醒",
    "明天", "今天", "上午", "下午", "早上", "晚上",
    "点", "点半", "分", "小时"
]


def is_schedule_message(message: str) -> bool:
    """判断是否是日程相关消息"""
    # 检查是否包含日程关键词
    keyword_count = sum(1 for keyword in SCHEDULE_KEYWORDS if keyword in message)

    # 如果包含2个以上关键词，可能是日程消息
    if keyword_count >= 2:
        return True

    # 特殊模式：时间+事件
    time_patterns = ["点开会", "点会议", "点有", "点要", "提醒我"]
    if any(pattern in message for pattern in time_patterns):
        return True

    return False


def extract_schedule(message: str) -> dict:
    """使用 Claude 提取日程信息"""
    try:
        client = anthropic.Anthropic(
            api_key=CLAUDE_API_KEY,
            base_url=CLAUDE_BASE_URL
        )

        today = datetime.now().strftime("%Y-%m-%d")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]

        system_prompt = f"""你是一个日程解析助手。请从用户的消息中提取日程安排信息。

当前日期：{today}（{weekday}）

【输出格式】
请返回 JSON 格式：
{{
    "has_schedule": true/false,
    "date": "YYYY-MM-DD",
    "schedules": [
        {{
            "time": "HH:MM 或 上午/下午",
            "event": "事件描述",
            "duration": "持续时间（如有）",
            "location": "地点（如有）"
        }}
    ],
    "summary": "日程摘要（一句话）"
}}

【规则】
1. 如果用户说的是"今天"，日期就是 {today}
2. 如果用户说的是"明天"，请计算明天的日期
3. 只提取用户明确提到的日程，不要编造
4. 如果没有明确的时间，time 字段可以为空
5. 如果不是日程消息，has_schedule 设为 false"""

        response = client.messages.create(
            model="mimo-v2.5-pro",
            max_tokens=512,
            system=system_prompt,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        result = response.content[0].text

        # 尝试解析 JSON
        try:
            # 清理可能的 markdown 代码块标记
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]

            return json.loads(result.strip())
        except json.JSONDecodeError:
            return {"has_schedule": False, "error": "解析失败", "raw": result}

    except Exception as e:
        return {"has_schedule": False, "error": str(e)}


def save_schedule(schedule_data: dict) -> str:
    """保存日程到文件"""
    if not schedule_data.get("has_schedule"):
        return None

    date_str = schedule_data.get("date", datetime.now().strftime("%Y-%m-%d"))

    # 读取现有日程
    existing_content = read_report("日程安排.md", date_str)

    # 构建日程内容
    new_schedule = ""
    for item in schedule_data.get("schedules", []):
        time_str = item.get("time", "待定")
        event = item.get("event", "")
        location = item.get("location", "")

        line = f"- **{time_str}**：{event}"
        if location:
            line += f"（📍{location}）"
        new_schedule += line + "\n"

    # 如果已有日程，追加；否则创建新文件
    if existing_content:
        content = existing_content.rstrip() + "\n" + new_schedule
    else:
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][
            datetime.strptime(date_str, "%Y-%m-%d").weekday()
        ]
        content = f"""# 日程安排 - {date_str}（{weekday}）

## 今日安排

{new_schedule}
"""

    # 保存文件
    filepath = save_report("日程安排.md", content, date_str)
    return filepath


def format_schedule_response(schedule_data: dict) -> str:
    """格式化日程确认回复"""
    if not schedule_data.get("has_schedule"):
        return None

    date_str = schedule_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    summary = schedule_data.get("summary", "")

    response = f"✅ 日程已记录！\n\n📅 日期：{date_str}\n"
    response += f"📋 摘要：{summary}\n\n"
    response += "详细安排：\n"

    for item in schedule_data.get("schedules", []):
        time_str = item.get("time", "待定")
        event = item.get("event", "")
        location = item.get("location", "")

        response += f"• {time_str} - {event}"
        if location:
            response += f"（{location}）"
        response += "\n"

    response += "\n已保存到日报文件，可随时查看。"
    return response


def process_schedule_message(message: str) -> str:
    """处理日程消息，返回回复内容"""
    # 提取日程信息
    schedule_data = extract_schedule(message)

    if not schedule_data.get("has_schedule"):
        return None

    # 保存日程
    filepath = save_schedule(schedule_data)

    if filepath:
        # 返回确认消息
        return format_schedule_response(schedule_data)
    else:
        return "抱歉，保存日程时出现问题，请重试。"
