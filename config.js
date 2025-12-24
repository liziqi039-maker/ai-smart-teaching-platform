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

  
  // 语音识别配置
  speech: {
    baidu: {
      appId: process.env.BAIDU_APP_ID || '',
      apiKey: process.env.BAIDU_API_KEY || '',
      secretKey: process.env.BAIDU_SECRET_KEY || '',
      enabled: !!(process.env.BAIDU_APP_ID && process.env.BAIDU_API_KEY && process.env.BAIDU_SECRET_KEY)
    },
    aliyun: {
      accessKeyId: process.env.ALIYUN_ACCESS_KEY_ID || '',
      accessKeySecret: process.env.ALIYUN_ACCESS_KEY_SECRET || ''
    }
  },
  
  // 文件上传配置
  upload: {
    maxSize: process.env.MAX_FILE_SIZE || '50MB',
    directory: './uploads'
  },
  
  // 演示配置
  demo: {
    sessionTimeout: 30 * 60 * 1000, // 30分钟
    maxSessions: 100
  },
  
  // 系统监控配置
  monitoring: {
    enabled: true,
    logLevel: process.env.LOG_LEVEL || 'info',
    logDirectory: './logs'
  }
};