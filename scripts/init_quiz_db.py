"""
初始化测验数据库
"""
import sys
import os
import json
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent  # scripts目录
project_root = current_dir.parent    # 项目根目录
backend_dir = project_root / "backend"

# 添加项目根目录和backend目录到Python路径
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

print(f"项目根目录: {project_root}")
print(f"Backend目录: {backend_dir}")

try:
    # 尝试不同的导入方式
    try:
        from backend.models import db, Quiz, QuizStatistics, QuizSubmission
        from backend.models.user import User
    except ImportError:
        try:
            from models import db, Quiz, QuizStatistics, QuizSubmission
            from models.user import User
        except ImportError as e:
            print(f"导入模块失败: {e}")
            print("正在尝试直接导入...")
            
            # 尝试直接导入模块
            import importlib.util
            
            # 导入db
            spec = importlib.util.spec_from_file_location("db", backend_dir / "__init__.py")
            db_module = importlib.util.module_from_spec(spec)
            sys.modules["db"] = db_module
            spec.loader.exec_module(db_module)
            
            # 导入Quiz模型
            spec = importlib.util.spec_from_file_location("quiz", backend_dir / "models" / "quiz.py")
            quiz_module = importlib.util.module_from_spec(spec)
            sys.modules["quiz"] = quiz_module
            spec.loader.exec_module(quiz_module)
            
            db = getattr(quiz_module, 'db', None)
            Quiz = getattr(quiz_module, 'Quiz', None)
            QuizSubmission = getattr(quiz_module, 'QuizSubmission', None)
            QuizStatistics = getattr(quiz_module, 'QuizStatistics', None)
            
            # 导入User模型
            spec = importlib.util.spec_from_file_location("user", backend_dir / "models" / "user.py")
            user_module = importlib.util.module_from_spec(spec)
            sys.modules["user"] = user_module
            spec.loader.exec_module(user_module)
            User = getattr(user_module, 'User', None)
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def init_quiz_database():
    """初始化测验数据库"""
    print("开始初始化测验数据库...")
    
    try:
        # 创建Flask应用上下文
        from backend import create_app
        app = create_app()
    except ImportError:
        print("❌ 无法导入create_app，尝试直接连接数据库...")
        # 如果无法导入create_app，尝试直接连接数据库
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        app = Flask(__name__)
        
        # 从配置文件读取数据库URI
        config_path = backend_dir / "config.py"
        if config_path.exists():
            print(f"📁 读取配置文件: {config_path}")
            # 动态加载配置
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            # 获取配置
            config_class = getattr(config_module, 'Config', None)
            if config_class:
                app.config.from_object(config_class)
            else:
                # 默认配置
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{project_root}/ai_classroom.db'
                app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        else:
            # 默认配置
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{project_root}/ai_classroom.db'
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # 初始化数据库
        db = SQLAlchemy(app)
    
    with app.app_context():
        try:
            # 创建表
            db.create_all()
            print("✅ 测验相关表创建完成")
            
            # 检查是否已有数据
            quiz_count = Quiz.query.count()
            if quiz_count > 0:
                print(f"⚠️  数据库已有 {quiz_count} 条题目，跳过初始化")
                return
            
            # 添加静态题库数据（从 lyj3.py 提取）
            print("📝 添加静态题库数据...")
            
            # 客观题
            objective_questions = [
                {
                    "question": "Python定义函数的关键字是？",
                    "options": json.dumps([
                        {"label": "A", "text": "def"},
                        {"label": "B", "text": "function"},
                        {"label": "C", "text": "func"},
                        {"label": "D", "text": "define"}
                    ], ensure_ascii=False),
                    "answer": "A",
                    "type": "objective",
                    "anchor": "obj1",
                    "knowledge_point": "Python基础语法",
                    "explanation": "Python中使用def（definition的缩写）关键字定义函数，function/func/define均不是Python的内置关键字。",
                    "difficulty": 1,
                    "category": "Python基础语法"
                },
                {
                    "question": "下列哪个不是Python数据类型？",
                    "options": json.dumps([
                        {"label": "A", "text": "list"},
                        {"label": "B", "text": "tuple"},
                        {"label": "C", "text": "array"},
                        {"label": "D", "text": "dict"}
                    ], ensure_ascii=False),
                    "answer": "C",
                    "type": "objective",
                    "anchor": "obj2",
                    "knowledge_point": "Python数据类型",
                    "explanation": "list（列表）、tuple（元组）、dict（字典）是Python内置基础数据类型；array不是Python原生类型，需导入numpy库才能使用。",
                    "difficulty": 2,
                    "category": "Python数据类型"
                },
                {
                    "question": "Python中单行注释的符号是？",
                    "options": json.dumps([
                        {"label": "A", "text": "//"},
                        {"label": "B", "text": "#"},
                        {"label": "C", "text": "/* */"},
                        {"label": "D", "text": "--"}
                    ], ensure_ascii=False),
                    "answer": "B",
                    "type": "objective",
                    "anchor": "obj3",
                    "knowledge_point": "Python基础语法",
                    "explanation": "Python中单行注释用#，多行注释用三引号（'''/\"\"\"）；//和/* */是C/C++注释符号，--是SQL注释符号。",
                    "difficulty": 1,
                    "category": "Python基础语法"
                },
                {
                    "question": "Python中向列表末尾添加元素的方法是？",
                    "options": json.dumps([
                        {"label": "A", "text": "add()"},
                        {"label": "B", "text": "append()"},
                        {"label": "C", "text": "insert()"},
                        {"label": "D", "text": "extend()"}
                    ], ensure_ascii=False),
                    "answer": "B",
                    "type": "objective",
                    "anchor": "obj4",
                    "knowledge_point": "Python列表操作",
                    "explanation": "append()用于向列表末尾添加单个元素；insert()指定位置添加元素；extend()添加可迭代对象（如列表）；Python列表无add()方法。",
                    "difficulty": 2,
                    "category": "Python列表操作"
                },
                {
                    "question": "Python中用于判断数据类型的内置函数是？",
                    "options": json.dumps([
                        {"label": "A", "text": "type()"},
                        {"label": "B", "text": "isinstance()"},
                        {"label": "C", "text": "typeof()"},
                        {"label": "D", "text": "checktype()"}
                    ], ensure_ascii=False),
                    "answer": "A",
                    "type": "objective",
                    "anchor": "obj5",
                    "knowledge_point": "Python类型判断",
                    "explanation": "type()返回对象的精确类型；isinstance()判断对象是否属于指定类/子类（更灵活）；typeof()/checktype()不是Python内置函数。",
                    "difficulty": 2,
                    "category": "Python类型判断"
                }
            ]
            
            # 主观题
            subjective_questions = [
                {
                    "question": "简述Python列表与元组的区别",
                    "reference_answer": "列表是可变序列（可增删改元素），用[]表示；元组是不可变序列，用()表示",
                    "type": "subjective",
                    "anchor": "sub1",
                    "knowledge_point": "Python序列类型",
                    "explanation": "1. 可变性：列表可变（mutable），元组不可变（immutable）；2. 语法：列表用[]，元组用()；3. 性能：元组因不可变，遍历/访问速度略快；4. 用途：列表适合动态修改数据，元组适合存储固定不变的数据（如配置项）。",
                    "difficulty": 2,
                    "category": "Python序列类型"
                },
                {
                    "question": "简述Python中if-else语句的使用场景",
                    "reference_answer": "if-else语句用于根据条件执行不同代码块；单条件判断用if，二选一判断用if-else，多条件分支用if-elif-else。",
                    "type": "subjective",
                    "anchor": "sub2",
                    "knowledge_point": "Python流程控制",
                    "explanation": "1. 基础场景：判断单个条件是否成立（如判断数值大小）；2. 多分支场景：用if-elif-else处理多个互斥条件（如成绩等级判定）；3. 嵌套场景：if语句内部嵌套if-else，处理复杂条件逻辑；4. 注意：else子句可选，仅当所有if/elif条件不成立时执行。",
                    "difficulty": 1,
                    "category": "Python流程控制"
                },
                {
                    "question": "简述Python中异常处理（try-except）的作用",
                    "reference_answer": "try-except用于捕获并处理程序运行时的异常，避免程序崩溃；try包裹可能出错的代码，except捕获指定异常并执行处理逻辑。",
                    "type": "subjective",
                    "anchor": "sub3",
                    "knowledge_point": "Python异常处理",
                    "explanation": "1. 核心作用：防止程序因运行时错误（如除零、索引越界）直接崩溃，提升程序健壮性；2. 常用用法：try-except（捕获所有异常）、try-except-else（无异常时执行else）、try-except-finally（无论是否异常都执行finally，如关闭文件）；3. 场景：文件操作、网络请求、用户输入验证等易出错的场景。",
                    "difficulty": 2,
                    "category": "Python异常处理"
                }
            ]
            
            # 插入题目
            for question in objective_questions + subjective_questions:
                quiz = Quiz(**question)
                db.session.add(quiz)
            
            db.session.commit()
            
            # 添加默认用户测验统计（如果有用户的话）
            try:
                users = User.query.all()
                for user in users:
                    stats = QuizStatistics(
                        user_id=user.id,
                        quiz_type='static',
                        knowledge_statistics=json.dumps({}),
                        difficulty_statistics=json.dumps({}),
                        weak_areas=json.dumps([])
                    )
                    db.session.add(stats)
                
                db.session.commit()
                print(f"✅ 为 {len(users)} 个用户创建了测验统计")
            except Exception as e:
                print(f"⚠️  创建用户统计失败（可能用户表不存在）: {e}")
                db.session.rollback()
            
            print(f"✅ 添加了 {len(objective_questions)} 道客观题和 {len(subjective_questions)} 道主观题")
            print("✅ 初始化测验数据库完成！")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    init_quiz_database()