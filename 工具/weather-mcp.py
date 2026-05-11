#!/usr/bin/env python3
"""天气MCP Server - 使用wttr.in获取天气信息（完全免费）"""

import json
import sys
import requests
from typing import Any, Dict

CITY = "Chengdu"

def get_weather() -> str:
    """获取当前天气"""
    url = f"https://wttr.in/{CITY}?format=%l:+%c+%t+%h+%w+%p"
    response = requests.get(url, timeout=10)
    return response.text.strip()

def get_weather_detail() -> str:
    """获取详细天气信息"""
    url = f"https://wttr.in/{CITY}?lang=zh&format=3"
    response = requests.get(url, timeout=10)
    return response.text.strip()

def get_weather_forecast() -> str:
    """获取3天天气预报"""
    url = f"https://wttr.in/{CITY}?lang=zh&format=%l\n日期:%d\n天气:%C\n温度:%t\n湿度:%h\n风速:%w\n"
    response = requests.get(url, timeout=10)
    return response.text.strip()

def get_weather_full() -> str:
    """获取完整天气报告"""
    url = f"https://wttr.in/{CITY}?lang=zh&format=4"
    response = requests.get(url, timeout=10)
    return response.text.strip()

def get_advice(weather_text: str) -> str:
    """根据天气给出建议"""
    advice = []

    # 温度建议
    if "°C" in weather_text:
        try:
            temp_str = weather_text.split("°C")[0].split()[-1]
            temp = int(temp_str.replace("+", "").replace("-", "-"))
            if temp < 10:
                advice.append("🧥 天气寒冷，注意保暖")
            elif temp < 20:
                advice.append("👔 适合穿薄外套或长袖")
            elif temp < 30:
                advice.append("👕 天气舒适，适合轻便着装")
            else:
                advice.append("🥵 天气炎热，注意防暑")
        except:
            pass

    # 天气状况建议
    if "雨" in weather_text or "rain" in weather_text.lower():
        advice.append("🌧️ 记得带伞")
    if "雪" in weather_text or "snow" in weather_text.lower():
        advice.append("❄️ 路滑注意安全")
    if "雾" in weather_text or "fog" in weather_text.lower():
        advice.append("🌫️ 能见度低，注意出行安全")

    return "\n".join(advice) if advice else "✅ 天气适宜出行"

# MCP协议处理
class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "get_weather",
                "description": f"获取{CITY}当前天气信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_weather_detail",
                "description": f"获取{CITY}详细天气信息和建议",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "weather-mcp", "version": "1.0.0"}
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.tools}
            }
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")

            if tool_name == "get_weather":
                weather = get_weather()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": weather}]
                    }
                }
            elif tool_name == "get_weather_detail":
                weather = get_weather_detail()
                advice = get_advice(weather)
                result = f"{weather}\n\n💡 建议：\n{advice}"
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"未知工具: {tool_name}"}
                }
        elif method == "notifications/initialized":
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"未知方法: {method}"}
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
        except:
            continue

if __name__ == "__main__":
    main()
