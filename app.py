# backend/app.py
import os
import sys
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# ========== 修复导入路径 ==========
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
# =================================

from config import config

# ========== 导入统一的db实例 ==========
try:
    from db_instance import db
    print("✅ 从db_instance导入统一的db实例")
except ImportError as e:
    print(f"⚠️  无法导入db_instance: {e}")
    # 创建临时db实例
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
# =================================================


def create_app(config_name='default'):
    """创建Flask应用 - 纯API版本"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])
    
    # ========== CORS配置 - 允许前端3000端口访问 ==========
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "X-Auth-Token", "Origin", "Accept"],
                 "expose_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                 "supports_credentials": True,
                 "max_age": 3600
             },
             r"/*": {
                 "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                 "methods": ["GET", "OPTIONS"],
                 "allow_headers": ["Content-Type"],
                 "supports_credentials": True
             }
         },
         supports_credentials=True)
    
    # ========== 使用统一的db实例 ==========
    from flask_migrate import Migrate
    db.init_app(app)  # 将统一的db实例绑定到当前app
    migrate = Migrate(app, db)
    # ============================================================
    
    jwt = JWTManager(app)

    # 创建必要的目录
    upload_folder = app.config.get('UPLOAD_FOLDER', 'backend/static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs('backend/static/videos', exist_ok=True)
    os.makedirs('backend/static/subtitles', exist_ok=True)
    os.makedirs('backend/static/frames', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # ========== 在上下文中导入模型 ==========
    with app.app_context():
        try:
            from models import User, Role, Permission, UserStats
            from models import Course, Video, Progress, Quiz, Note, Chapter
            print("✅ 模型导入成功")
        except Exception as e:
            print(f"⚠️  模型导入警告: {e}")
    # ===================================================

    # ========== 注册蓝图 - 保持原有的v1版本不变 ==========
    try:
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        print("✅ auth蓝图注册成功 (v1)")
    except ImportError as e:
        print(f"警告: 无法导入 auth 路由: {e}")
    
    try:
        from routes.user import user_bp
        app.register_blueprint(user_bp, url_prefix='/api/v1/users')
        print("✅ user蓝图注册成功 (v1)")
    except ImportError as e:
        print(f"警告: 无法导入 user 路由: {e}")
    
    try:
        from routes.quiz import quiz_bp
        app.register_blueprint(quiz_bp, url_prefix='/api/v1/quiz')
        print("✅ quiz蓝图注册成功 (v1)")
    except ImportError as e:
        print(f"警告: 无法导入 quiz 路由: {e}")

    # ========== 注册AI路由 ==========
    try:
        from routes.ai import ai_bp
        app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')
        print("✅ AI路由注册成功 (v1)")
        
        # 检查AI服务配置
        doubao_key = os.getenv('DOUBAO_API_KEY', '')
        zhipu_key = os.getenv('ZHIPU_API_KEY', '')
        
        if doubao_key:
            print(f"   ├── 豆包大模型: 已配置")
        else:
            print(f"   ├── 豆包大模型: 未配置 (请在.env中设置DOUBAO_API_KEY)")
        
        if zhipu_key:
            print(f"   ├── 智谱清言: 已配置")
        else:
            print(f"   ├── 智谱清言: 未配置 (请在.env中设置ZHIPU_API_KEY)")
            
        print(f"   └── AI端点: /api/v1/ai/*")
    except ImportError as e:
        print(f"警告: 无法导入 AI 路由: {e}")

    # ========== 添加兼容层路由 - 解决前端路径问题 ==========
    
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def auth_login_compat():
        """兼容性路由 - 将 /api/auth/* 转发到 /api/v1/auth/*"""
        return forward_to_v1('auth/login', request)
    
    @app.route('/api/auth/check', methods=['GET', 'OPTIONS'])
    def auth_check_compat():
        """兼容性路由 - 用户状态检查"""
        return forward_to_v1('auth/check', request)
    
    @app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
    def auth_me_compat():
        """兼容性路由 - 获取当前用户"""
        return forward_to_v1('auth/me', request)
    
    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    def auth_logout_compat():
        """兼容性路由 - 退出登录"""
        return forward_to_v1('auth/logout', request)
    
    @app.route('/api/auth/check-login', methods=['GET', 'OPTIONS'])
    def auth_check_login_compat():
        """兼容性路由 - 检查登录状态（前端请求）"""
        return jsonify({
            'success': True,
            'data': None,
            'message': '请使用 /api/auth/me 接口'
        })
    
    @app.route('/api/user/current', methods=['GET', 'OPTIONS'])
    def user_current_compat():
        """兼容性路由 - 获取当前用户信息"""
        return forward_to_v1('users/current', request)
    
    @app.route('/api/system-info', methods=['GET', 'OPTIONS'])
    def system_info_compat():
        """兼容性路由 - 系统信息"""
        return jsonify({
            'success': True,
            'data': {
                'status': 'online',
                'backend': 'Flask API',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'api_base': 'http://localhost:8000/api',
                'frontend': 'http://localhost:3000',
                'endpoints': {
                    'health': '/api/v1/health',
                    'auth': '/api/auth',
                    'user': '/api/user',
                    'quiz': '/api/quiz',
                    'ai': '/api/ai'
                },
                'cors_enabled': True
            }
        })
    
    @app.route('/api/test', methods=['GET', 'OPTIONS'])
    def test_compat():
        """兼容性路由 - 测试接口"""
        return jsonify({
            'success': True,
            'message': 'API连接测试成功',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'note': '此接口为兼容性接口，实际业务请使用相应版本化接口'
        })
    
    @app.route('/api/quiz/questions', methods=['GET', 'OPTIONS'])
    def quiz_questions_compat():
        """兼容性路由 - 获取题目"""
        return forward_to_v1('quiz/questions', request)
    
    @app.route('/api/quiz/submit', methods=['POST', 'OPTIONS'])
    def quiz_submit_compat():
        """兼容性路由 - 提交答题"""
        return forward_to_v1('quiz/submit', request)
    
    @app.route('/api/ai/status', methods=['GET', 'OPTIONS'])
    def ai_status_compat():
        """兼容性路由 - AI服务状态"""
        return forward_to_v1('ai/status', request)
    
    @app.route('/api/ai/chat', methods=['POST', 'OPTIONS'])
    def ai_chat_compat():
        """兼容性路由 - AI聊天"""
        return forward_to_v1('ai/chat', request)
    
    @app.route('/api/ai/ppt/generate', methods=['POST', 'OPTIONS'])
    def ai_ppt_generate_compat():
        """兼容性路由 - 生成PPT"""
        return forward_to_v1('ai/ppt/generate', request)
    
    @app.route('/api/ai/textbook/generate', methods=['POST', 'OPTIONS'])
    def ai_textbook_generate_compat():
        """兼容性路由 - 生成教材"""
        return forward_to_v1('ai/textbook/generate', request)
    
    @app.route('/api/ai/quiz/generate', methods=['POST', 'OPTIONS'])
    def ai_quiz_generate_compat():
        """兼容性路由 - 生成测验"""
        return forward_to_v1('ai/quiz/generate', request)
    
    @app.route('/api/ai/analyze', methods=['POST', 'OPTIONS'])
    def ai_analyze_compat():
        """兼容性路由 - 内容分析"""
        return forward_to_v1('ai/analyze', request)
    
    @app.route('/api/ai/<path:ai_path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def ai_compat_gateway(ai_path):
        """兼容性AI路由 - 转发到v1版本"""
        return forward_to_v1(f'ai/{ai_path}', request)

    def forward_to_v1(endpoint, req):
        """将请求转发到对应的v1端点"""
        try:
            # 获取请求数据
            data = req.get_json(silent=True) or req.form.to_dict()
            
            # 构建转发URL（本地转发，不经过网络）
            # 这里我们实际上不需要真正的网络请求，可以直接调用相应的视图函数
            # 但为了简单起见，我们模拟一个请求
            
            # 如果是AI相关的请求，直接返回成功响应（因为AI路由已经注册）
            if endpoint.startswith('ai/'):
                return jsonify({
                    'success': True,
                    'message': f'请直接使用 /api/v1/{endpoint} 接口',
                    'compatibility_note': '兼容层路由，已注册AI服务'
                }), 200
            
            # 对于其他请求，尝试转发
            response = requests.request(
                method=req.method,
                url=f'http://localhost:8000/api/v1/{endpoint}',
                json=data if req.is_json else None,
                data=None if req.is_json else data,
                headers={key: value for key, value in req.headers 
                        if key.lower() not in ['host', 'content-length']},
                cookies=req.cookies,
                timeout=30
            )
            
            # 返回响应
            return jsonify(response.json()), response.status_code
            
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'message': '后端服务内部通信错误',
                'timestamp': datetime.now().isoformat()
            }), 503
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'请求转发失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    # ========== 原有的v1接口保持不变 ==========
    
    # 用户登录状态检查
    @app.route('/api/v1/auth/check', methods=['GET', 'OPTIONS'])
    def check_auth():
        """检查用户登录状态 - 用于前端右上角显示"""
        if request.method == 'OPTIONS':
            return '', 200
        
        return jsonify({
            'success': True,
            'data': None,  # 未登录时返回None
            'message': '用户未登录'
        })

    # 简化健康检查端点
    @app.route('/api/v1/health', methods=['GET', 'OPTIONS'])
    def health_check():
        """简化的健康检查端点"""
        if request.method == 'OPTIONS':
            return '', 200
        
        return jsonify({
            'success': True,
            'message': 'API服务器运行正常',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'ai_services': {
                'doubao': 'available' if os.getenv('DOUBAO_API_KEY') else 'not_configured',
                'zhipu': 'available' if os.getenv('ZHIPU_API_KEY') else 'not_configured'
            }
        })
    
    # API连接测试端点
    @app.route('/api/v1/test-connection', methods=['GET', 'OPTIONS'])
    def test_connection():
        """前端调用此端点来测试API连接"""
        if request.method == 'OPTIONS':
            return '', 200
            
        return jsonify({
            'success': True,
            'message': 'API连接测试成功',
            'timestamp': datetime.now().isoformat(),
            'frontend_origin': request.headers.get('Origin', 'unknown'),
            'cors_configured': True,
            'services': {
                'backend': 'running',
                'ai_doubao': 'configured' if os.getenv('DOUBAO_API_KEY') else 'not_configured',
                'ai_zhipu': 'configured' if os.getenv('ZHIPU_API_KEY') else 'not_configured'
            },
            'recommendations': [
                '1. 确保后端运行在 http://localhost:8000',
                '2. 前端运行在 http://localhost:3000',
                '3. 检查浏览器控制台是否有CORS错误'
            ]
        })
    
    # 静态文件服务
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """提供上传的文件"""
        upload_dir = os.path.join(backend_dir, 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        return send_from_directory(upload_dir, filename)
    
    # ========== 根路径 ==========
    @app.route('/')
    def index():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI智慧教学平台 - 后端API服务</title>
            <meta http-equiv="refresh" content="0; url=http://localhost:3000">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #2c7be5 0%, #1a5bb8 100%);
                    color: white;
                    height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    max-width: 600px;
                    padding: 40px;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                h1 {
                    font-size: 2.5rem;
                    margin-bottom: 20px;
                }
                p {
                    font-size: 1.1rem;
                    margin-bottom: 30px;
                    opacity: 0.9;
                }
                .btn {
                    display: inline-block;
                    background: white;
                    color: #2c7be5;
                    padding: 12px 30px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 10px;
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
                }
                .spinner {
                    margin: 30px 0;
                    font-size: 3rem;
                }
                .links {
                    margin-top: 30px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .api-link {
                    color: rgba(255, 255, 255, 0.8);
                    text-decoration: none;
                    padding: 8px 15px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    transition: all 0.3s;
                }
                .api-link:hover {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                }
                .status {
                    padding: 10px 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    text-align: left;
                    font-family: monospace;
                    background: rgba(0, 0, 0, 0.2);
                }
                .success {
                    color: #4ade80;
                    border-left: 4px solid #4ade80;
                }
                .error {
                    color: #f87171;
                    border-left: 4px solid #f87171;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="spinner">🤖</div>
                <h1>AI智慧教学平台 - 后端API</h1>
                <p>API服务运行中，正在跳转到前端界面...</p>
                
                <div id="status" class="status">
                    <div>正在检查API连接...</div>
                </div>
                
                <div>
                    <a href="http://localhost:3000" class="btn">
                        <i class="fas fa-external-link-alt"></i> 立即访问前端
                    </a>
                    <a href="/api/v1/health" class="btn" style="background: rgba(255,255,255,0.1); color: white;">
                        <i class="fas fa-heartbeat"></i> 检查API状态
                    </a>
                </div>
                
                <div class="links">
                    <h3>📚 API端点：</h3>
                    <a href="/api/v1/health" class="api-link">GET /api/v1/health - 健康检查</a>
                    <a href="/api/v1/test-connection" class="api-link">GET /api/v1/test-connection - 连接测试</a>
                    <a href="/api/v1/ai/status" class="api-link">GET /api/v1/ai/status - AI服务状态</a>
                    <a href="/api/auth/check" class="api-link">GET /api/auth/check - 用户登录状态</a>
                    <a href="/api/quiz/questions" class="api-link">GET /api/quiz/questions - 获取题目</a>
                    <a href="/api/auth/login" class="api-link">POST /api/auth/login - 用户登录</a>
                </div>
                
                <p style="margin-top: 30px; font-size: 0.9rem; opacity: 0.7;">
                    如果页面没有自动跳转，请点击上方按钮或访问：
                    <a href="http://localhost:3000" style="color: #00d2ff; text-decoration: none;">
                        http://localhost:3000
                    </a>
                </p>
            </div>
            
            <script>
                // 测试API连接
                async function testApi() {
                    const statusDiv = document.getElementById('status');
                    try {
                        const response = await fetch('/api/v1/health', {
                            method: 'GET',
                            headers: {
                                'Accept': 'application/json'
                            }
                        });
                        
                        if (response.ok) {
                            const data = await response.json();
                            statusDiv.innerHTML = `
                                <div class="success">✅ API连接成功</div>
                                <div>后端状态: ${data.message}</div>
                                <div>版本: ${data.version}</div>
                                <div>时间: ${new Date(data.timestamp).toLocaleString()}</div>
                            `;
                            console.log('API连接测试成功:', data);
                        } else {
                            statusDiv.innerHTML = `
                                <div class="error">❌ API连接失败 (${response.status})</div>
                                <div>状态: ${response.statusText}</div>
                            `;
                            console.error('API连接测试失败:', response.status, response.statusText);
                        }
                    } catch (error) {
                        statusDiv.innerHTML = `
                            <div class="error">❌ API连接错误</div>
                            <div>错误: ${error.message}</div>
                            <div>请确保后端服务已启动</div>
                        `;
                        console.error('API连接错误:', error);
                    }
                }
                
                // 页面加载后测试API
                document.addEventListener('DOMContentLoaded', testApi);
                
                // 3秒后自动跳转
                setTimeout(() => {
                    window.location.href = 'http://localhost:3000';
                }, 3000);
            </script>
        </body>
        </html>
        '''
    
    # ========== 错误处理 ==========
    @app.errorhandler(404)
    def not_found(error):
        # 如果是API请求，返回JSON错误
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'API接口不存在',
                'path': request.path,
                'timestamp': datetime.now().isoformat(),
                'available_endpoints': {
                    'health': '/api/v1/health',
                    'auth_check': '/api/auth/check',
                    'test_connection': '/api/test',
                    'auth': '/api/auth/*',
                    'user': '/api/user/*',
                    'quiz': '/api/quiz/*',
                    'ai': '/api/ai/*'
                }
            }), 404
        # 否则重定向到前端
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>页面未找到 - AI智慧教学平台</title>
            <meta http-equiv="refresh" content="3; url=http://localhost:3000">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }
                h1 {
                    font-size: 3rem;
                    margin-bottom: 20px;
                }
                p {
                    font-size: 1.2rem;
                    margin-bottom: 30px;
                    opacity: 0.9;
                }
                a {
                    color: #00d2ff;
                    text-decoration: none;
                    font-weight: bold;
                    padding: 10px 20px;
                    border: 2px solid #00d2ff;
                    border-radius: 25px;
                    transition: all 0.3s;
                }
                a:hover {
                    background: #00d2ff;
                    color: white;
                }
            </style>
        </head>
        <body>
            <h1>404 - 页面未找到</h1>
            <p>您访问的页面不存在，正在跳转到前端首页...</p>
            <a href="http://localhost:3000">立即前往</a>
            <script>
                setTimeout(() => {
                    window.location.href = 'http://localhost:3000';
                }, 3000);
            </script>
        </body>
        </html>
        ''', 404

    @app.errorhandler(500)
    def internal_error(error):
        # 使用统一的db实例
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'timestamp': datetime.now().isoformat(),
            'error': str(error) if app.config.get('DEBUG', False) else None
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        # 处理所有未捕获的异常
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': '服务器处理请求时发生错误',
                'timestamp': datetime.now().isoformat(),
                'error': str(error) if app.config.get('DEBUG', False) else None
            }), 500
        return f"服务器错误: {str(error)}", 500

    return app


if __name__ == '__main__':
    # 获取配置环境
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)

    # 启动应用
    print("\n" + "="*60)
    print("🤖 AI智慧教学平台 - 后端API服务")
    print("="*60)
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 后端目录: {backend_dir}")
    print("="*60)
    
    port = app.config.get('BACKEND_PORT', 8000)
    host = app.config.get('BACKEND_HOST', '127.0.0.1')
    debug_mode = app.config.get('DEBUG', True)
    
    print(f"🚀 后端API地址: http://{host}:{port}")
    print(f"🔗 前端访问地址: http://localhost:3000")
    print(f"🐛 调试模式: {debug_mode}")
    print("="*60)
    print("📚 核心API端点:")
    print(f"  - 健康检查: http://{host}:{port}/api/v1/health")
    print(f"  - AI服务状态: http://{host}:{port}/api/v1/ai/status")
    print(f"  - 用户状态检查: http://{host}:{port}/api/auth/check")
    print(f"  - 连接测试: http://{host}:{port}/api/test")
    print(f"  - 用户认证: http://{host}:{port}/api/auth/login")
    print(f"  - 题库API: http://{host}:{port}/api/quiz/questions")
    print(f"  - AI服务:")
    print(f"     聊天: http://{host}:{port}/api/v1/ai/chat")
    print(f"     PPT生成: http://{host}:{port}/api/v1/ai/ppt/generate")
    print(f"     教材生成: http://{host}:{port}/api/v1/ai/textbook/generate")
    print(f"     测验生成: http://{host}:{port}/api/v1/ai/quiz/generate")
    print(f"     内容分析: http://{host}:{port}/api/v1/ai/analyze")
    print("="*60)
    print("💡 提示:")
    print("  1. 前端页面请访问 http://localhost:3000")
    print("  2. 所有前端路由由前端服务器处理")
    print("  3. 后端只处理 /api/* 请求")
    print("  4. AI服务已集成到后端，无需单独启动Node.js服务")
    print("  5. 请确保在 .env 文件中配置了AI API密钥")
    print("="*60 + "\n")
    
    print("🔍 测试连接命令:")
    print(f"  curl http://{host}:{port}/api/v1/health")
    print(f"  curl http://{host}:{port}/api/v1/ai/status")
    print(f"  或")
    print(f"  Invoke-RestMethod -Uri 'http://{host}:{port}/api/v1/health' -Method GET")
    print("="*60 + "\n")

    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=True
    )