@echo off
chcp 65001 >nul
title AI智慧教学平台 - 调试启动
echo.
echo ========================================
echo   AI智慧教学平台 - 调试启动模式
echo ========================================
echo.
echo 当前目录: %CD%
echo.

REM 检查 Python
echo [检查 1/3] 检查 Python...
python --version
if errorlevel 1 (
    echo [错误] 未安装 Python！
    echo 请从 https://www.python.org/downloads/ 下载安装
    echo.
    pause
    exit /b 1
)
echo [✓] Python 检查通过
echo.

REM 检查 Node.js
echo [检查 2/3] 检查 Node.js...
node --version
if errorlevel 1 (
    echo [错误] 未安装 Node.js！
    echo 请从 https://nodejs.org/ 下载安装
    echo.
    pause
    exit /b 1
)
echo [✓] Node.js 检查通过
echo.

REM 检查项目结构
echo [检查 3/3] 检查项目结构...
if not exist "backend" (
    echo [错误] 未找到 backend 目录！
    echo 当前目录: %CD%
    dir
    echo.
    pause
    exit /b 1
)
if not exist "frontend" (
    echo [错误] 未找到 frontend 目录！
    echo 当前目录: %CD%
    dir
    echo.
    pause
    exit /b 1
)
echo [✓] 项目结构检查通过
echo.

echo ========================================
echo   所有检查通过！
echo   现在可以运行 start-dev.bat
echo ========================================
echo.
pause
