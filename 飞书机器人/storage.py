"""
存储路径管理
- 本地开发：使用项目目录下的 日报 文件夹
- Replit 部署：使用项目目录持久化存储
"""
import os
from datetime import datetime

# 存储路径配置
# 本地开发时使用项目目录，Replit 部署时也使用项目目录
STORAGE_PATH = os.getenv("STORAGE_PATH", os.path.dirname(os.path.abspath(__file__)))

def get_report_dir(date_str: str = None) -> str:
    """获取日报目录路径"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # 日报存储路径
    report_dir = os.path.join(STORAGE_PATH, "日报", date_str)

    # 确保目录存在
    os.makedirs(report_dir, exist_ok=True)

    return report_dir


def get_report_path(filename: str, date_str: str = None) -> str:
    """获取日报文件完整路径"""
    report_dir = get_report_dir(date_str)
    return os.path.join(report_dir, filename)


def save_report(filename: str, content: str, date_str: str = None) -> str:
    """保存日报文件"""
    filepath = get_report_path(filename, date_str)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[存储] 日报已保存: {filepath}")
    return filepath


def read_report(filename: str, date_str: str = None) -> str:
    """读取日报文件"""
    filepath = get_report_path(filename, date_str)

    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def list_reports(date_str: str = None) -> list:
    """列出指定日期的所有日报文件"""
    report_dir = get_report_dir(date_str)

    if not os.path.exists(report_dir):
        return []

    return [f for f in os.listdir(report_dir) if f.endswith(".md")]


def get_storage_info() -> dict:
    """获取存储信息"""
    return {
        "storage_path": STORAGE_PATH,
        "is_replit": os.getenv("REPL_ID") is not None,
        "report_base": os.path.join(STORAGE_PATH, "日报")
    }
