"""
存储模块使用示例
演示如何使用 storage.py 保存和读取日报
"""
from storage import save_report, read_report, list_reports, get_storage_info
from datetime import datetime


def demo():
    """演示存储功能"""

    # 1. 查看存储信息
    info = get_storage_info()
    print("存储信息:")
    print(f"  存储路径: {info['storage_path']}")
    print(f"  是否在 Replit: {info['is_replit']}")
    print(f"  日报目录: {info['report_base']}")
    print()

    # 2. 保存日报
    today = datetime.now().strftime("%Y-%m-%d")

    news_content = """# AI新闻简报 - {date}

## 今日要闻

1. 大模型持续迭代
2. AI Agent 成为主流
3. AI 编程助手升级
""".format(date=today)

    save_report("新闻简报.md", news_content, today)
    print()

    # 3. 读取日报
    content = read_report("新闻简报.md", today)
    if content:
        print("读取到的日报:")
        print(content[:200] + "...")
    print()

    # 4. 列出所有日报
    reports = list_reports(today)
    print(f"{today} 的日报文件: {reports}")


if __name__ == "__main__":
    demo()
