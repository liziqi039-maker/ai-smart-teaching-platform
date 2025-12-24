Write-Host "🎯 AI功能最终测试" -ForegroundColor Cyan
Write-Host "="*60

# 检查AI微服务是否运行
Write-Host "1. 检查AI微服务状态..." -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/health" -Method Get -TimeoutSec 5
    if ($response.success -eq $true) {
        Write-Host "   ✅ AI微服务运行正常" -ForegroundColor Green
        Write-Host "   消息: $($response.message)" -ForegroundColor Gray
        Write-Host "   版本: $($response.version)" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️ AI微服务响应异常" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ AI微服务未运行或无法访问" -ForegroundColor Red
    Write-Host "   请确保已运行: node app.js" -ForegroundColor Yellow
    exit 1
}

# 测试所有主要端点
Write-Host "`n2. 测试所有AI功能端点..." -ForegroundColor White

$endpoints = @(
    @{Name="AI聊天"; Path="/chat"; Method="POST"; Body=@{messages=@(@{role="user";content="你好，测试AI聊天功能"})}},
    @{Name="PPT生成"; Path="/ppt/generate"; Method="POST"; Body=@{topic="测试主题"; slides=5}},
    @{Name="测验生成"; Path="/quiz/generate"; Method="POST"; Body=@{topic="测试"; difficulty="easy"; count=3}},
    @{Name="高级PPT"; Path="/generate-ppt"; Method="POST"; Body=@{topic="高级测试"; slides=8}},
    @{Name="AI助手"; Path="/live-assistant"; Method="POST"; Body=@{question="什么是AI？"; context="测试"}}
)

foreach ($endpoint in $endpoints) {
    $url = "http://localhost:3001/api/v1/ai" + $endpoint.Path
    
    try {
        if ($endpoint.Method -eq "POST") {
            $bodyJson = $endpoint.Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $url -Method $endpoint.Method -Body $bodyJson -ContentType "application/json" -TimeoutSec 5
        } else {
            $response = Invoke-RestMethod -Uri $url -Method $endpoint.Method -TimeoutSec 5
        }
        
        if ($response.success -ne $false) {
            Write-Host "   ✅ $($endpoint.Name): 成功" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ $($endpoint.Name): 响应异常" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ $($endpoint.Name): 失败" -ForegroundColor Red
        Write-Host "     错误: $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}

# 检查前端服务
Write-Host "`n3. 检查前端服务..." -ForegroundColor White
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Head -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   ✅ 前端服务运行正常 (端口 3000)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ 前端服务可能未运行" -ForegroundColor Yellow
    Write-Host "   请确保前端服务在端口 3000 运行" -ForegroundColor Gray
}

Write-Host "`n="*60
Write-Host "📊 测试结果总结" -ForegroundColor Cyan
Write-Host "如果看到多个✅，表示AI功能基本可用" -ForegroundColor White
Write-Host "`n🚀 下一步操作:" -ForegroundColor Yellow
Write-Host "1. 访问 http://localhost:3000/ai-test.html 进行详细测试" -ForegroundColor Green
Write-Host "2. 测试具体的AI功能模块" -ForegroundColor Green
Write-Host "3. 查看日志了解服务运行情况" -ForegroundColor Green
Write-Host "`n🔧 故障排除:" -ForegroundColor Cyan
Write-Host "- 如果测试失败，检查AI微服务是否运行: node app.js" -ForegroundColor Gray
Write-Host "- 查看端口占用: netstat -ano | findstr :3001" -ForegroundColor Gray
Write-Host "- 查看日志输出" -ForegroundColor Gray

# 等待用户确认
Write-Host "`n按 Enter 键打开测试页面，或按 Ctrl+C 退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 尝试打开测试页面
try {
    Start-Process "http://localhost:3000/ai-test.html"
} catch {
    Write-Host "无法自动打开浏览器，请手动访问" -ForegroundColor Yellow
}
