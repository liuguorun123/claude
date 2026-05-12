"""
日程管理功能示例
演示如何识别和存储日程安排
"""
from schedule_handler import is_schedule_message, extract_schedule, save_schedule, format_schedule_response
from datetime import datetime


def demo():
    """演示日程管理功能"""

    print("=" * 50)
    print("日程管理功能演示")
    print("=" * 50)
    print()

    # 示例消息
    test_messages = [
        "今天上午10点有早会",
        "下午2点和客户开会，地点在会议室A",
        "明天上午9点半项目评审",
        "今天天气怎么样",  # 非日程消息
        "提醒我3点提交报告",
    ]

    for msg in test_messages:
        print(f"消息: {msg}")
        print("-" * 40)

        # 检查是否是日程消息
        is_schedule = is_schedule_message(msg)
        print(f"是否日程: {is_schedule}")

        if is_schedule:
            # 提取日程信息
            schedule_data = extract_schedule(msg)
            print(f"提取结果: {schedule_data}")

            if schedule_data.get("has_schedule"):
                # 保存日程
                filepath = save_schedule(schedule_data)
                print(f"保存路径: {filepath}")

                # 格式化回复
                response = format_schedule_response(schedule_data)
                print(f"回复内容:\n{response}")

        print()
        print("=" * 50)
        print()


if __name__ == "__main__":
    demo()
