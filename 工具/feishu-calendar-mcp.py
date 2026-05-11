#!/usr/bin/env python3
"""飞书日历MCP Server - 获取日程安排"""

import json
import sys
import os
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List

# 飞书配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_aa8b6d69b4f95bec")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh")

def get_tenant_access_token() -> str:
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

def get_calendar_list() -> Dict[str, Any]:
    """获取日历列表"""
    token = get_tenant_access_token()
    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_calendar_events(calendar_id: str = "primary", days: int = 1) -> Dict[str, Any]:
    """获取日历事件

    Args:
        calendar_id: 日历ID，默认为primary
        days: 获取未来几天的事件，默认1天
    """
    token = get_tenant_access_token()

    # 计算时间范围
    now = datetime.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=days)

    # 转换为时间戳（秒）
    start_timestamp = str(int(start_time.timestamp()))
    end_timestamp = str(int(end_time.timestamp()))

    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "start_time": start_timestamp,
        "end_time": end_timestamp
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def get_today_events() -> Dict[str, Any]:
    """获取今天的日程安排"""
    return get_calendar_events(days=1)

def get_tomorrow_events() -> Dict[str, Any]:
    """获取明天的日程安排"""
    token = get_tenant_access_token()

    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    start_time = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=1)

    start_timestamp = str(int(start_time.timestamp()))
    end_timestamp = str(int(end_time.timestamp()))

    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars/primary/events"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "start_time": start_timestamp,
        "end_time": end_timestamp
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def format_event(event: Dict) -> str:
    """格式化事件信息"""
    summary = event.get("summary", "无标题")
    start = event.get("start_time", {})
    end = event.get("end_time", {})
    location = event.get("location", {}).get("name", "")

    # 处理时间
    if start.get("timestamp"):
        start_dt = datetime.fromtimestamp(int(start["timestamp"]))
        start_str = start_dt.strftime("%H:%M")
    else:
        start_str = "全天"

    if end.get("timestamp"):
        end_dt = datetime.fromtimestamp(int(end["timestamp"]))
        end_str = end_dt.strftime("%H:%M")
    else:
        end_str = ""

    time_range = f"{start_str}-{end_str}" if end_str else start_str

    result = f"[{time_range}] {summary}"
    if location:
        result += f" @ {location}"

    return result

# MCP协议处理
class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "get_today_calendar",
                "description": "获取今天的日程安排",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_tomorrow_calendar",
                "description": "获取明天的日程安排",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_week_calendar",
                "description": "获取本周的日程安排",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "feishu-calendar-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": self.tools
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")

            if tool_name == "get_today_calendar":
                result = get_today_events()
                # 格式化输出
                if result.get("code") == 0:
                    events = result.get("data", {}).get("items", [])
                    if events:
                        formatted = "今日日程：\n" + "\n".join([format_event(e) for e in events])
                    else:
                        formatted = "今日暂无日程安排"
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": formatted}]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": f"获取日程失败: {result}"}]
                        }
                    }

            elif tool_name == "get_tomorrow_calendar":
                result = get_tomorrow_events()
                if result.get("code") == 0:
                    events = result.get("data", {}).get("items", [])
                    if events:
                        formatted = "明日日程：\n" + "\n".join([format_event(e) for e in events])
                    else:
                        formatted = "明日暂无日程安排"
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": formatted}]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": f"获取日程失败: {result}"}]
                        }
                    }

            elif tool_name == "get_week_calendar":
                result = get_calendar_events(days=7)
                if result.get("code") == 0:
                    events = result.get("data", {}).get("items", [])
                    if events:
                        # 按日期分组
                        from collections import defaultdict
                        events_by_date = defaultdict(list)
                        for event in events:
                            start = event.get("start_time", {})
                            if start.get("timestamp"):
                                dt = datetime.fromtimestamp(int(start["timestamp"]))
                                date_str = dt.strftime("%m月%d日")
                                events_by_date[date_str].append(format_event(event))

                        formatted = "本周日程：\n"
                        for date, day_events in sorted(events_by_date.items()):
                            formatted += f"\n{date}:\n"
                            for e in day_events:
                                formatted += f"  {e}\n"
                    else:
                        formatted = "本周暂无日程安排"
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": formatted}]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": f"获取日程失败: {result}"}]
                        }
                    }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"未知工具: {tool_name}"
                    }
                }

        elif method == "notifications/initialized":
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"未知方法: {method}"
                }
            }

def main():
    server = MCPServer()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
