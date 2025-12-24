# start-all.ps1 - AI智慧课堂一键启动脚本
Write-Host "🚀 AI智慧课堂 - 一键启动所有服务" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor DarkGray

# 设置变量
$ProjectRoot = Get-Location
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendUrl = "http://localhost:8000"
$FrontendUrl = "http://localhost:3000"

Write-Host "📁 项目根目录: $ProjectRoot" -ForegroundColor Gray
Write-Host "📁 后端目录: $BackendDir" -ForegroundColor Gray
Write-Host "📁 前端目录: $FrontendDir" -ForegroundColor Gray
Write-Host "🔗 后端地址: $BackendUrl" -ForegroundColor Gray
Write-Host "🔗 前端地址: $FrontendUrl" -ForegroundColor Gray
Write-Host "="*60 -ForegroundColor DarkGray

# 函数：检查命令是否存在
function Test-Command {
    param([string]$CommandName)
    try {
        Get-Command $CommandName -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# 函数：检查端口是否被占用
function Test-Port {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            return @{
                Used = $true
                PID = $connection.OwningProcess
                ProcessName = $process.Name
            }
        }
        return @{Used = $false}
    } catch {
        return @{Used = $false}
    }
}

# 函数：终止占用端口的进程
function Stop-PortProcess {
    param([int]$Port, [string]$ServiceName)
    $portInfo = Test-Port -Port $Port
    if ($portInfo.Used) {
        Write-Host "   ⚠️  端口 $Port 被 $($portInfo.ProcessName) (PID: $($portInfo.PID)) 占用" -ForegroundColor Yellow
        Write-Host "   尝试终止进程..." -ForegroundColor Gray
        try {
            Stop-Process -Id $portInfo.PID -Force -ErrorAction Stop
            Write-Host "   ✅ 已终止占用进程" -ForegroundColor Green
            Start-Sleep -Seconds 1
        } catch {
            Write-Host "   ❌ 无法终止进程: $_" -ForegroundColor Red
            return $false
        }
    }
    return $true
}

# 1. 检查环境
Write-Host "1. 检查运行环境..." -ForegroundColor Yellow

# 检查Python
if (Test-Command -CommandName "python") {
    $pythonVersion = python --version
    Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python 未安装" -ForegroundColor Red
    Write-Host "   请从 https://www.python.org/downloads/ 安装Python" -ForegroundColor Gray
    exit 1
}

# 检查Node.js
if (Test-Command -CommandName "node") {
    $nodeVersion = node --version
    Write-Host "   ✅ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Node.js 未安装" -ForegroundColor Red
    Write-Host "   请从 https://nodejs.org/ 安装Node.js" -ForegroundColor Gray
    exit 1
}

# 检查npm
if (Test-Command -CommandName "npm") {
    $npmVersion = npm --version
    Write-Host "   ✅ npm: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ npm 未安装" -ForegroundColor Red
    exit 1
}

# 2. 检查端口占用
Write-Host "`n2. 检查端口占用..." -ForegroundColor Yellow

$portsToCheck = @(
    @{Port=8000; Service="后端API"},
    @{Port=3000; Service="前端服务"}
)

