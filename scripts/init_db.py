#!/usr/bin/env python
"""
数据库初始化脚本 - 简化版
"""
import sys
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建最简单的Flask应用
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/ai_teaching.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 在应用内部创建db实例
db = SQLAlchemy(app)

# ===== 定义所有模型（就在这个文件中）=====

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)

class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    module = db.Column(db.String(50))

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(100))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class UserStats(db.Model):
    """用户统计模型"""
    __tablename__ = 'user_stats'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', backref=db.backref('stats', uselist=False))

    total_study_time = db.Column(db.Integer, default=0)
    courses_enrolled = db.Column(db.Integer, default=0)

class Course(db.Model):
    """课程模型"""
    __tablename__ = 'courses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(50))
    level = db.Column(db.String(20))
    duration = db.Column(db.Integer)
    price = db.Column(db.Float, default=0.0)
    is_published = db.Column(db.Boolean, default=False)

class Video(db.Model):
    """视频模型"""
    __tablename__ = 'videos'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    duration = db.Column(db.Integer, default=0)
    order_index = db.Column(db.Integer, default=0)
    is_free = db.Column(db.Boolean, default=False)

class Chapter(db.Model):
    """章节模型"""
    __tablename__ = 'chapters'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)

# ===== 数据库初始化函数 =====

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    with app.app_context():
        try:
            # 删除所有表并重新创建
            print("  [1/4] 创建数据库表...")
            db.drop_all()
            db.create_all()
            print("  ✓ 数据库表创建完成")
            
            # 检查是否已初始化
            if Role.query.first():
                print("  ⚠ 数据库已初始化,跳过数据导入")
                return

            # 创建角色
            print("  [2/4] 创建角色...")
            roles_data = [
                {
                    'name': 'admin',
                    'display_name': '管理员',
                    'description': '系统管理员',
                    'permissions': 'all'
                },
                {
                    'name': 'student',
                    'display_name': '学生',
                    'description': '学习课程、提交作业、参与测验',
                    'permissions': json.dumps([
                        'view_course',
                        'submit_assignment',
                        'take_quiz',
                        'view_own_stats'
                    ])
                },
                {
                    'name': 'teacher',
                    'display_name': '教师',
                    'description': '创建课程、编辑教材、批改作业、查看统计',
                    'permissions': json.dumps([
                        'create_course',
                        'edit_course',
                        'delete_course',
                        'upload_material',
                        'grade_assignment',
                        'create_quiz',
                        'view_all_stats',
                        'manage_students'
                    ])
                },
                {
                    'name': 'ai_assistant',
                    'display_name': 'AI助教',
                    'description': '智能答疑、自动批改、数据分析',
                    'permissions': json.dumps([
                        'answer_question',
                        'auto_grade',
                        'generate_quiz',
                        'analyze_data'
                    ])
                }
            ]

            roles = {}
            for role_data in roles_data:
                role = Role(**role_data)
                db.session.add(role)
                roles[role_data['name']] = role

            db.session.commit()
            print(f"  ✓ 已创建 {len(roles)} 个角色")

            # 创建权限
            print("  [3/4] 创建权限...")
            permissions_data = [
                {'name': '查看课程', 'code': 'view_course', 'module': 'course'},
                {'name': '创建课程', 'code': 'create_course', 'module': 'course'},
                {'name': '编辑课程', 'code': 'edit_course', 'module': 'course'},
                {'name': '删除课程', 'code': 'delete_course', 'module': 'course'},
                {'name': '上传资料', 'code': 'upload_material', 'module': 'material'},
                {'name': '提交作业', 'code': 'submit_assignment', 'module': 'assignment'},
                {'name': '批改作业', 'code': 'grade_assignment', 'module': 'assignment'},
                {'name': '参与测验', 'code': 'take_quiz', 'module': 'quiz'},
                {'name': '创建测验', 'code': 'create_quiz', 'module': 'quiz'},
                {'name': '查看个人统计', 'code': 'view_own_stats', 'module': 'stats'},
                {'name': '查看全部统计', 'code': 'view_all_stats', 'module': 'stats'},
                {'name': '管理学生', 'code': 'manage_students', 'module': 'student'},
                {'name': '智能答疑', 'code': 'answer_question', 'module': 'ai'},
                {'name': '自动批改', 'code': 'auto_grade', 'module': 'ai'},
                {'name': '生成测验', 'code': 'generate_quiz', 'module': 'ai'},
                {'name': '数据分析', 'code': 'analyze_data', 'module': 'ai'},
            ]

            for perm_data in permissions_data:
                permission = Permission(**perm_data)
                db.session.add(permission)

            db.session.commit()
            print(f"  ✓ 已创建 {len(permissions_data)} 个权限")

            # 创建默认用户
            print("  [4/4] 创建测试用户...")
            
            # 创建管理员用户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员',
                role=roles['admin'],
                is_teacher=True,
                is_verified=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # 为管理员创建统计数据
            admin_stats = UserStats(user=admin_user)
            db.session.add(admin_stats)
            
            default_users = [
                {
                    'username': 'teacher001',
                    'password': '123456',
                    'email': 'teacher001@example.com',
                    'real_name': '张老师',
                    'role': roles['teacher'],
                    'employee_id': 'T20240001',
                },
                {
                    'username': 'student001',
                    'password': '123456',
                    'email': 'student001@example.com',
                    'real_name': '李同学',
                    'role': roles['student'],
                    'student_id': 'S20240001',
                },
                {
                    'username': 'student002',
                    'password': '123456',
                    'email': 'student002@example.com',
                    'real_name': '王同学',
                    'role': roles['student'],
                    'student_id': 'S20240002',
                },
                {
                    'username': 'ai_assistant',
                    'password': '123456',
                    'email': 'ai@example.com',
                    'real_name': 'AI助教小智',
                    'role': roles['ai_assistant']
                }
            ]

            for user_data in default_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    real_name=user_data['real_name'],
                    role=user_data['role'],
                    is_active=True,
                    is_verified=True,
                    is_teacher=(user_data['role'].name == 'teacher')
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                db.session.flush()

                # 为每个用户创建统计数据
                user_stats = UserStats(user_id=user.id)
                db.session.add(user_stats)

            db.session.commit()
            print(f"  ✓ 已创建 {len(default_users) + 1} 个测试用户（包含管理员）")

            # 创建示例课程
            course = Course(
                title='AI教学平台入门教程',
                description='学习如何使用AI教学平台的基本功能',
                teacher_id=admin_user.id,
                category='技术',
                level='beginner',
                duration=120,
                is_published=True
            )
            db.session.add(course)
            db.session.commit()
            print("  ✓ 示例课程创建完成")

            print("\n✅ 数据库初始化完成!\n")
            print("="*60)
            print("默认测试账号:")
            print("  管理员: admin / admin123")
            print("  教师: teacher001 / 123456")
            print("  学生: student001 / 123456")
            print("  学生: student002 / 123456")
            print("  AI助教: ai_assistant / 123456")
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    init_database()