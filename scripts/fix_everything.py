"""
AI教学平台终极修复脚本 - 一个脚本解决所有问题
"""
import sqlite3
import os
import sys
from pathlib import Path
import hashlib
import binascii

def main():
    print("🔧 AI教学平台终极修复")
    print("=" * 60)
    
    # 第1步：修复数据库配置
    print("\n1️⃣ 修复数据库配置...")
    fix_config()
    
    # 第2步：修复数据库表
    print("\n2️⃣ 修复数据库表...")
    fix_database()
    
    # 第3步：重启建议
    print("\n" + "=" * 60)
    print("✅ 修复完成！")
    print("\n📋 下一步操作：")
    print("1. 在运行后端服务的终端中按 Ctrl+C 停止服务")
    print("2. 重新启动服务：")
    print("   cd backend")
    print("   python app.py")
    print("3. 在新终端测试登录：")
    print("   $login = @{username='admin';password='admin123'} | ConvertTo-Json")
    print("   Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' -Method Post -Body $login -ContentType 'application/json'")
    print("=" * 60)

def fix_config():
    """修复配置文件"""
    config_path = Path("backend/config.py")
    
    if not config_path.exists():
        print("   ❌ 配置文件不存在")
        return
    
    # 读取原文件
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换内存数据库为文件数据库
    if "sqlite:///:memory:" in content:
        new_content = content.replace(
            "sqlite:///:memory:", 
            "f'sqlite:///{Path(__file__).parent.parent / \"database\" / \"ai_teaching.db\"}'"
        )
        
        # 添加必要的导入
        if "from pathlib import Path" not in new_content:
            lines = new_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    lines.insert(i + 1, "from pathlib import Path")
                    break
            new_content = '\n'.join(lines)
        
        # 备份并写入
        backup_path = config_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("   ✅ 配置文件已更新：内存数据库 → 文件数据库")
    else:
        print("   ✅ 配置文件已正确配置")

def fix_database():
    """修复数据库"""
    db_path = Path("database/ai_teaching.db")
    
    if not db_path.exists():
        print("   ❌ 数据库文件不存在")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"   发现 {len(tables)} 个表")
    
    # 2. 修复用户表
    if 'users' in tables:
        print("   ✅ users表已存在")
        # 检查users表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password_hash' not in columns:
            print("   🔧 添加password_hash字段到users表")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            except:
                print("   ⚠️  添加字段失败，可能已存在")
    else:
        print("   🔧 创建users表")
        create_users_table(cursor)
    
    # 3. 删除重复的简单表
    for table in ['user', 'course', 'quiz']:
        if table in tables:
            print(f"   🗑️  删除重复的{table}表")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    # 4. 更新admin密码
    update_admin_password(cursor)
    
    # 5. 提交更改
    conn.commit()
    conn.close()
    print("   ✅ 数据库修复完成")

def create_users_table(cursor):
    """创建完整的users表"""
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        real_name TEXT,
        role_id INTEGER,
        student_id TEXT,
        employee_id TEXT,
        is_active BOOLEAN DEFAULT 1,
        is_verified BOOLEAN DEFAULT 0,
        is_teacher BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    """)
    
    # 插入测试用户
    users = [
        ('admin', 'admin@example.com', hash_password('admin123'), '系统管理员', 1, 1, 1),
        ('teacher001', 'teacher@example.com', hash_password('123456'), '张老师', 2, 1, 1),
        ('student001', 'student1@example.com', hash_password('123456'), '李同学', 3, 1, 1),
        ('student002', 'student2@example.com', hash_password('123456'), '王同学', 3, 1, 1)
    ]
    
    for username, email, password_hash, real_name, role_id, is_active, is_verified in users:
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, real_name, role_id, is_active, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, real_name, role_id, is_active, is_verified))

def update_admin_password(cursor):
    """更新admin密码"""
    # 检查admin用户是否存在
    cursor.execute("SELECT username FROM users WHERE username='admin'")
    if not cursor.fetchone():
        print("   🔧 创建admin用户")
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, real_name, role_id, is_active, is_verified)
        VALUES ('admin', 'admin@example.com', ?, '系统管理员', 1, 1, 1)
        """, (hash_password('admin123'),))
    else:
        print("   🔧 更新admin密码")
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", 
                      (hash_password('admin123'),))

def hash_password(password):
    """创建密码哈希"""
    salt = b'ai_teaching_platform_salt'
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"pbkdf2:sha256:100000${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

if __name__ == '__main__':
    main()