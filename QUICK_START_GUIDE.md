# 项目整合快速指南

## 🎯 整合目标

将5个分散的子项目整合为一个统一的AI智慧教学平台:

1. **ai-teaching-platform** → 前端React应用 + 教材制作功能
2. **py fl** → 视频学习系统
3. **用户** → 用户认证与权限管理
4. **lyj3** → AI测验批改系统
5. **front end practice** → 前端练习(可选)
6. **aiteacher.web - 副本** → 备份(忽略)

## 📁 新的统一项目结构

```
ai-teaching-platform-unified/     # 新的统一项目根目录
│
├── README.md                      # 项目说明(已创建✅)
├── .env.example                   # 环境变量示例(已创建✅)
├── .env                          # 环境变量(需复制.env.example)
├── requirements.txt              # Python依赖(已创建✅)
├── start-dev.bat                 # 启动脚本(已创建✅)
├── .gitignore                    # Git忽略文件(需创建)
│
├── backend/                      # 统一后端(需创建)
│   ├── app.py                    # 主应用
│   ├── config.py                 # 配置
│   ├── models/                   # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py               # 从"用户"项目迁移
│   │   ├── role.py
│   │   ├── course.py             # 从"py fl"项目迁移
│   │   ├── video.py
│   │   ├── quiz.py
│   │   └── note.py
│   ├── routes/                   # API路由
│   │   ├── __init__.py
│   │   ├── auth.py               # 从"用户"项目
│   │   ├── user.py
│   │   ├── course.py             # 从"py fl"项目
│   │   ├── video.py
│   │   ├── quiz.py
│   │   └── ai.py                 # 从"lyj3"项目
│   ├── services/                 # 业务逻辑
│   │   ├── __init__.py
│   │   ├── bert_service.py       # 从"lyj3"迁移
│   │   └── doubao_service.py     # 从"py fl"迁移
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── jwt_util.py
│   │   └── decorators.py
│   └── static/                   # 静态文件
│       ├── uploads/
│       ├── videos/
│       └── subtitles/
│
├── frontend/                     # React前端(从ai-teaching-platform迁移)
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── store/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── database/                     # 数据库文件
│   ├── ai_teaching.db           # 统一数据库(初始化后生成)
│   └── migrations/
│
├── scripts/                      # 脚本工具
│   ├── init_db.py               # 初始化数据库
│   ├── migrate_data.py          # 数据迁移脚本
│   └── fix_directories.py       # 修复py fl目录名
│
├── docs/                        # 文档
│   ├── API.md
│   ├── DATABASE.md
│   └── DEPLOYMENT.md
│
└── tests/                       # 测试
    ├── backend/
    └── frontend/
```

## 🔄 整合步骤详解

### 步骤1: 创建新项目目录结构

```bash
cd C:\Users\Think\Desktop\1108

# 创建主目录(已完成✅)
mkdir ai-teaching-platform-unified

# 创建后端目录
cd ai-teaching-platform-unified
mkdir backend
mkdir backend\models
mkdir backend\routes
mkdir backend\services
mkdir backend\utils
mkdir backend\static
mkdir backend\static\uploads
mkdir backend\static\videos
mkdir backend\static\subtitles

# 创建其他目录
mkdir database
mkdir database\migrations
mkdir scripts
mkdir docs
mkdir tests
mkdir tests\backend
mkdir tests\frontend

# 创建__init__.py文件
type nul > backend\__init__.py
type nul > backend\models\__init__.py
type nul > backend\routes\__init__.py
type nul > backend\services\__init__.py
type nul > backend\utils\__init__.py
```

### 步骤2: 迁移前端代码

**从 ai-teaching-platform 复制整个frontend目录**:

```bash
# 在PowerShell中执行
cd C:\Users\Think\Desktop\1108
xcopy "ai-teaching-platform\src" "ai-teaching-platform-unified\frontend\src\" /E /I /H /Y
xcopy "ai-teaching-platform\public" "ai-teaching-platform-unified\frontend\public\" /E /I /H /Y
copy "ai-teaching-platform\package.json" "ai-teaching-platform-unified\frontend\"
copy "ai-teaching-platform\vite.config.js" "ai-teaching-platform-unified\frontend\"
copy "ai-teaching-platform\index.html" "ai-teaching-platform-unified\frontend\"
copy "ai-teaching-platform\eslint.config.js" "ai-teaching-platform-unified\frontend\"
```

### 步骤3: 整合后端模型

**从"用户"项目复制models.py内容**:

```bash
# 复制用户模型
copy "用户\backend\models.py" "ai-teaching-platform-unified\backend\models\user.py"
```

然后需要手动拆分文件:
- User, Role, Permission, UserStats → `backend/models/user.py`
- Course → `backend/models/course.py`