foreach ($portInfo in $portsToCheck) {
    $result = Test-Port -Port $portInfo.Port
    if ($result.Used) {
        Write-Host "   ⚠️  $($portInfo.Service)端口 $($portInfo.Port) 被占用" -ForegroundColor Yellow
        Write-Host "      进程: $($result.ProcessName) (PID: $($result.PID))" -ForegroundColor Gray
        
        $choice = Read-Host "   是否终止进程？(y/n)"
        if ($choice -eq 'y') {
            Stop-PortProcess -Port $portInfo.Port -ServiceName $portInfo.Service
        } else {
            Write-Host "   ⚠️  请手动释放端口或修改配置" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ✅ $($portInfo.Service)端口 $($portInfo.Port) 可用" -ForegroundColor Green
    }
}

# 3. 检查Python依赖
Write-Host "`n3. 检查Python依赖..." -ForegroundColor Yellow
$requiredPythonPackages = @("flask", "flask-cors", "flask-sqlalchemy", "flask-migrate", "flask-jwt-extended", "requests")

foreach ($package in $requiredPythonPackages) {
    try {
        python -c "import $($package.Replace('-', '_'))" 2>$null
        Write-Host "   ✅ $package" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  $package 未安装" -ForegroundColor Yellow
        $installChoice = Read-Host "   是否安装？(y/n)"
        if ($installChoice -eq 'y') {
            Write-Host "   正在安装 $package..." -ForegroundColor Gray
            pip install $package
        }
    }
}

# 4. 检查前端依赖
Write-Host "`n4. 检查前端依赖..." -ForegroundColor Yellow
if (Test-Path "$FrontendDir\package.json") {
    Write-Host "   ✅ 找到 package.json" -ForegroundColor Green
    
    # 检查是否有node_modules
    if (-not (Test-Path "$FrontendDir\node_modules")) {
        Write-Host "   ⚠️  node_modules 不存在" -ForegroundColor Yellow
        $installChoice = Read-Host "   是否安装依赖？(y/n)"
        if ($installChoice -eq 'y') {
            Set-Location $FrontendDir
            Write-Host "   正在安装依赖..." -ForegroundColor Gray
            npm install
            Set-Location $ProjectRoot
        }
    } else {
        Write-Host "   ✅ node_modules 存在" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  未找到 package.json" -ForegroundColor Yellow
    Write-Host "   前端可能需要手动配置" -ForegroundColor Gray
}

# 5. 启动后端服务
Write-Host "`n5. 启动后端服务..." -ForegroundColor Yellow

$backendScript = @"
cd "$BackendDir"
python app.py
"@

$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -PassThru
$backendPID = $backendProcess.Id

Write-Host "   ✅ 后端启动成功 (PID: $backendPID)" -ForegroundColor Green
Write-Host "   等待后端初始化..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 6. 启动前端服务
Write-Host "`n6. 启动前端服务..." -ForegroundColor Yellow

$frontendScript = @"
cd "$FrontendDir"
npm start
"@

$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -PassThru
$frontendPID = $frontendProcess.Id

Write-Host "   ✅ 前端启动成功 (PID: $frontendPID)" -ForegroundColor Green
Write-Host "   等待前端初始化..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# 7. 验证服务状态
Write-Host "`n7. 验证服务状态..." -ForegroundColor Yellow

# 测试后端
Write-Host "   测试后端连接..." -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/api/v1/health" -Method GET -TimeoutSec 5
    if ($response.success) {
        Write-Host "   ✅ 后端服务正常: $($response.message)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ 后端服务异常" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ 后端连接失败: $_" -ForegroundColor Red
}

# 测试前端
Write-Host "   测试前端连接..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri $FrontendUrl -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ 前端服务正常" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  前端返回状态: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ 前端连接失败: $_" -ForegroundColor Red
}

# 8. 显示信息和菜单
Write-Host "`n8. 服务状态和访问信息:" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor DarkGray
Write-Host "🔗 前端页面: $FrontendUrl" -ForegroundColor Green
Write-Host "🔗 后端API: $BackendUrl" -ForegroundColor Green
Write-Host "🔗 健康检查: $BackendUrl/api/v1/health" -ForegroundColor Green
Write-Host "🔗 用户状态: $BackendUrl/api/v1/auth/check" -ForegroundColor Green
Write-Host "🔗 测试连接: $BackendUrl/api/v1/test-connection" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor DarkGray

Write-Host "进程信息:" -ForegroundColor Cyan
Write-Host "   后端 (Flask): PID $backendPID" -ForegroundColor Gray
Write-Host "   前端 (Node.js): PID $frontendPID" -ForegroundColor Gray

# 9. 显示控制菜单
Write-Host "`n9. 控制菜单:" -ForegroundColor Cyan
Write-Host "   [1] 打开前端页面" -ForegroundColor Yellow
Write-Host "   [2] 测试所有API端点" -ForegroundColor Yellow
Write-Host "   [3] 查看进程状态" -ForegroundColor Yellow
Write-Host "   [4] 停止所有服务" -ForegroundColor Yellow
Write-Host "   [5] 重启所有服务" -ForegroundColor Yellow
Write-Host "   [6] 退出脚本（保持服务运行）" -ForegroundColor Yellow

# 10. 主循环
while ($true) {
    $choice = Read-Host "`n请选择操作 (1-6)"
    
    switch ($choice) {
        "1" {
            Write-Host "打开前端页面..." -ForegroundColor Cyan
            Start-Process $FrontendUrl
        }
        "2" {
            Write-Host "测试所有API端点..." -ForegroundColor Cyan
            $testUrls = @(
                "$BackendUrl/api/v1/health",
                "$BackendUrl/api/v1/auth/check",
                "$BackendUrl/api/v1/test-connection"
            )
            
            foreach ($url in $testUrls) {
                Write-Host "   测试 $url" -ForegroundColor Gray
                try {
                    $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 3
                    Write-Host "   ✅ $($response.message)" -ForegroundColor Green
                } catch {
                    Write-Host "   ❌ 连接失败: $_" -ForegroundColor Red
                }
            }
        }
        "3" {
            Write-Host "进程状态:" -ForegroundColor Cyan
            
            # 检查后端进程
            try {
                Get-Process -Id $backendPID -ErrorAction Stop | Out-Null
                Write-Host "   ✅ 后端进程运行中 (PID: $backendPID)" -ForegroundColor Green
            } catch {
                Write-Host "   ❌ 后端进程已停止" -ForegroundColor Red
            }
            
            # 检查前端进程
            try {
                Get-Process -Id $frontendPID -ErrorAction Stop | Out-Null
                Write-Host "   ✅ 前端进程运行中 (PID: $frontendPID)" -ForegroundColor Green
            } catch {
                Write-Host "   ❌ 前端进程已停止" -ForegroundColor Red
            }
            
            # 检查端口
            $ports = @(8000, 3000)
            foreach ($port in $ports) {
                $result = Test-Port -Port $port
                if ($result.Used) {
                    Write-Host "   ✅ 端口 $port 正在使用" -ForegroundColor Green
                } else {
                    Write-Host "   ❌ 端口 $port 未使用" -ForegroundColor Red
                }
            }
        }
        "4" {
            Write-Host "停止所有服务..." -ForegroundColor Cyan
            try {
                Stop-Process -Id $backendPID -Force -ErrorAction Stop
                Write-Host "   ✅ 已停止后端进程" -ForegroundColor Green
            } catch {
                Write-Host "   ⚠️  后端进程可能已停止" -ForegroundColor Yellow
            }
            
            try {
                Stop-Process -Id $frontendPID -Force -ErrorAction Stop
                Write-Host "   ✅ 已停止前端进程" -ForegroundColor Green
            } catch {
                Write-Host "   ⚠️  前端进程可能已停止" -ForegroundColor Yellow
            }
            
            Write-Host "所有服务已停止。脚本将在5秒后退出..." -ForegroundColor Green
            Start-Sleep -Seconds 5
            exit 0
        }
        "5" {
            Write-Host "重启所有服务..." -ForegroundColor Cyan
            
            # 停止现有进程
            try {
                Stop-Process -Id $backendPID -Force -ErrorAction SilentlyContinue
                Stop-Process -Id $frontendPID -Force -ErrorAction SilentlyContinue
            } catch {}
            
            Write-Host "正在重新启动..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
            
            # 重新启动脚本
            Write-Host "重新启动脚本..." -ForegroundColor Gray
            & "$PSCommandPath"
            exit 0
        }
        "6" {
            Write-Host "退出脚本，保持服务运行..." -ForegroundColor Cyan
            Write-Host "服务将继续在后台运行:" -ForegroundColor Gray
            Write-Host "   后端进程: $backendPID" -ForegroundColor Gray
            Write-Host "   前端进程: $frontendPID" -ForegroundColor Gray
            Write-Host "按 Enter 键退出..." -ForegroundColor Gray
            Read-Host
            exit 0
        }
        default {
            Write-Host "无效选择，请重新输入" -ForegroundColor Red
        }
    }
}