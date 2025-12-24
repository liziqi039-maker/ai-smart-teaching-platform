"""
配置文件 - 支持多模式AI服务集成
模式1: 直接模式 - Python后端直接调用豆包/智谱清言API
模式2: 网关模式 - Python后端通过Node.js AI服务中台调用AI（当前推荐）
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载环境变量文件: {env_path}")
else:
    print(f"⚠️  未找到环境变量文件: {env_path}，将使用默认配置")

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

class Config:
    """基础配置类"""
    
    # ========== 应用基础配置 ==========
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-teaching-platform-dev-secret-2024')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # ========== 数据库配置 ==========
    # 优先使用环境变量中的DATABASE_URI
    DATABASE_URI = os.getenv('DATABASE_URI')
    if DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = DATABASE_URI
    else:
        # 使用SQLite，确保database目录存在
        database_dir = BASE_DIR / 'database'
        database_dir.mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_dir / "ai_teaching.db"}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== JWT配置 ==========
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key-2024')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 86400))
    
    # ========== AI服务配置 ==========
    # AI服务运行模式: 'direct'=直接模式, 'gateway'=网关模式(通过Node.js), 'auto'=自动选择
    AI_SERVICE_MODE = os.getenv('AI_SERVICE_MODE', 'direct').lower()

    # ----- 直接模式配置（Python直接调用官方API）-----
    # DeepSeek AI配置 (推荐)
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    # 豆包大模型配置 (已弃用，保留兼容性)
    DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY', '')
    DOUBAO_API_URL = os.getenv('DOUBAO_API_URL', 'https://ark.cn-beijing.volces.com/api/v3')
    DOUBAO_CHAT_MODEL = os.getenv('DOUBAO_CHAT_MODEL', 'doubao-lite')
    DOUBAO_PRO_MODEL = os.getenv('DOUBAO_PRO_MODEL', 'doubao-pro-32k')

    # 智谱清言配置 (已弃用，保留兼容性)
    ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
    ZHIPU_API_URL = os.getenv('ZHIPU_API_URL', 'https://open.bigmodel.cn/api/paas/v4')
    ZHIPU_CHAT_MODEL = os.getenv('ZHIPU_CHAT_MODEL', 'glm-4')

    # ----- 网关模式配置（通过Node.js AI服务）-----
    AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:3001/api/v1/ai')
    AI_SERVICE_TIMEOUT = int(os.getenv('AI_SERVICE_TIMEOUT', 30))
    
    # ========== 文件上传配置 ==========
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'backend/static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 默认50MB
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {
        'video': {'mp4', 'avi', 'mov', 'mkv'},
        'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'},
        'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp'},
    }
    
    # ========== CORS配置 ==========
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # ========== 服务器配置 ==========
    BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
    BACKEND_PORT = int(os.getenv('BACKEND_PORT', 8000))
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # ========== 日志配置 ==========
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / os.getenv('LOG_FILE', 'logs/backend.log')
    
    # ========== 功能开关 ==========
    ENABLE_AI_SERVICE = os.getenv('ENABLE_AI_SERVICE', 'true').lower() == 'true'
    
    @property
    def ai_service_available(self):
        """检查AI服务是否可用"""
        if not self.ENABLE_AI_SERVICE:
            return False, "AI服务已禁用"

        if self.AI_SERVICE_MODE == 'direct':
            # 直接模式下，优先使用DeepSeek，然后检查其他API
            if self.DEEPSEEK_API_KEY:
                return True, "直接模式可用 (DeepSeek)"
            elif self.DOUBAO_API_KEY or self.ZHIPU_API_KEY:
                return True, "直接模式可用 (备用AI)"
            return False, "直接模式下未配置任何AI API密钥"
        elif self.AI_SERVICE_MODE == 'gateway':
            # 网关模式下，检查服务URL是否配置
            if self.AI_SERVICE_URL:
                return True, f"网关模式可用，目标: {self.AI_SERVICE_URL}"
            return False, "网关模式下未配置AI_SERVICE_URL"
        else:  # auto模式
            # 优先使用直接模式的DeepSeek，然后是网关，最后是其他直接模式
            if self.DEEPSEEK_API_KEY:
                return True, "自动模式选择DeepSeek直接调用"
            elif self.AI_SERVICE_URL:
                return True, f"自动模式选择网关，目标: {self.AI_SERVICE_URL}"
            elif self.DOUBAO_API_KEY or self.ZHIPU_API_KEY:
                return True, "自动模式选择备用AI直接调用"
            return False, "自动模式下无可用AI服务"
    
    def get_ai_endpoints(self):
        """获取AI服务端点信息"""
        base_info = {
            'chat': '/api/v1/ai/chat',
            'ppt': '/api/v1/ai/ppt/generate',
            'textbook': '/api/v1/ai/textbook/generate',
            'quiz': '/api/v1/ai/quiz/generate',
            'analyze': '/api/v1/ai/analyze',
            'status': '/api/v1/ai/status',
        }

        # 根据模式添加特定信息
        if self.AI_SERVICE_MODE == 'direct':
            base_info['mode'] = 'direct'
            base_info['providers'] = {
                'deepseek': 'available' if self.DEEPSEEK_API_KEY else 'not_configured',
                'doubao': 'available (deprecated)' if self.DOUBAO_API_KEY else 'not_configured',
                'zhipu': 'available (deprecated)' if self.ZHIPU_API_KEY else 'not_configured',
            }
        else:
            base_info['mode'] = 'gateway'
            base_info['gateway_url'] = self.AI_SERVICE_URL

        return base_info
    
    def print_config_summary(self):
        """打印配置摘要信息"""
        print("\n" + "="*60)
        print("🤖 AI智慧教学平台 - 后端配置摘要")
        print("="*60)
        
        # 基础信息
        print(f"📁 项目根目录: {BASE_DIR}")
        print(f"🔧 环境: {'开发' if self.DEBUG else '生产'}")
        print(f"🚀 服务器: {self.BACKEND_HOST}:{self.BACKEND_PORT}")
        print(f"🔗 前端地址: {self.FRONTEND_URL}")
        print(f"🗄️  数据库: {self.SQLALCHEMY_DATABASE_URI}")
        
        # AI服务配置
        print(f"\n🧠 AI服务配置:")
        print(f"   运行模式: {self.AI_SERVICE_MODE.upper()}模式")

        available, message = self.ai_service_available
        status_icon = "✅" if available else "❌"
        print(f"   服务状态: {status_icon} {message}")

        if self.AI_SERVICE_MODE == 'direct':
            print(f"   DeepSeek AI: {'✅ 已配置 (推荐)' if self.DEEPSEEK_API_KEY else '❌ 未配置'}")
            if self.DEEPSEEK_API_KEY:
                print(f"      - API URL: {self.DEEPSEEK_API_URL}")
                print(f"      - 模型: {self.DEEPSEEK_MODEL}")

            print(f"   豆包大模型: {'⚠️  已配置 (已弃用)' if self.DOUBAO_API_KEY else '❌ 未配置'}")
            if self.DOUBAO_API_KEY:
                print(f"      - 聊天模型: {self.DOUBAO_CHAT_MODEL}")
                print(f"      - Pro模型: {self.DOUBAO_PRO_MODEL}")

            print(f"   智谱清言: {'⚠️  已配置 (已弃用)' if self.ZHIPU_API_KEY else '❌ 未配置'}")
            if self.ZHIPU_API_KEY:
                print(f"      - 模型: {self.ZHIPU_CHAT_MODEL}")
        else:
            print(f"   AI服务网关: {self.AI_SERVICE_URL}")
            print(f"   超时设置: {self.AI_SERVICE_TIMEOUT}秒")
        
        # 文件上传
        print(f"\n📁 文件上传配置:")
        print(f"   上传目录: {self.UPLOAD_FOLDER}")
        print(f"   最大文件: {self.MAX_CONTENT_LENGTH // (1024*1024)}MB")
        
        # CORS配置
        print(f"\n🌐 CORS配置:")
        for origin in self.CORS_ORIGINS:
            print(f"   - {origin}")
        
        print("="*60)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
    def print_config_summary(self):
        """打印开发环境配置摘要"""
        super().print_config_summary()
        print("💡 提示: 当前为开发环境，已启用调试模式")


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    def print_config_summary(self):
        """打印生产环境配置摘要"""
        super().print_config_summary()
        print("⚠️  警告: 当前为生产环境，请确保所有敏感信息已正确配置")


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    def print_config_summary(self):
        """打印测试环境配置摘要"""
        super().print_config_summary()
        print("🧪 提示: 当前为测试环境，使用内存数据库")


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


if __name__ == '__main__':
    """直接运行此文件时打印配置信息"""
    print("测试配置加载...")
    
    # 根据环境变量选择配置
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config.get(env, config['default'])
    
    # 创建配置实例并打印信息
    cfg = config_class()
    cfg.print_config_summary()
    
    # 测试AI服务可用性
    available, message = cfg.ai_service_available
    print(f"\n🧪 AI服务可用性测试: {message}")
    
    # 显示端点信息
    endpoints = cfg.get_ai_endpoints()
    print(f"\n🔌 可用AI端点:")
    for key, value in endpoints.items():
        if key not in ['mode', 'providers', 'gateway_url']:
            print(f"   - {key}: {value}")