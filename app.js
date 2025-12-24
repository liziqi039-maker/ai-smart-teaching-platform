// ai-service/app.js - 合并版本（包含所有路由）
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:8000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
}));

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// 配置文件上传
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB
});

// 导入配置
const config = require('./config.js');
console.log(`🔧 AI提供商: ${config.ai.provider}`);

// 创建必要的目录
const uploadsDir = path.join(__dirname, 'uploads');
const downloadsDir = path.join(__dirname, 'downloads');

if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
  console.log(`✅ 创建上传目录: ${uploadsDir}`);
}

if (!fs.existsSync(downloadsDir)) {
  fs.mkdirSync(downloadsDir, { recursive: true });
  console.log(`✅ 创建下载目录: ${downloadsDir}`);
}

// ==================== AI路由定义 ====================

// 健康检查
app.get('/api/v1/ai/health', (req, res) => {
  console.log('🏥 健康检查请求');
  res.json({
    success: true,
    message: 'AI微服务运行正常',
    version: '2.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      chat: '/api/v1/ai/chat',
      ppt: '/api/v1/ai/ppt/generate',
      quiz: '/api/v1/ai/quiz/generate',
      speech: '/api/v1/ai/speech-to-text',
      pptGenerate: '/api/v1/ai/generate-ppt',
      liveAssistant: '/api/v1/ai/live-assistant'
    }
  });
});

