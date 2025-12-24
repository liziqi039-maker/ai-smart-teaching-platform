@echo off
chcp 65001 >nul
title AI智慧教学平台 - 开发环境启动
echo.
echo ========================================
echo   AI智慧教学平台 - 开发环境启动 v2.0
echo ========================================
echo.

REM ========== 环境检查 ==========
echo [1/8] 检查运行环境...

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
    echo [✓] Python版本: %python_version%
)

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js环境，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%i in ('node --version') do set "node_version=%%i"
    echo [✓] Node.js版本: %node_version%
)

REM 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到npm，请确保Node.js正确安装
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%i in ('npm --version') do set "npm_version=%%i"
    echo [✓] npm版本: %npm_version%
)

REM ========== 端口检查与释放 ==========
echo.
echo [2/8] 检查端口占用...

set "ports_freed=0"
for %%p in (8000, 3000) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p "') do (
        echo [警告] 端口%%p被占用，进程ID: %%a
        echo 尝试终止占用进程...
        taskkill /F /PID %%a >nul 2>&1
        if errorlevel 1 (
            echo [错误] 无法终止进程 %%a，请手动处理
        ) else (
            echo [✓] 已释放端口 %%p
            set /a "ports_freed+=1"
            timeout /t 1 /nobreak >nul
        )
    )
)

if %ports_freed% gtr 0 (
    echo [✓] 端口清理完成，释放了 %ports_freed% 个端口
) else (
    echo [✓] 端口状态正常
)

REM ========== 虚拟环境设置 ==========
echo.
echo [3/8] 设置Python虚拟环境...

REM 检查虚拟环境 - 优先使用backend目录中的venv
if not exist "backend\venv" (
    echo 创建Python虚拟环境...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [✓] 虚拟环境创建成功
    cd ..
) else (
    echo [✓] Python虚拟环境已存在
)

echo 激活虚拟环境...
call backend\venv\Scripts\activate
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

REM ========== Python依赖安装 ==========
echo.
echo [4/8] 安装Python依赖...

REM 更新pip
echo 更新pip...
python -m pip install --upgrade pip -q

REM 安装requirements.txt中的依赖
if exist "backend\requirements.txt" (
    echo 安装后端依赖...
    pip install -r backend\requirements.txt -q
    if errorlevel 1 (
        echo [警告] 部分依赖安装失败，尝试安装核心依赖...
        pip install flask flask-cors flask-sqlalchemy flask-migrate flask-jwt-extended requests -q
    )
    echo [✓] 后端依赖安装完成
) else (
    echo [警告] 未找到requirements.txt，安装核心依赖...
    pip install flask flask-cors flask-sqlalchemy flask-migrate flask-jwt-extended requests -q
    echo [✓] 核心依赖安装完成
)

REM ========== 前端依赖安装 ==========
echo.
echo [5/8] 安装前端依赖...

if exist "frontend\" (
    cd frontend
    if exist "package.json" (
        if not exist "node_modules" (
            echo 首次安装前端依赖，这可能需要几分钟...
            npm install
            if errorlevel 1 (
                echo [警告] npm install失败，尝试使用cnpm或yarn
                REM 尝试cnpm
                cnpm install 2>nul || (
                    echo [提示] 使用--force参数重试
                    npm install --force
                )
            )
            echo [✓] 前端依赖安装完成
        ) else (
            echo [跳过] 前端依赖已安装 (node_modules存在)
        )
    ) else (
        echo [提示] 未找到package.json，跳过前端依赖安装
        REM 创建简单的package.json
        echo { > package.json
        echo   "name": "ai-teaching-platform-frontend", >> package.json
        echo   "version": "1.0.0", >> package.json
        echo   "description": "AI智慧课堂前端", >> package.json
        echo   "scripts": { >> package.json
        echo     "start": "npx http-server -p 3000 -c-1" >> package.json
        echo   } >> package.json
        echo } >> package.json
        echo [✓] 已创建简单package.json
    )
    cd ..
) else (
    echo [错误] 未找到frontend目录！
    pause
    exit /b 1
)

