#!/usr/bin/env python3
"""飞书MCP Server - 提供飞书消息发送能力"""

import json
import sys
import os
from typing import Any, Dict, List, Optional

# 从环境变量获取配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_aa8b6d69b4f95bec")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "1FFHn4A3RQekxOaFjB1gpfvo0IrB57uh")
CHAT_ID = os.getenv("FEISHU_CHAT_ID", "oc_c0a8434e665e3fe113a4e82de30959c0")

import requests

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

def send_feishu_message(content: str, msg_type: str = "text") -> Dict[str, Any]:
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
        payload = {
            "receive_id": CHAT_ID,
            "msg_type": "post",
            "content": json.dumps(content)
        }
    else:
        return {"error": f"不支持的消息类型: {msg_type}"}

    params = {"receive_id_type": "chat_id"}
    response = requests.post(url, headers=headers, params=params, json=payload)
    return response.json()

# MCP协议处理
class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "send_feishu_message",
                "description": "发送消息到飞书流星群",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "要发送的消息内容"
                        },
                        "msg_type": {
                            "type": "string",
                            "enum": ["text", "post"],
                            "description": "消息类型：text为纯文本，post为富文本",
                            "default": "text"
                        }
                    },
                    "required": ["content"]
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
                        "name": "feishu-mcp",
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
            arguments = params.get("arguments", {})

            if tool_name == "send_feishu_message":
                content = arguments.get("content", "")
                msg_type = arguments.get("msg_type", "text")
                result = send_feishu_message(content, msg_type)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False)
                            }
                        ]
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
            # 通知不需要响应
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
    """主函数 - 处理stdin/stdout通信"""
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
