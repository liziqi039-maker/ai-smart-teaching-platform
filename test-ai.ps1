Write-Host "🔍 AI微服务诊断测试" -ForegroundColor Cyan
Write-Host "="*50

# 测试基础连接
Write-Host "1. 测试基础连接..." -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3001" -Method Get -TimeoutSec 3
    Write-Host "   ✅ 基础连接成功" -ForegroundColor Green
    Write-Host "   消息: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ 基础连接失败: $_" -ForegroundColor Red
}

# 测试健康检查
Write-Host "`n2. 测试健康检查..." -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/health" -Method Get -TimeoutSec 3
    Write-Host "   ✅ 健康检查成功" -ForegroundColor Green
    Write-Host "   状态: $($response.message)" -ForegroundColor Gray
    Write-Host "   版本: $($response.version)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ 健康检查失败: $_" -ForegroundColor Red
}

# 测试AI聊天功能
Write-Host "`n3. 测试AI聊天功能..." -ForegroundColor White
try {
    $body = @{
        messages = @(
            @{role = "user"; content = "你好，请回复'AI连接测试成功'"}
        )
    } | ConvertTo-Json -Depth 10
    
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "   ✅ AI聊天成功" -ForegroundColor Green
    Write-Host "   回答: $($response.data.answer)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ AI聊天失败: $_" -ForegroundColor Red
}

# 测试PPT生成功能
Write-Host "`n4. 测试PPT生成功能..." -ForegroundColor White
try {
    $body = @{
        topic = "人工智能简介"
        slides = 5
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/ppt/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "   ✅ PPT生成成功" -ForegroundColor Green
    Write-Host "   主题: $($response.data.topic)" -ForegroundColor Gray
    Write-Host "   幻灯片数: $($response.data.totalSlides)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ PPT生成失败: $_" -ForegroundColor Red
}

# 测试测验生成功能
Write-Host "`n5. 测试测验生成功能..." -ForegroundColor White
try {
    $body = @{
        topic = "Python基础"
        difficulty = "medium"
        count = 3
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/quiz/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "   ✅ 测验生成成功" -ForegroundColor Green
    Write-Host "   主题: $($response.data.topic)" -ForegroundColor Gray
    Write-Host "   问题数: $($response.data.questionCount)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ 测验生成失败: $_" -ForegroundColor Red
}

# 测试高级功能
Write-Host "`n6. 测试高级功能..." -ForegroundColor White
Write-Host "   a) 测试PPT生成(原版)..." -ForegroundColor Gray
try {
    $body = @{
        topic = "深度学习"
        slides = 8
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/generate-ppt" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "      ✅ 高级PPT生成成功" -ForegroundColor Green
} catch {
    Write-Host "      ❌ 高级PPT生成失败" -ForegroundColor Red
}

Write-Host "`n   b) 测试AI直播助手..." -ForegroundColor Gray
try {
    $body = @{
        question = "什么是机器学习？"
        context = "教学场景"
        sessionId = "test_session_123"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/v1/ai/live-assistant" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host "      ✅ AI直播助手成功" -ForegroundColor Green
} catch {
    Write-Host "      ❌ AI直播助手失败" -ForegroundColor Red
}

Write-Host "`n="*50

# 总结报告
Write-Host "📊 诊断总结:" -ForegroundColor Cyan
Write-Host "服务状态: 如果所有基础功能(1-5)都显示✅，则AI微服务可用" -ForegroundColor White
Write-Host "高级功能: 如果第6项显示✅，则所有高级功能也可用" -ForegroundColor White
Write-Host "`n🎯 下一步:" -ForegroundColor Yellow
Write-Host "1. 访问 http://localhost:3000/ai-test.html 测试前端" -ForegroundColor Green
Write-Host "2. 或访问 http://localhost:3001/ 查看服务状态" -ForegroundColor Green
