@echo off
chcp 65001 >nul
title 停止飞书机器人

echo ========================================
echo   停止飞书机器人
echo ========================================
echo.

:: 查找并结束机器人进程
taskkill /FI "WINDOWTITLE eq 飞书机器人*" /F >nul 2>&1

echo [完成] 飞书机器人已停止
echo.
pause
