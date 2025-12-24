# DeepSeek AI集成指南

本文档说明如何将AI教学平台的AI接口从豆包/智谱清言迁移到DeepSeek。

## 📋 已完成的优化

### 1. 环境变量配置 ✅
已更新 `.env.example` 文件，添加DeepSeek配置：
```env
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### 2. 后端配置 ✅
已更新 `backend/config.py`，添加DeepSeek支持，优先使用DeepSeek，保留旧配置作为备用。

### 3. 后端AI路由 ✅
已完全重写 `backend/routes/ai.py`，使用DeepSeek API（OpenAI兼容格式）。

新增功能：
- ✨ `POST /api/v1/ai/chat` - AI对话聊天
- ✨ `POST /api/v1/ai/ppt/generate` - 生成PPT大纲
- ✨ `POST /api/v1/ai/quiz/generate` - 生成测验题目
- ✨ `POST /api/v1/ai/analyze` - 内容分析
- ✨ `GET /api/v1/ai/status` - AI服务状态检查
- ✨ `GET /api/v1/ai/health` - 健康检查

## 🔧 需要手动完成的步骤

### 步骤1: 更新AI-Service配置 (需手动操作)

由于文件权限限制，需要手动更新 `ai-service/config.js`：

```javascript
// ai-service/config.js - 更新AI配置部分
ai: {
  provider: process.env.AI_PROVIDER || 'deepseek',

  // 1. DeepSeek配置 (推荐)
  deepseek: {
    apiKey: process.env.DEEPSEEK_API_KEY || '',
    apiUrl: process.env.DEEPSEEK_API_URL || 'https://api.deepseek.com/v1',
    model: process.env.DEEPSEEK_MODEL || 'deepseek-chat'
  },

  // 2. 豆包配置 (已弃用，保留兼容性)
  doubao: {
    apiKey: process.env.DOUBAO_API_KEY || ''
  },

  // 3. 智谱清言配置 (已弃用，保留兼容性)
  zhipu: {
    apiKey: process.env.ZHIPU_API_KEY || ''
  },

  // 4. OpenAI配置 (备用)
  openai: {
    apiKey: process.env.OPENAI_API_KEY || ''
  }
},
```

### 步骤2: 更新AI-Service路由 (可选)

可选择更新 `ai-service/routes/ai-routes.js` 中的 `callAIProvider` 函数以使用DeepSeek：

```javascript
// 在 ai-routes.js 中更新 callAIProvider 函数
async function callAIProvider(question, context) {
  const config = require('../config.js');

  // 优先使用DeepSeek
  if (config.ai.provider === 'deepseek' && config.ai.deepseek.apiKey) {
    try {
      const axios = require('axios');
      const response = await axios.post(
        `${config.ai.deepseek.apiUrl}/chat/completions`,
        {
          model: config.ai.deepseek.model,
          messages: [
            { role: 'system', content: '你是一个专业的AI助教，请回答学生的问题。' },
            { role: 'user', content: question }
          ],
          temperature: 0.7,
          max_tokens: 2000
        },
        {
          headers: {
            'Authorization': `Bearer ${config.ai.deepseek.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const aiResponse = response.data.choices[0].message.content;
      return {
        text: aiResponse,
        suggestions: ["查看相关课程", "完成配套练习", "参与在线讨论"],
        confidence: 0.90
      };
    } catch (error) {
      console.error('DeepSeek API调用失败:', error.message);
      // 降级到模拟响应
    }
  }

  // 模拟响应（备用）
  return {
    text: "这是AI助教的回答，基于您的问题和上下文生成。",
    suggestions: ["查看相关课程视频", "完成配套练习", "参与在线讨论"],
    confidence: 0.85
  };
}
```

### 步骤3: 配置.env文件

1. 复制 `.env.example` 到 `.env`：
```bash
cp .env.example .env
```

2. 在 `.env` 文件中添加您的DeepSeek API密钥：
```env
# ========== AI服务配置 ==========
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 设置AI服务模式为直接模式
AI_SERVICE_MODE=direct
```

### 步骤4: 安装必要的依赖

确保已安装 `axios`（用于Node.js服务）：
```bash
cd ai-service
npm install axios
```

## 🚀 如何获取DeepSeek API Key

1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入"API密钥"页面
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

## 📊 API使用示例

### 1. 聊天接口
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "什么是人工智能?"}
    ]
  }'
```

### 2. PPT生成接口
```bash
curl -X POST http://localhost:8000/api/v1/ai/ppt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python编程入门",
    "slides": 10,
    "style": "professional"
  }'
```

### 3. 题目生成接口
```bash
curl -X POST http://localhost:8000/api/v1/ai/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Python是一种高级编程语言...",
    "type": "multiple_choice",
    "num": 5,
    "difficulty": "medium"
  }'
```

### 4. 状态检查
```bash
curl http://localhost:8000/api/v1/ai/status
```

## 🔍 测试验证

启动后端服务后，访问健康检查端点：
```bash
curl http://localhost:8000/api/v1/ai/health
```

预期响应：
```json
{
  "success": true,
  "message": "AI服务运行正常 (DeepSeek)",
  "provider": "DeepSeek",
  "timestamp": "2025-12-24T..."
}
```

## 📝 优化亮点

1. **OpenAI兼容格式** - DeepSeek使用OpenAI兼容的API格式，易于迁移
2. **统一接口** - 所有AI功能通过统一的 `call_deepseek_api` 函数调用
3. **完善错误处理** - 包含超时处理、异常捕获和详细错误信息
4. **灵活配置** - 支持自定义temperature、max_tokens等参数
5. **向后兼容** - 保留原有API接口路径，不影响前端调用
6. **降级策略** - 保留旧AI配置作为备用方案

## ⚡ 性能优化建议

1. **启用流式响应**（可选）：在长文本生成时使用stream=true
2. **调整timeout**：根据实际网络情况调整请求超时时间
3. **缓存策略**：对于相同的问题可以考虑缓存响应结果
4. **并发控制**：使用连接池限制并发请求数量

## 🔒 安全注意事项

1. ⚠️ **永远不要**将API密钥提交到Git仓库
2. ✅ 在生产环境中使用环境变量管理密钥
3. ✅ 定期轮换API密钥
4. ✅ 设置API调用频率限制
5. ✅ 记录所有API调用以便监控和审计

## 📚 相关资源

- [DeepSeek API文档](https://platform.deepseek.com/docs)
- [OpenAI API参考](https://platform.openai.com/docs/api-reference)（格式兼容）
- 项目配置文件：`backend/config.py`、`ai-service/config.js`
- AI路由：`backend/routes/ai.py`

## 🆘 故障排查

### 问题1: API密钥未配置
**错误**: "DeepSeek API Key未配置"
**解决**: 检查 `.env` 文件中是否正确设置了 `DEEPSEEK_API_KEY`

### 问题2: API调用超时
**错误**: "DeepSeek API请求超时"
**解决**:
- 检查网络连接
- 增加timeout配置
- 检查API服务状态

### 问题3: 响应格式异常
**错误**: "AI返回结果格式异常"
**解决**:
- 检查API URL是否正确
- 验证API密钥是否有效
- 查看完整错误日志

## ✅ 验证清单

- [ ] `.env` 文件已配置DeepSeek API密钥
- [ ] `ai-service/config.js` 已更新DeepSeek配置
- [ ] 后端服务可以正常启动
- [ ] `/api/v1/ai/health` 端点返回成功
- [ ] `/api/v1/ai/status` 显示DeepSeek状态为healthy
- [ ] 可以成功调用 `/api/v1/ai/chat` 接口
- [ ] PPT生成功能正常工作
- [ ] 题目生成功能正常工作

完成以上步骤后，您的AI教学平台将成功集成DeepSeek AI服务！
