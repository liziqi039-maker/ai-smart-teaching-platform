"""
验证数据库数据完整性
"""
import sqlite3
import json
from pathlib import Path

def verify_database():
    """验证数据库完整性"""
    db_path = Path(__file__).parent.parent / "database" / "ai_teaching.db"
    
    print("🔍 数据库验证工具")
    print("=" * 60)
    print(f"数据库: {db_path}")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. 验证用户表
    print("\n1. 用户验证:")
    cursor.execute("SELECT username, real_name, role_id FROM users")
    users = cursor.fetchall()
    
    print(f"   用户数量: {len(users)}")
    for username, real_name, role_id in users:
        cursor.execute("SELECT name FROM roles WHERE id = ?", (role_id,))
        role_name = cursor.fetchone()
        role = role_name[0] if role_name else "未知"
        print(f"   - {username} ({real_name}): {role}")
    
    # 2. 验证角色权限
    print("\n2. 角色权限验证:")
    cursor.execute("SELECT name, display_name, permissions FROM roles")
    roles = cursor.fetchall()
    
    for name, display_name, permissions in roles:
        try:
            perm_list = json.loads(permissions) if permissions != 'all' else ['all']
            print(f"   - {display_name} ({name}): {len(perm_list)} 个权限")
        except:
            print(f"   - {display_name} ({name}): {permissions}")
    
    # 3. 验证题库
    print("\n3. 题库验证:")
    cursor.execute("""
    SELECT type, COUNT(*) as count, 
           AVG(difficulty) as avg_difficulty 
    FROM quizzes 
    GROUP BY type
    """)
    quiz_stats = cursor.fetchall()
    
    for quiz_type, count, avg_diff in quiz_stats:
        print(f"   - {quiz_type}题: {count} 道，平均难度: {avg_diff:.1f}")
    
    # 4. 验证表结构
    print("\n4. 表结构验证:")
    cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' 
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"   有效表数量: {len(tables)}")
    
    # 检查关键表
    key_tables = ['users', 'roles', 'courses', 'quizzes', 'quiz_statistics']
    missing_tables = [t for t in key_tables if t not in tables]
    
    if missing_tables:
        print(f"   ⚠️  缺少关键表: {missing_tables}")
    else:
        print("   ✅ 所有关键表都存在")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据库验证完成")
    
    # 显示建议
    if 'user' in tables and 'users' in tables:
        print("\n⚠️  注意：发现重复表 'user' 和 'users'")
        print("   建议清理旧表：")
        print("   sqlite3 database\\ai_teaching.db \"DROP TABLE IF EXISTS user;\"")
    
    return True

if __name__ == '__main__':
    verify_database()