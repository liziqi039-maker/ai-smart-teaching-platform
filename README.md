# AI智慧教学平台 - 统一整合版

一个功能完整的AI驱动的线上教学系统,整合了用户管理、视频学习、智能测验、教材制作等多个模块。

## 项目特色

- 🎓 **完整的学习闭环**: 选课 → 学习 → 测验 → 反馈
- 🤖 **AI智能功能**: DeepSeek智能对话、BERT语义批改、智能PPT生成、题目生成
- 👥 **多角色支持**: 学生、教师、AI助教三种角色
- 📹 **视频学习**: 进度追踪、在线笔记、字幕翻译
- 📝 **智能测验**: 客观题自动批改、主观题AI评分
- 📚 **教材制作**: 文档/文本/语音转PPT,PPT转视频
- 🔐 **统一认证**: JWT Token跨域认证
- 📊 **数据统计**: 学习时长、课程进度、测验分析

## 技术栈

### 后端
- Python 3.9+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-JWT-Extended 4.6.0
- PyTorch + Transformers (BERT)
- SQLite / PostgreSQL

### 前端
- React 18
- Vite 5
- Ant Design 6
- React Router v7
- Redux Toolkit
- Axios

### AI服务
- BERT (bert-base-chinese) - 语义相似度计算
- Doubao API - 翻译、摘要、OCR

## 快速开始

### 方式一: 一键启动(推荐)

**Windows**:
```bash
start-dev.bat
```

**Linux/Mac**:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### 方式二: 手动启动

#### 1. 安装依赖

**后端**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**前端**:
```bash
cd frontend
npm install
cd ..
```

#### 2. 配置环境变量

复制 `.env.example` 为 `.env`,修改配置:
```bash
cp .env.example .env
```

必须配置的项:
- `SECRET_KEY`: Flask密钥
- `JWT_SECRET_KEY`: JWT密钥
- `DOUBAO_API_KEY`: Doubao API密钥(AI功能)

#### 3. 初始化数据库

```bash
python scripts/init_db.py
```

这会创建数据库并初始化:
- 3种角色(学生、教师、AI助教)
- 16个权限
- 4个测试账号

#### 4. 启动服务

**启动后端** (新终端):
```bash
venv\Scripts\activate
python backend/app.py
```

**启动前端** (新终端):
```bash
cd frontend
npm run dev
```

#### 5. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/api/docs

## 默认账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 教师 | teacher001 | 123456 | 可创建课程、上传视频、批改作业 |
| 学生 | student001 | 123456 | 可选课、学习、测验 |
| 学生 | student002 | 123456 | 可选课、学习、测验 |
| AI助教 | ai_assistant | 123456 | 可答疑、批改、分析 |

## 项目结构

```
ai-teaching-platform/
├── backend/                 # 后端Flask应用
│   ├── app.py              # 主应用入口
│   ├── config.py           # 配置管理
│   ├── models/             # 数据库模型
│   ├── routes/             # API路由
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   └── static/             # 静态文件
├── frontend/               # 前端React应用
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API服务
│   │   ├── store/          # Redux状态
│   │   └── App.jsx         # 主组件
│   ├── public/
│   └── package.json
├── database/               # 数据库文件
│   └── ai_teaching.db
├── scripts/                # 脚本工具
│   ├── init_db.py          # 初始化数据库
│   └── migrate_data.py     # 数据迁移
├── docs/                   # 文档
│   ├── API.md              # API文档
│   ├── DATABASE.md         # 数据库设计
│   └── DEPLOYMENT.md       # 部署文档
├── .env                    # 环境变量(不提交)
├── .env.example            # 环境变量示例
├── requirements.txt        # Python依赖
├── start-dev.bat           # Windows启动脚本
├── start-dev.sh            # Linux/Mac启动脚本
├── README.md               # 项目说明
└── PROJECT_ANALYSIS_REPORT.md  # 项目分析报告
```

## 核心功能

### 1. 用户管理
- 用户注册、登录、登出
- 角色权限控制(RBAC)
- 个人信息管理
- 学习统计数据

### 2. 课程管理
- 教师创建和管理课程
- 章节和视频组织
- 学生选课和学习
- 学习进度追踪

### 3. 视频学习
- 视频播放和进度保存
- 多设备进度同步
- 在线笔记功能
- 字幕多语言翻译
- OCR视频截图识别

### 4. 测验系统
- 客观题自动批改
- 主观题AI语义评分(BERT)
- 错题分析和推荐
- 测验统计报告

### 5. 教材制作
- 文档转PPT (Word/PDF)
- 文本转PPT (AI生成)
- 语音转PPT (语音识别)
- PPT转视频 (微课制作)

