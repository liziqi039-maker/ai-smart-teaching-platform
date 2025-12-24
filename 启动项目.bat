@echo off
chcp 65001 >nul
title AI智慧教学平台 - 快速启动
color 0A

echo.
echo ╔════════════════════════════════════════╗
echo ║   AI智慧教学平台 - 快速启动           ║
echo ╚════════════════════════════════════════╝
echo.

REM 切换到项目目录
cd /d "%~dp0"
echo 当前目录: %CD%
echo.

REM 检查 Python
echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 Python！请从 https://www.python.org/downloads/ 安装
    pause
    exit /b 1
)
python --version
echo [✓] Python 检查通过
echo.

REM 检查 Node.js
echo [2/3] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未安装 Node.js！请从 https://nodejs.org/ 安装
    pause
    exit /b 1
)
node --version
echo [✓] Node.js 检查通过
echo.

REM 启动服务
echo [3/3] 启动服务...
echo.

echo 正在启动后端服务 (Flask)...
start "后端服务" cmd /k "cd /d %~dp0backend && python -m venv venv 2>nul & call venv\Scripts\activate & pip install -q flask flask-cors flask-sqlalchemy flask-jwt-extended 2>nul & python app.py"

echo 等待后端启动...
timeout /t 5 /nobreak >nul

echo 正在启动前端服务 (Vite)...
start "前端服务" cmd /k "cd /d %~dp0frontend && npm run dev 2>nul || npx vite"

echo.
echo ╔════════════════════════════════════════╗
echo ║          启动完成！                    ║
echo ╚════════════════════════════════════════╝
echo.
echo   📍 访问地址:
echo      前端: http://localhost:3000
echo      后端: http://localhost:8000
echo.
echo   👥 测试账号:
echo      教师: teacher001 / 123456
echo      学生: student001 / 123456
echo.
echo   💡 提示:
echo      - 已打开两个新窗口(后端和前端)
echo      - 关闭那两个窗口可以停止服务
echo      - 首次启动需要安装依赖,请耐心等待
echo.

timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"

echo 正在打开浏览器...
echo.
echo 按任意键关闭此窗口...
pause >nul