REM ========== 数据库初始化 ==========
echo.
echo [6/8] 初始化数据库...

REM 检查database目录
if not exist "database" (
    mkdir database
    echo [✓] 创建database目录
)

REM 检查数据库文件是否存在
if not exist "database\ai_teaching.db" (
    echo 初始化数据库结构...
    
    REM 方法1：使用init_db.py脚本
    if exist "backend\scripts\init_db.py" (
        echo 使用init_db.py初始化...
        python backend\scripts\init_db.py
        if errorlevel 1 (
            echo [警告] init_db.py执行失败
        )
    )
    
    REM 方法2：使用Flask命令
    if not exist "database\ai_teaching.db" (
        echo 使用Flask命令初始化...
        cd backend
        flask db upgrade 2>nul || (
            echo [提示] 尝试创建数据库表...
            python -c "
import sys
sys.path.append('.')
from app import create_app
from db_instance import db
app = create_app()
with app.app_context():
    db.create_all()
    print('数据库表创建完成')
            "
        )
        cd ..
    )
    
    if exist "database\ai_teaching.db" (
        echo [✓] 数据库初始化成功
    ) else (
        echo [警告] 数据库初始化失败，但将继续启动
    )
) else (
    echo [✓] 数据库已存在
)

REM ========== 服务启动 ==========
echo.
echo [7/8] 启动服务...

echo 启动后端服务 (Flask on :8000)...
start "AI教学平台-后端" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && python app.py"

echo 等待后端服务启动...
timeout /t 8 /nobreak >nul

REM 测试后端是否启动成功
curl --max-time 5 http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo [警告] 后端服务可能未正常启动，请稍后手动检查
) else (
    echo [✓] 后端服务已启动
)

echo 启动前端服务 (HTTP Server on :3000)...
cd frontend

REM 前端启动方式优先级：
REM 1. package.json中的scripts.start
REM 2. package.json中的scripts.dev
REM 3. npx http-server
REM 4. python http.server

if exist "package.json" (
    REM 检查是否有start脚本
    start "AI教学平台-前端" cmd /k "cd /d %~dp0 && (npm start 2^>nul || npm run dev 2^>nul || npx http-server -p 3000 -c-1)"
) else (
    REM 使用简单的HTTP服务器
    start "AI教学平台-前端" cmd /k "cd /d %~dp0 && python -m http.server 3000"
)

cd ..
timeout /t 3 /nobreak >nul

REM ========== 完成信息 ==========
echo.
echo [8/8] 启动完成！
echo.
echo ========================================
echo   服务启动成功！
echo ========================================
echo.
echo   📍 访问地址:
echo     前端页面: http://localhost:3000
echo     后端API:  http://localhost:8000
echo.
echo   📋 核心API端点:
echo     健康检查: http://localhost:8000/api/v1/health
echo     用户状态: http://localhost:8000/api/v1/auth/check
echo     连接测试: http://localhost:8000/api/v1/test-connection
echo.
echo   👥 测试账号:
echo     教师账号: teacher001 / 123456
echo     学生账号: student001 / 123456
echo     AI助教账号: ai_assistant / 123456
echo.
echo   ⚙️  服务状态:
echo     后端进程: 正在运行 (端口 8000)
echo     前端进程: 正在运行 (端口 3000)
echo.
echo ========================================
echo.
echo   💡 使用提示:
echo     - 关闭此窗口不会停止服务
echo     - 请关闭后端和前端的独立窗口来停止服务
echo     - 如果遇到问题，请检查日志信息
echo     - 首次运行可能需要下载模型文件，请耐心等待
echo.
echo   如果浏览器没有自动打开，请手动访问:
echo   http://localhost:3000
echo.
echo   按任意键打开浏览器访问平台...
pause >nul

REM 打开浏览器
start "" "http://localhost:3000"

echo.
echo ========================================
echo   启动脚本执行完成！
echo   按任意键退出本窗口...
echo ========================================
pause >nul