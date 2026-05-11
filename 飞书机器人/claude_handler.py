import anthropic
from config import CLAUDE_API_KEY, CLAUDE_BASE_URL

# Agent配置
AGENTS = {
    "新闻Z": {
        "role": "新闻助理",
        "prompt": "你是新闻Z，负责获取AI新闻并生成简报。请用简洁的中文回复。"
    },
    "天气Z": {
        "role": "天气助理",
        "prompt": "你是天气Z，负责查询天气并给出出行建议。请用简洁的中文回复。"
    },
    "办公Z": {
        "role": "办公助理",
        "prompt": "你是办公Z，负责制定工作计划。请用简洁的中文回复。"
    },
    "整理Z": {
        "role": "整理助理",
        "prompt": "你是整理Z，负责安排时间和标注注意事项。请用简洁的中文回复。"
    },
    "日报Z": {
        "role": "日报助理",
        "prompt": "你是日报Z，负责生成工作日报。请用简洁的中文回复。"
    },
    "反思Z": {
        "role": "反思助理",
        "prompt": "你是反思Z，负责深度反思和规划明日。请用简洁的中文回复。"
    }
}

# 默认助理配置
DEFAULT_AGENT = {
    "role": "通用助理",
    "prompt": "你是刘总的AI办公助理，可以帮助处理各种工作事务。请用简洁的中文回复。"
}

# 命令映射
COMMAND_MAP = {
    "获取新闻": "新闻Z",
    "新闻": "新闻Z",
    "今天天气": "天气Z",
    "天气": "天气Z",
    "天气怎么样": "天气Z",
    "制定计划": "办公Z",
    "工作计划": "办公Z",
    "计划": "办公Z",
    "整理安排": "整理Z",
    "整理": "整理Z",
    "写日报": "日报Z",
    "日报": "日报Z",
    "工作结束": "反思Z",
    "反思": "反思Z"
}


def get_agent_by_command(message: str) -> dict:
    """根据命令识别对应的Agent"""
    for command, agent_name in COMMAND_MAP.items():
        if command in message:
            return {
                "name": agent_name,
                **AGENTS[agent_name]
            }
    return {
        "name": "助理Z",
        **DEFAULT_AGENT
    }


def call_claude(message: str, agent: dict = None) -> str:
    """调用Claude API处理消息"""
    if agent is None:
        agent = {
            "name": "助理Z",
            **DEFAULT_AGENT
        }

    try:
        client = anthropic.Anthropic(
            api_key=CLAUDE_API_KEY,
            base_url=CLAUDE_BASE_URL
        )

        system_prompt = f"""{agent['prompt']}

当前角色：{agent['name']}
当前用户：刘总

请根据用户的问题提供有帮助的回复。如果用户没有指定具体任务，请询问用户需要什么帮助。"""

        # 尝试小米MIMO模型
        models_to_try = [
            "mimo-v2.5-pro",
            "mimo-v2.5"
        ]

        response = None
        for model in models_to_try:
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": message}
                    ]
                )
                print(f"成功使用模型: {model}")
                break
            except Exception as e:
                print(f"模型 {model} 失败: {str(e)}")
                continue

        if response is None:
            return "抱歉，所有模型都不可用，请联系管理员。"

        return response.content[0].text

    except Exception as e:
        return f"抱歉，处理消息时出现错误：{str(e)}"