### 6. AI功能
- BERT语义相似度计算
- Doubao翻译(支持多语言)
- 智能笔记摘要
- OCR文字识别
- 智能答疑(待开发)

## API接口

完整API文档见 [docs/API.md](docs/API.md)

### 主要接口

#### 认证
```
POST   /api/v1/auth/register      # 注册
POST   /api/v1/auth/login         # 登录
POST   /api/v1/auth/logout        # 登出
POST   /api/v1/auth/refresh       # 刷新Token
GET    /api/v1/auth/me            # 获取当前用户
```

#### 课程
```
GET    /api/v1/courses            # 课程列表
POST   /api/v1/courses            # 创建课程
GET    /api/v1/courses/:id        # 课程详情
PUT    /api/v1/courses/:id        # 更新课程
DELETE /api/v1/courses/:id        # 删除课程
```

#### 视频
```
GET    /api/v1/videos             # 视频列表
POST   /api/v1/videos             # 上传视频
GET    /api/v1/videos/:id         # 视频详情
POST   /api/v1/videos/:id/progress # 保存进度
```

#### AI功能
```
POST   /api/v1/ai/translate       # 翻译
POST   /api/v1/ai/summarize       # 摘要
POST   /api/v1/ai/ocr             # OCR识别
POST   /api/v1/ai/grade           # AI批改
```

## 数据库设计

主要数据表:

- **users** - 用户表
- **roles** - 角色表
- **permissions** - 权限表
- **courses** - 课程表
- **chapters** - 章节表
- **videos** - 视频表
- **user_progress** - 学习进度
- **notes** - 笔记表
- **quizzes** - 测验题目
- **quiz_submissions** - 测验提交
- **materials** - 教材资源

详细设计见 [docs/DATABASE.md](docs/DATABASE.md)

## 配置说明

### 环境变量

必须配置:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

可选配置:
```env
# AI服务
DOUBAO_API_KEY=your-api-key
BERT_MODEL=bert-base-chinese

# 数据库
DATABASE_URI=sqlite:///database/ai_teaching.db

# 服务器
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

完整配置见 [.env.example](.env.example)

## 开发指南

### 后端开发

1. 创建新的路由模块:
```python
# backend/routes/my_module.py
from flask import Blueprint, jsonify
from backend.utils.decorators import token_required

my_bp = Blueprint('my_module', __name__)

@my_bp.route('/test')
@token_required
def test(current_user):
    return jsonify({'message': 'Hello!'})
```

2. 注册蓝图:
```python
# backend/app.py
from backend.routes.my_module import my_bp
app.register_blueprint(my_bp, url_prefix='/api/v1/my')
```

### 前端开发

1. 创建新页面:
```jsx
// frontend/src/pages/MyPage/index.jsx
export default function MyPage() {
  return <div>My New Page</div>;
}
```

2. 添加路由:
```jsx
// frontend/src/router/index.jsx
import MyPage from '@/pages/MyPage';

{
  path: '/my-page',
  element: <MyPage />
}
```

3. 创建API服务:
```javascript
// frontend/src/services/myService.js
import api from './api';

export const getMyData = () => api.get('/my/data');
```

## 测试

### 后端测试
```bash
pytest tests/backend/
```

### 前端测试
```bash
cd frontend
npm test
```

### API测试
使用Postman导入 `docs/postman_collection.json`

## 部署

### Docker部署(推荐)

```bash
docker-compose up -d
```

### 手动部署

详见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 常见问题

### 1. 端口被占用
修改 `.env` 中的 `BACKEND_PORT` 和前端的 `vite.config.js`

### 2. BERT模型下载失败
设置环境变量:
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 3. Doubao API报错
检查 `.env` 中的 `DOUBAO_API_KEY` 是否正确

### 4. 数据库初始化失败
删除 `database/ai_teaching.db` 重新运行:
```bash
python scripts/init_db.py
```

## 更新日志

### v1.0.0 (2025-12-15)
- 🎉 初始版本发布
- ✅ 整合5个子项目为统一平台
- ✅ 实现JWT统一认证
- ✅ 集成BERT AI批改
- ✅ 集成Doubao API
- ✅ 完整的用户、课程、视频、测验功能

## 贡献指南

欢迎贡献代码!请遵循以下步骤:

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议,欢迎提Issue!

## 致谢

感谢所有贡献者和开源项目:
- Flask
- React
- Ant Design
- BERT (Hugging Face)
- 火山引擎Doubao API

---

**当前版本**: v1.0.0
**最后更新**: 2025-12-15
**项目状态**: ✅ 整合完成,可投入使用
