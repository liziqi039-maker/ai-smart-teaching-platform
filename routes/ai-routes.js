const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const config = require('../config.js');

// 配置文件上传
const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB
});

// ==================== AI核心功能路由 ====================

// 1. 语音识别
router.post('/speech-to-text', upload.single('audio'), async (req, res) => {
  try {
    const { language } = req.body;
    const audioFile = req.file;
    
    console.log('🎤 语音识别请求:', { language, file: audioFile?.originalname });
    
    // 根据配置选择语音识别服务
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

// 2. PPT生成
router.post('/generate-ppt', async (req, res) => {
  try {
    const { topic, outline, style, slides = 12 } = req.body;
    
    console.log('📊 PPT生成请求:', { topic, slides });
    
    // 调用AI服务生成PPT
    const pptResult = {
      pptId: `ppt_${Date.now()}`,
      topic: topic || 'AI教学平台介绍',
      slides: generateSlides(topic, slides),
      totalSlides: slides,
      estimatedTime: slides * 2.5, // 每页2.5秒
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

// 3. 视频生成
router.post('/generate-video', upload.single('ppt'), async (req, res) => {
  try {
    const pptFile = req.file;
    const { voice, speed, resolution } = req.body;
    
    console.log('🎥 视频生成请求:', { 
      file: pptFile?.originalname, 
      voice, 
      resolution 
    });
    
    const videoResult = {
      videoId: `video_${Date.now()}`,
      pptName: pptFile?.originalname || '演示文稿.pptx',
      duration: 300, // 5分钟
      resolution: resolution || '1920x1080',
      status: 'processing',
      progress: 0,
      estimatedTime: 120, // 2分钟
      downloadUrl: `/api/v1/ai/download/video_${Date.now()}.mp4`,
      createdAt: new Date().toISOString()
    };
    
    res.json({
      success: true,
      data: videoResult
    });
  } catch (error) {
    console.error('视频生成失败:', error);
    res.status(500).json({
      success: false,
      message: '视频生成失败',
      error: error.message
    });
  }
});

// 4. AI直播助手
router.post('/live-assistant', async (req, res) => {
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

// ==================== 演示系统路由（从ai-routes.js提取） ====================

// 创建演示会话
router.post('/demo/session', async (req, res) => {
  try {
    console.log('📝 创建演示会话请求:', req.body);
    
    const sessionData = {
      sessionId: 'demo_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
      createdAt: new Date(),
      status: 'active',
      steps: [],
      currentStep: 0,
      userId: req.body.userId || 'demo_user_' + Date.now(),
      demoType: req.body.demoType || 'full'
    };
    
    // 初始化演示会话存储
    if (!global.demoSessions) {
      global.demoSessions = {};
    }
    global.demoSessions[sessionData.sessionId] = sessionData;
    
    console.log('✅ 演示会话创建成功:', sessionData.sessionId);
    
    res.json({
      success: true,
      sessionId: sessionData.sessionId,
      message: '演示会话创建成功',
      session: sessionData
    });
  } catch (error) {
    console.error('❌ 创建演示会话失败:', error);
    res.status(500).json({
      success: false,
      message: '创建演示会话失败',
      error: error.message
    });
  }
});

// 获取演示会话
router.get('/demo/session/:sessionId', (req, res) => {
  try {
    const { sessionId } = req.params;
    console.log('📋 获取演示会话:', sessionId);
    
    if (!global.demoSessions || !global.demoSessions[sessionId]) {
      console.log('❌ 演示会话不存在:', sessionId);
      return res.status(404).json({
        success: false,
        message: '演示会话不存在'
      });
    }
    
    const session = global.demoSessions[sessionId];
    console.log('✅ 找到演示会话:', sessionId);
    
    res.json({
      success: true,
      session: session
    });
  } catch (error) {
    console.error('❌ 获取演示会话失败:', error);
    res.status(500).json({
      success: false,
      message: '获取演示会话失败',
      error: error.message
    });
  }
});

// ==================== 辅助函数 ====================

// 调用百度语音API
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

// 生成PPT幻灯片
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

// ==================== 导出路由 ====================
module.exports = router;