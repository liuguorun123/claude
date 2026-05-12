"""
停止飞书机器人
"""
import subprocess
import sys

def stop_bot():
    """停止机器人进程"""
    print("正在停止飞书机器人...")

    if sys.platform == "win32":
        # Windows: 通过任务标题查找
        subprocess.run(["taskkill", "/FI", "WINDOWTITLE eq *ws_client_v4*", "/F"],
                       capture_output=True)
        # 也尝试通过 python 进程名查找相关脚本
        result = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get", "commandline"],
            capture_output=True, text=True
        )
        for line in result.stdout.split("\n"):
            if "ws_client_v4" in line:
                # 提取 PID
                parts = line.split()
                # 找到并结束进程
                subprocess.run(["taskkill", "/F", "/IM", "python.exe"],
                              capture_output=True)
    else:
        # Linux/Mac
        subprocess.run(["pkill", "-f", "ws_client_v4"], capture_output=True)

    print("[完成] 飞书机器人已停止")

if __name__ == "__main__":
    stop_bot()
    input("按回车键退出...")
