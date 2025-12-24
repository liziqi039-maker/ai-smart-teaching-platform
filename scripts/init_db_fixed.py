#!/usr/bin/env python
"""
数据库初始化脚本 - 使用绝对路径
"""
import sys
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'ai_teaching.db')

# 确保数据库目录存在
os.makedirs(DATABASE_DIR, exist_ok=True)

print(f"数据库路径: {DATABASE_PATH}")
print(f"数据库目录: {DATABASE_DIR}")

# 检查是否有写入权限
try:
    test_file = os.path.join(DATABASE_DIR, 'test_write.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("✅ 有写入权限")
except Exception as e:
    print(f"❌ 没有写入权限: {e}")

# 创建最简单的Flask应用
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# 使用绝对路径
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 在应用内部创建db实例
db = SQLAlchemy(app)

# ===== 定义所有模型 =====

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)

# ... [其他模型定义保持不变，直接使用之前修复版中的模型定义] ...

# ===== 数据库初始化函数 =====

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    with app.app_context():
        try:
            # 先尝试创建表，不删除原有表
            print("  [1/4] 创建数据库表...")
            db.create_all()
            print("  ✓ 数据库表创建完成")
            
            # 检查是否已初始化
            if Role.query.first():
                print("  ⚠ 数据库已有数据，跳过数据导入")
                return

            # ... [这里插入之前修复版中的角色、权限、用户创建代码] ...

        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    init_database()
