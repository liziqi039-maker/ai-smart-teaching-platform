"""
统一数据库初始化脚本 - 整合所有初始化功能
"""
import sys
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

# 项目路径
BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "ai_teaching.db"

# 确保数据库目录存在
DATABASE_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("🤖 AI教学平台 - 统一数据库初始化")
print("=" * 60)
print(f"项目根目录: {BASE_DIR}")
print(f"数据库路径: {DATABASE_PATH}")
print("=" * 60)

def check_database_permissions():
    """检查数据库目录权限"""
    try:
        test_file = DATABASE_DIR / "test_write.txt"
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ 数据库目录有写入权限")
        return True
    except Exception as e:
        print(f"❌ 数据库目录无写入权限: {e}")
        return False

def init_core_database():
    """初始化核心数据库（用户、角色、课程等）"""
    print("\n[阶段1] 初始化核心数据库...")
    
    # 创建Flask应用
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # ===== 定义核心模型 =====
    
    class Role(db.Model):
        __tablename__ = 'roles'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        display_name = db.Column(db.String(100))
        description = db.Column(db.Text)
        permissions = db.Column(db.Text)
    
    class User(db.Model):
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
    
    class Course(db.Model):
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
    
    # 创建应用上下文
    with app.app_context():
        try:
            # 删除旧表并重新创建
            print("  1. 创建核心数据库表...")
            db.drop_all()
            db.create_all()
            print("  ✅ 核心表创建完成")
            
            # 创建角色
            print("  2. 创建系统角色...")
            roles_data = [
                {'name': 'admin', 'display_name': '管理员', 'description': '系统管理员', 'permissions': 'all'},
                {'name': 'student', 'display_name': '学生', 'description': '学习课程、提交作业、参与测验', 
                 'permissions': json.dumps(['view_course', 'submit_assignment', 'take_quiz', 'view_own_stats'])},
                {'name': 'teacher', 'display_name': '教师', 'description': '创建课程、编辑教材、批改作业、查看统计',
                 'permissions': json.dumps(['create_course', 'edit_course', 'delete_course', 'upload_material', 
                                           'grade_assignment', 'create_quiz', 'view_all_stats', 'manage_students'])},
                {'name': 'ai_assistant', 'display_name': 'AI助教', 'description': '智能答疑、自动批改、数据分析',
                 'permissions': json.dumps(['answer_question', 'auto_grade', 'generate_quiz', 'analyze_data'])}
            ]
            
            roles = {}
            for role_data in roles_data:
                role = Role(**role_data)
                db.session.add(role)
                roles[role_data['name']] = role
            
            db.session.commit()
            print(f"  ✅ 已创建 {len(roles)} 个角色")
            
            # 创建默认用户
            print("  3. 创建测试用户...")
            default_users = [
                {'username': 'admin', 'email': 'admin@example.com', 'real_name': '系统管理员', 
                 'password': 'admin123', 'role': roles['admin'], 'is_teacher': True},
                {'username': 'teacher001', 'email': 'teacher001@example.com', 'real_name': '张老师',
                 'password': '123456', 'role': roles['teacher'], 'is_teacher': True},
                {'username': 'student001', 'email': 'student001@example.com', 'real_name': '李同学',
                 'password': '123456', 'role': roles['student'], 'is_teacher': False},
                {'username': 'student002', 'email': 'student002@example.com', 'real_name': '王同学',
                 'password': '123456', 'role': roles['student'], 'is_teacher': False}
            ]
            
            for user_data in default_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    real_name=user_data['real_name'],
                    role=user_data['role'],
                    is_active=True,
                    is_verified=True,
                    is_teacher=user_data['is_teacher']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
            
            db.session.commit()
            print(f"  ✅ 已创建 {len(default_users)} 个测试用户")
            
            # 创建示例课程
            print("  4. 创建示例课程...")
            admin_user = User.query.filter_by(username='admin').first()
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
            print("  ✅ 示例课程创建完成")
            
            print("\n  🎉 核心数据库初始化完成!")
            
            return True
            
        except Exception as e:
            print(f"❌ 核心数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def init_quiz_database():
    """初始化测验数据库"""
    print("\n[阶段2] 初始化测验数据库...")
    
    # 连接到数据库
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    try:
        # 检查现有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"  现有表: {', '.join(existing_tables)}")
        
        # 创建测验表（如果不存在）
        quiz_tables = ['quizzes', 'quiz_submissions', 'quiz_statistics']
        created_tables = []
        
        if 'quizzes' not in existing_tables:
            cursor.execute('''
            CREATE TABLE quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                options TEXT,
                answer TEXT,
                type TEXT DEFAULT 'objective',
                anchor TEXT,
                knowledge_point TEXT,
                explanation TEXT,
                reference_answer TEXT,
                difficulty INTEGER DEFAULT 1,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            created_tables.append('quizzes')
        
        if 'quiz_submissions' not in existing_tables:
            cursor.execute('''
            CREATE TABLE quiz_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_id INTEGER,
                answers TEXT,
                score REAL,
                ai_feedback TEXT,
                quiz_type TEXT DEFAULT 'static',
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
            ''')
            created_tables.append('quiz_submissions')
        
        if 'quiz_statistics' not in existing_tables:
            cursor.execute('''
            CREATE TABLE quiz_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_type TEXT DEFAULT 'static',
                knowledge_statistics TEXT DEFAULT '{}',
                difficulty_statistics TEXT DEFAULT '{}',
                weak_areas TEXT DEFAULT '[]',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            created_tables.append('quiz_statistics')
        
        if created_tables:
            print(f"  ✅ 创建了 {len(created_tables)} 个测验表: {', '.join(created_tables)}")
        else:
            print("  ⚠️  所有测验表已存在")
        
        # 检查是否有测验数据
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        quiz_count = cursor.fetchone()[0]
        
        if quiz_count > 0:
            print(f"  ⚠️  数据库中已有 {quiz_count} 条题目，跳过数据导入")
        else:
            # 插入测验数据
            print("  5. 插入静态题库数据...")
            
            # 客观题
            objective_questions = [
                ("Python定义函数的关键字是？",
                 json.dumps([{"label": "A", "text": "def"}, {"label": "B", "text": "function"}, 
                            {"label": "C", "text": "func"}, {"label": "D", "text": "define"}]),
                 "A", "objective", "obj1", "Python基础语法",
                 "Python中使用def（definition的缩写）关键字定义函数，function/func/define均不是Python的内置关键字。",
                 None, 1, "Python基础语法"),
                
                ("下列哪个不是Python数据类型？",
                 json.dumps([{"label": "A", "text": "list"}, {"label": "B", "text": "tuple"}, 
                            {"label": "C", "text": "array"}, {"label": "D", "text": "dict"}]),
                 "C", "objective", "obj2", "Python数据类型",
                 "list（列表）、tuple（元组）、dict（字典）是Python内置基础数据类型；array不是Python原生类型，需导入numpy库才能使用。",
                 None, 2, "Python数据类型"),
                
                ("Python中单行注释的符号是？",
                 json.dumps([{"label": "A", "text": "//"}, {"label": "B", "text": "#"}, 
                            {"label": "C", "text": "/* */"}, {"label": "D", "text": "--"}]),
                 "B", "objective", "obj3", "Python基础语法",
                 "Python中单行注释用#，多行注释用三引号（'''/\"\"\"）；//和/* */是C/C++注释符号，--是SQL注释符号。",
                 None, 1, "Python基础语法"),
                
                ("Python中向列表末尾添加元素的方法是？",
                 json.dumps([{"label": "A", "text": "add()"}, {"label": "B", "text": "append()"}, 
                            {"label": "C", "text": "insert()"}, {"label": "D", "text": "extend()"}]),
                 "B", "objective", "obj4", "Python列表操作",
                 "append()用于向列表末尾添加单个元素；insert()指定位置添加元素；extend()添加可迭代对象（如列表）；Python列表无add()方法。",
                 None, 2, "Python列表操作"),
                
                ("Python中用于判断数据类型的内置函数是？",
                 json.dumps([{"label": "A", "text": "type()"}, {"label": "B", "text": "isinstance()"}, 
                            {"label": "C", "text": "typeof()"}, {"label": "D", "text": "checktype()"}]),
                 "A", "objective", "obj5", "Python类型判断",
                 "type()返回对象的精确类型；isinstance()判断对象是否属于指定类/子类（更灵活）；typeof()/checktype()不是Python内置函数。",
                 None, 2, "Python类型判断")
            ]
            
            # 主观题
            subjective_questions = [
                ("简述Python列表与元组的区别",
                 None, None, "subjective", "sub1", "Python序列类型",
                 "1. 可变性：列表可变（mutable），元组不可变（immutable）；2. 语法：列表用[]，元组用()；3. 性能：元组因不可变，遍历/访问速度略快；4. 用途：列表适合动态修改数据，元组适合存储固定不变的数据（如配置项）。",
                 "列表是可变序列（可增删改元素），用[]表示；元组是不可变序列，用()表示", 2, "Python序列类型"),
                
                ("简述Python中if-else语句的使用场景",
                 None, None, "subjective", "sub2", "Python流程控制",
                 "1. 基础场景：判断单个条件是否成立（如判断数值大小）；2. 多分支场景：用if-elif-else处理多个互斥条件（如成绩等级判定）；3. 嵌套场景：if语句内部嵌套if-else，处理复杂条件逻辑；4. 注意：else子句可选，仅当所有if/elif条件不成立时执行。",
                 "if-else语句用于根据条件执行不同代码块；单条件判断用if，二选一判断用if-else，多条件分支用if-elif-else。", 1, "Python流程控制"),
                
                ("简述Python中异常处理（try-except）的作用",
                 None, None, "subjective", "sub3", "Python异常处理",
                 "1. 核心作用：防止程序因运行时错误（如除零、索引越界）直接崩溃，提升程序健壮性；2. 常用用法：try-except（捕获所有异常）、try-except-else（无异常时执行else）、try-except-finally（无论是否异常都执行finally，如关闭文件）；3. 场景：文件操作、网络请求、用户输入验证等易出错的场景。",
                 "try-except用于捕获并处理程序运行时的异常，避免程序崩溃；try包裹可能出错的代码，except捕获指定异常并执行处理逻辑。", 2, "Python异常处理")
            ]
            
            # 插入客观题
            cursor.executemany('''
            INSERT INTO quizzes (question, options, answer, type, anchor, knowledge_point, explanation, reference_answer, difficulty, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', objective_questions)
            
            # 插入主观题
            cursor.executemany('''
            INSERT INTO quizzes (question, options, answer, type, anchor, knowledge_point, explanation, reference_answer, difficulty, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', subjective_questions)
            
            print(f"  ✅ 添加了 {len(objective_questions)} 道客观题")
            print(f"  ✅ 添加了 {len(subjective_questions)} 道主观题")
            
            # 为用户创建统计记录
            cursor.execute("SELECT id FROM users")
            users = cursor.fetchall()
            
            for user_id, in users:
                cursor.execute('''
                INSERT OR IGNORE INTO quiz_statistics (user_id, quiz_type)
                VALUES (?, 'static')
                ''', (user_id,))
            
            print(f"  ✅ 为 {len(users)} 个用户创建/检查了统计记录")
        
        conn.commit()
        print("\n  🎉 测验数据库初始化完成!")
        
        # 显示统计信息
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        total_quizzes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM quiz_statistics")
        total_users = cursor.fetchone()[0]
        
        print(f"\n  📊 数据库统计:")
        print(f"     题库题目数: {total_quizzes}")
        print(f"     用户统计数: {total_users}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测验数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    print("\n" + "="*60)
    
    # 1. 检查权限
    if not check_database_permissions():
        print("❌ 请检查目录权限后重试")
        return
    
    # 2. 初始化核心数据库
    if not init_core_database():
        print("❌ 核心数据库初始化失败")
        return
    
    # 3. 初始化测验数据库
    if not init_quiz_database():
        print("❌ 测验数据库初始化失败")
        return
    
    # 4. 显示完成信息
    print("\n" + "="*60)
    print("🎉 AI教学平台数据库完整初始化完成!")
    print("="*60)
    print("\n📋 系统概览:")
    print(f"   数据库文件: {DATABASE_PATH}")
    print(f"   数据库大小: {os.path.getsize(DATABASE_PATH) / 1024:.1f} KB")
    
    # 连接到数据库显示最终统计
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 数据库包含 {len(tables)} 个表:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   - {table}: {count} 条记录")
    
    conn.close()
    
    print("\n👤 测试账号:")
    print("   管理员: admin / admin123")
    print("   教师: teacher001 / 123456")
    print("   学生: student001 / 123456")
    print("   学生: student002 / 123456")
    
    print("\n🚀 下一步:")
    print("   1. 启动后端服务: cd backend && python app.py")
    print("   2. 访问测验系统: http://localhost:5000/quiz")
    print("="*60)

if __name__ == '__main__':
    main()