"""
飞书机器人启动脚本
- 自动安装依赖
- 后台启动机器人
- 记录日志到 bot.log
"""
import subprocess
import sys
import os
import time

def install_deps():
    """安装依赖"""
    print("[1/2] 安装依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    subprocess.run([sys.executable, "-m", "pip", "install", "lark-oapi", "-q"])
    print("[1/2] 依赖安装完成")

def start_bot():
    """后台启动机器人"""
    print("[2/2] 启动飞书机器人...")

    # 获取当前目录
    cwd = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(cwd, "bot.log")

    # 后台启动进程
    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            [sys.executable, "ws_client_v4.py"],
            cwd=cwd,
            stdout=f,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

    # 等待启动
    time.sleep(2)

    # 检查是否启动成功
    if process.poll() is None:
        print()
        print("=" * 40)
        print("  [启动成功] 飞书机器人已在后台运行")
        print("=" * 40)
        print()
        print(f"  进程PID: {process.pid}")
        print(f"  日志文件: bot.log")
        print(f"  停止方法: 运行 stop.py 或在任务管理器结束进程")
        print()
    else:
        print("[启动失败] 请查看 bot.log 日志文件")

if __name__ == "__main__":
    install_deps()
    start_bot()
    input("按回车键退出...")