**从"py fl"项目提取模型**:

打开 `py fl\app.py`,复制以下类到对应文件:
- Course, Chapter → `backend/models/course.py`
- Video → `backend/models/video.py`
- UserProgress → `backend/models/progress.py`
- Quiz → `backend/models/quiz.py`
- Note, SubtitleTranslation → `backend/models/note.py`

### 步骤4: 整合后端路由

**从"用户"项目**:
```bash
# 复制认证路由
copy "用户\backend\routes\auth.py" "ai-teaching-platform-unified\backend\routes\"
copy "用户\backend\routes\user.py" "ai-teaching-platform-unified\backend\routes\"
```

**从"py fl"项目**:

需要手动提取 `py fl\app.py` 中的路由:
- 视频相关路由 → `backend/routes/video.py`
- 课程相关路由 → `backend/routes/course.py`
- 测验相关路由 → `backend/routes/quiz.py`
- 笔记相关路由 → `backend/routes/note.py`

**从"lyj3"项目**:

提取 `lyj3\lyj3.py` 中的AI批改功能:
- 测验批改路由 → `backend/routes/ai.py`
- BERT服务 → `backend/services/bert_service.py`

### 步骤5: 整合AI服务

**BERT服务** (从lyj3):

创建 `backend/services/bert_service.py`:
```python
# 从 lyj3/lyj3.py 复制:
# - get_text_embedding 函数
# - calculate_similarity 函数
# - tokenizer 和 model 加载代码
```

**Doubao服务** (从py fl):

创建 `backend/services/doubao_service.py`:
```python
# 从 py fl/app.py 复制:
# - _generate_ai_summary 函数
# - api_translate 相关代码
# - api_ocr_text 相关代码
```

### 步骤6: 创建主应用

创建 `backend/app.py`:

```python
from flask import Flask
from flask_cors import CORS
from backend.models import db
from backend.config import Config

# 导入所有蓝图
from backend.routes.auth import auth_bp
from backend.routes.user import user_bp
from backend.routes.course import course_bp
from backend.routes.video import video_bp
from backend.routes.quiz import quiz_bp
from backend.routes.note import note_bp
from backend.routes.ai import ai_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    CORS(app)

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(course_bp, url_prefix='/api/v1/courses')
    app.register_blueprint(video_bp, url_prefix='/api/v1/videos')
    app.register_blueprint(quiz_bp, url_prefix='/api/v1/quizzes')
    app.register_blueprint(note_bp, url_prefix='/api/v1/notes')
    app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')

    return app

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=8000)
```

### 步骤7: 创建配置文件

创建 `backend/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///database/ai_teaching.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))

    # CORS配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    # 上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'backend/static/uploads')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 104857600))

    # AI服务配置
    DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY', '')
    DOUBAO_API_URL = os.getenv('DOUBAO_API_URL', 'https://ark.cn-beijing.volces.com/api/v3')
    DOUBAO_MODEL = os.getenv('DOUBAO_MODEL', 'doubao-seed-1-6-251015')

    BERT_MODEL = os.getenv('BERT_MODEL', 'bert-base-chinese')
    HF_ENDPOINT = os.getenv('HF_ENDPOINT', 'https://hf-mirror.com')
```

### 步骤8: 创建数据库初始化脚本

创建 `scripts/init_db.py`:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app import create_app
from backend.models.user import db, User, Role, Permission, UserStats
import json

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()

    # 检查是否已初始化
    if Role.query.first():
        print("数据库已初始化")
        return

    # 创建角色
    roles_data = [
        {
            'name': 'student',
            'display_name': '学生',
            'description': '学习课程、提交作业、参与测验',
            'permissions': json.dumps(['view_course', 'submit_assignment', 'take_quiz'])
        },
        {
            'name': 'teacher',
            'display_name': '教师',
            'description': '创建课程、批改作业、查看统计',
            'permissions': json.dumps(['create_course', 'grade_assignment', 'view_all_stats'])
        },
        {
            'name': 'ai_assistant',
            'display_name': 'AI助教',
            'description': '智能答疑、自动批改',
            'permissions': json.dumps(['answer_question', 'auto_grade'])
        }
    ]

    roles = {}
    for role_data in roles_data:
        role = Role(**role_data)
        db.session.add(role)
        roles[role_data['name']] = role

    db.session.flush()

    # 创建测试用户
    users_data = [
        {
            'username': 'teacher001',
            'password': '123456',
            'email': 'teacher001@example.com',
            'real_name': '张老师',
            'role': roles['teacher']
        },
        {
            'username': 'student001',
            'password': '123456',
            'email': 'student001@example.com',
            'real_name': '李同学',
            'role': roles['student']
        }
    ]

    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            real_name=user_data['real_name'],
            role_id=user_data['role'].id
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()

        # 创建统计
        stats = UserStats(user_id=user.id)
        db.session.add(stats)

    db.session.commit()
    print("✅ 数据库初始化完成!")