// AI聊天
app.post('/api/v1/ai/chat', (req, res) => {
  try {
    const { messages } = req.body;
    console.log('💬 AI聊天请求:', messages?.length || 0, '条消息');
    
    const lastMessage = messages?.[messages.length - 1]?.content || '你好';
    
    res.json({
      success: true,
      data: {
        answer: `您好！我是AI助教。您刚才说："${lastMessage}"`,
        model: config.ai.provider === 'zhipu' ? 'glm-4' : 'doubao',
        provider: config.ai.provider,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('AI聊天错误:', error);
    res.status(500).json({
      success: false,
      message: 'AI聊天失败',
      error: error.message
    });
  }
});

// PPT生成（简化版）
app.post('/api/v1/ai/ppt/generate', (req, res) => {
  try {
    const { topic, outline, slides, style } = req.body;
    console.log('📊 PPT生成请求（简化版）:', { topic, slides });
    
    res.json({
      success: true,
      data: {
        pptId: `ppt_${Date.now()}`,
        topic: topic || 'AI教学平台介绍',
        slides: generateSimpleSlides(topic, slides || 10),
        totalSlides: slides || 10,
        downloadUrl: `/api/v1/ai/download/ppt_${Date.now()}.pptx`,
        previewUrl: `/api/v1/ai/preview/ppt_${Date.now()}.jpg`,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('PPT生成错误:', error);
    res.status(500).json({
      success: false,
      message: 'PPT生成失败',
      error: error.message
    });
  }
});

// 测验生成
app.post('/api/v1/ai/quiz/generate', (req, res) => {
  try {
    const { topic, difficulty, count } = req.body;
    console.log('📝 测验生成请求:', { topic, difficulty, count });
    
    const questions = generateQuizQuestions(topic, count || 5, difficulty || 'medium');
    
    res.json({
      success: true,
      data: {
        quizId: `quiz_${Date.now()}`,
        topic: topic || 'AI基础知识',
        difficulty: difficulty || 'medium',
        questionCount: questions.length,
        questions: questions,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('测验生成错误:', error);
    res.status(500).json({
      success: false,
      message: '测验生成失败',
      error: error.message
    });
  }
});

// 语音识别
app.post('/api/v1/ai/speech-to-text', upload.single('audio'), async (req, res) => {
  try {
    const { language } = req.body;
    const audioFile = req.file;
    
    console.log('🎤 语音识别请求:', { language, file: audioFile?.originalname });
    
    let result;
    if (config.speech.baidu.enabled) {
      // 百度语音识别
      result = await callBaiduSpeechAPI(audioFile.path, language);
    } else {
      // 模拟识别
      result = {
        text: "这是模拟的语音识别结果，系统可以实时将语音转换为文字，支持多种语言和方言。",
        confidence: 0.92,
        language: language || 'zh-CN',
        duration: audioFile ? Math.floor(audioFile.size / 16000) : 5.2,
        words: 25
      };
    }
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('语音识别失败:', error);
    res.status(500).json({
      success: false,
      message: '语音识别失败',
      error: error.message
    });
  }
});

// PPT生成（原版）
app.post('/api/v1/ai/generate-ppt', async (req, res) => {
  try {
    const { topic, outline, style, slides = 12 } = req.body;
    
    console.log('📊 PPT生成请求（原版）:', { topic, slides });
    
    const pptResult = {
      pptId: `ppt_${Date.now()}`,
      topic: topic || 'AI教学平台介绍',
      slides: generateSlides(topic, slides),
      totalSlides: slides,
      estimatedTime: slides * 2.5,
      downloadUrl: `/api/v1/ai/download/ppt_${Date.now()}.pptx`,
      previewUrl: `/api/v1/ai/preview/ppt_${Date.now()}.jpg`,
      status: 'generating',
      createdAt: new Date().toISOString()
    };
    
    res.json({
      success: true,
      data: pptResult
    });
  } catch (error) {
    console.error('PPT生成失败:', error);
    res.status(500).json({
      success: false,
      message: 'PPT生成失败',
      error: error.message
    });
  }
});

// AI直播助手
app.post('/api/v1/ai/live-assistant', async (req, res) => {
  try {
    const { question, context, userId, sessionId } = req.body;
    
    console.log('🤖 AI直播助手请求:', { 
      question: question?.substring(0, 50) + '...',
      sessionId 
    });
    
    const answer = await callAIProvider(question, context);
    
    res.json({
      success: true,
      data: {
        answer: answer.text,
        suggestions: answer.suggestions || ["建议1", "建议2", "建议3"],
        confidence: answer.confidence || 0.85,
        timestamp: new Date().toISOString(),
        sessionId: sessionId || `session_${Date.now()}`
      }
    });
  } catch (error) {
    console.error('AI直播助手失败:', error);
    res.status(500).json({
      success: false,
      message: 'AI助手响应失败',
      error: error.message
    });
  }
});

// ==================== 辅助函数 ====================

// 生成简单幻灯片
function generateSimpleSlides(topic, count) {
  const slides = [];
  for (let i = 1; i <= count; i++) {
    slides.push({
      slideNumber: i,
      title: `${topic || 'AI教学'} - 第${i}页`,
      content: `这是关于${topic || 'AI教学'}的第${i}页内容`,
      layout: i === 1 ? 'title' : 'content'
    });
  }
  return slides;
}

// 生成测验问题
function generateQuizQuestions(topic, count, difficulty) {
  const questions = [];
  const questionTypes = ['multiple_choice', 'true_false', 'short_answer'];
  
  for (let i = 1; i <= count; i++) {
    const type = questionTypes[i % questionTypes.length];
    const question = {
      id: i,
      type: type,
      question: `${topic}相关的${difficulty}难度问题 ${i}`,
      difficulty: difficulty
    };
    
    if (type === 'multiple_choice') {
      question.options = ['正确选项', '干扰项A', '干扰项B', '干扰项C'];
      question.answer = '正确选项';
    } else if (type === 'true_false') {
      question.options = ['正确', '错误'];
      question.answer = Math.random() > 0.5 ? '正确' : '错误';
    } else {
      question.answer = `这是关于${topic}的简答题参考答案 ${i}`;
    }
    
    questions.push(question);
  }
  
  return questions;
}

// 调用百度语音API
async function callBaiduSpeechAPI(audioPath, language) {
  // 实际项目中这里调用百度API
  return {
    text: "百度语音识别结果",
    confidence: 0.95,
    language: language || 'zh-CN',
    duration: 3.5
  };
}

// 调用AI提供商
async function callAIProvider(question, context) {
  // 根据config.ai.provider调用相应的AI服务
  if (config.ai.provider === 'zhipu' && config.ai.zhipu.apiKey) {
    // 调用智谱AI
    return {
      text: "这是来自智谱AI的回答",
      suggestions: ["扩展阅读1", "实践建议1"],
      confidence: 0.88
    };
  } else if (config.ai.provider === 'doubao' && config.ai.doubao.apiKey) {
    // 调用豆包AI
    return {
      text: "这是来自豆包AI的回答",
      suggestions: ["豆包建议1", "豆包建议2"],
      confidence: 0.87
    };
  } else {
    // 模拟响应
    return {
      text: "这是AI助教的回答，基于您的问题和上下文生成。系统可以处理多种教学场景，包括答疑解惑、知识点讲解、学习建议等。",
      suggestions: ["查看相关课程视频", "完成配套练习", "参与在线讨论"],
      confidence: 0.85
    };
  }
}

// 生成PPT幻灯片（原版）
function generateSlides(topic, count) {
  const slides = [];
  for (let i = 1; i <= count; i++) {
    slides.push({
      title: `${topic} - 第${i}页`,
      content: `这是关于${topic}的第${i}页内容`,
      slideNumber: i,
      layout: i === 1 ? 'title' : i % 2 === 0 ? 'content' : 'image',
      estimatedTime: 2.5
    });
  }
  return slides;
}

// ==================== 根路由和全局路由 ====================

// 根路由
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'AI微服务运行正常',
    version: '2.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      health: '/api/v1/ai/health',
      chat: '/api/v1/ai/chat',
      ppt: '/api/v1/ai/ppt/generate',
      quiz: '/api/v1/ai/quiz/generate',
      speech: '/api/v1/ai/speech-to-text',
      pptAdvanced: '/api/v1/ai/generate-ppt',
      assistant: '/api/v1/ai/live-assistant'
    }
  });
});

// 404处理
app.use((req, res, next) => {
  res.status(404).json({
    success: false,
    message: `找不到路由: ${req.method} ${req.url}`,
    availableRoutes: [
      'GET    /',
      'GET    /api/v1/ai/health',
      'POST   /api/v1/ai/chat',
      'POST   /api/v1/ai/ppt/generate',
      'POST   /api/v1/ai/quiz/generate',
      'POST   /api/v1/ai/speech-to-text',
      'POST   /api/v1/ai/generate-ppt',
      'POST   /api/v1/ai/live-assistant'
    ]
  });
});

// 全局错误处理
app.use((err, req, res, next) => {
  console.error('❌ 服务器错误:', err);
  res.status(500).json({
    success: false,
    message: '服务器内部错误',
    error: err.message,
    timestamp: new Date().toISOString()
  });
});

// 启动服务器
const server = app.listen(PORT, () => {
  console.log(`
=======================================
🤖 AI微服务启动成功！
=======================================
📡 服务地址: http://localhost:${PORT}
🌐 前端地址: http://localhost:3000
🔧 AI提供商: ${config.ai.provider}
📊 语音识别: ${config.speech.baidu.enabled ? '已启用' : '未启用'}
🎯 可用端点:
   - 健康检查: GET  /api/v1/ai/health
   - AI聊天:    POST /api/v1/ai/chat
   - PPT生成:   POST /api/v1/ai/ppt/generate
   - 测验生成:  POST /api/v1/ai/quiz/generate
   - 语音识别:  POST /api/v1/ai/speech-to-text
   - PPT高级:   POST /api/v1/ai/generate-ppt
   - AI助手:    POST /api/v1/ai/live-assistant
=======================================
    `);
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('🔄 收到关闭信号，正在优雅关闭...');
  server.close(() => {
    console.log('✅ AI微服务已关闭');
    process.exit(0);
  });
});

module.exports = app;
