@echo off
chcp 65001 >nul
title 飞书机器人后台服务

echo ========================================
echo   飞书机器人启动脚本
echo ========================================
echo.

:: 检查是否已在运行
tasklist /FI "WINDOWTITLE eq 飞书机器人*" 2>nul | find /I "python.exe" >nul
if %errorlevel%==0 (
    echo [警告] 飞书机器人可能已在运行中
    echo 如需重启，请先运行 stop.bat
    pause
    exit /b
)

:: 安装依赖
echo [1/2] 检查并安装依赖...
pip install -r requirements.txt -q
pip install lark-oapi -q
echo [1/2] 依赖安装完成
echo.

:: 后台启动机器人
echo [2/2] 启动飞书机器人...
start /B python ws_client_v4.py > bot.log 2>&1

:: 等待启动
timeout /t 2 >nul

:: 检查是否启动成功
tasklist | findstr "python.exe" >nul
if %errorlevel%==0 (
    echo.
    echo ========================================
    echo   [启动成功] 飞书机器人已在后台运行
    echo ========================================
    echo.
    echo   日志文件: bot.log
    echo   停止命令: 运行 stop.bat 或在任务管理器结束 python.exe
    echo.
) else (
    echo.
    echo   [启动失败] 请查看 bot.log 日志文件
    echo.
)

pause