```

### 步骤9: 修复py fl目录拼写错误

创建 `scripts/fix_directories.py`:

```python
import os
import shutil

base_dir = r"C:\Users\Think\Desktop\1108\py fl"

# 修复目录名
if os.path.exists(os.path.join(base_dir, 'ststic')):
    shutil.move(
        os.path.join(base_dir, 'ststic'),
        os.path.join(base_dir, 'static')
    )
    print("✅ 已修复 ststic → static")

if os.path.exists(os.path.join(base_dir, 'teplates')):
    shutil.move(
        os.path.join(base_dir, 'teplates'),
        os.path.join(base_dir, 'templates')
    )
    print("✅ 已修复 teplates → templates")
```

### 步骤10: 创建.gitignore

创建 `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite

# Environment
.env
.env.local

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp

# Node.js
node_modules/
npm-debug.log*
package-lock.json

# Build
dist/
build/
*.egg-info/

# OS
.DS_Store
Thumbs.db
```

### 步骤11: 配置环境变量

```bash
# 复制环境变量示例
copy .env.example .env

# 编辑.env文件,修改以下配置:
# - SECRET_KEY (生成随机字符串)
# - JWT_SECRET_KEY (生成随机字符串)
# - DOUBAO_API_KEY (如有)
```

生成随机密钥:
```python
import secrets
print(secrets.token_hex(32))
```

### 步骤12: 安装依赖并启动

```bash
# 运行启动脚本
start-dev.bat
```

或手动执行:

```bash
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd frontend
npm install
cd ..

# 4. 初始化数据库
python scripts\init_db.py

# 5. 启动后端(新终端)
python backend\app.py

# 6. 启动前端(新终端)
cd frontend
npm run dev
```

## ✅ 验证整合结果

### 1. 检查后端API

访问: http://localhost:8000/api/v1/health

应返回:
```json
{
  "success": true,
  "message": "AI线上课程系统运行正常"
}
```

### 2. 检查前端页面

访问: http://localhost:3000

应显示登录页面

### 3. 测试登录

使用账号: `teacher001` / `123456`

应能成功登录并跳转到教师工作台

### 4. 测试API接口

```bash
# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher001","password":"123456"}'

# 获取课程列表(需要token)
curl -X GET http://localhost:8000/api/v1/courses \
  -H "Authorization: Bearer <your_token>"
```

## 🐛 常见问题排查

### 问题1: 模块导入错误

**错误**: `ModuleNotFoundError: No module named 'backend'`

**解决**:
```bash
# 设置PYTHONPATH
set PYTHONPATH=%CD%
# 或在代码中添加
import sys
sys.path.insert(0, os.path.dirname(__file__))
```

### 问题2: 数据库错误

**错误**: `sqlalchemy.exc.OperationalError`

**解决**:
```bash
# 删除旧数据库
del database\ai_teaching.db
# 重新初始化
python scripts\init_db.py
```

### 问题3: 前端无法连接后端

**错误**: `Network Error` 或 `CORS Error`

**解决**:
- 检查后端是否启动: http://localhost:8000/api/v1/health
- 检查CORS配置: `.env` 中的 `CORS_ORIGINS`
- 检查前端API配置: `frontend/src/services/api.js`

### 问题4: BERT模型下载失败

**错误**: `OSError: Can't load model`

**解决**:
```bash
# 设置镜像
set HF_ENDPOINT=https://hf-mirror.com
# 手动下载模型
python -c "from transformers import BertModel; BertModel.from_pretrained('bert-base-chinese')"
```

## 📚 下一步

整合完成后,建议:

1. **阅读完整文档**:
   - `README.md` - 项目说明
   - `PROJECT_ANALYSIS_REPORT.md` - 详细分析报告
   - `docs/API.md` - API文档(需创建)

2. **测试所有功能**:
   - 用户注册/登录
   - 课程创建/管理
   - 视频上传/播放
   - 测验创建/答题
   - AI批改功能

3. **优化和扩展**:
   - 添加缺失的API接口
   - 完善前端页面
   - 优化性能
   - 添加单元测试

4. **部署到生产环境**:
   - 配置生产环境变量
   - 使用PostgreSQL
   - 配置Nginx
   - 使用Docker部署

## 🎉 完成!

完成以上步骤后,你将拥有一个功能完整、架构清晰的AI智慧教学平台!

如遇到问题,请查看 `PROJECT_ANALYSIS_REPORT.md` 获取更多帮助。
