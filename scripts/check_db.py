"""
检查数据库内容
"""
import sqlite3
import os
from pathlib import Path

def check_database():
    """检查数据库内容和结构"""
    print("🔍 数据库检查工具")
    print("=" * 60)
    
    # 可能的数据库路径
    possible_paths = [
        Path(__file__).parent.parent / "database" / "ai_teaching.db",
        Path(__file__).parent.parent / "backend" / "database" / "ai-teaching.db",
        Path(__file__).parent.parent / "backend" / "database" / "ai_teaching.db",
        Path(__file__).parent.parent / "ai_teaching.db",
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            print(f"✅ 找到数据库: {path}")
            break
    
    if not db_path:
        print("❌ 未找到数据库文件")
        return
    
    print(f"数据库大小: {db_path.stat().st_size / 1024:.1f} KB")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 1. 查看所有表
        print("\n1. 数据库中的所有表:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = cursor.fetchall()
        
        if not tables:
            print("   ⚠️  数据库中没有用户表")
        else:
            print(f"   共有 {len(tables)} 个表:")
            for table in tables:
                # 查看每个表的记录数
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"   - {table[0]}: {count} 条记录")
                except:
                    print(f"   - {table[0]}: 无法查询")
        
        # 2. 特别检查用户相关的表
        print("\n2. 用户相关表检查:")
        user_tables = []
        for table in tables:
            if 'user' in table[0].lower():
                user_tables.append(table[0])
        
        if user_tables:
            print(f"   找到用户表: {user_tables}")
            for table in user_tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"   {table} 表结构 ({len(columns)} 个字段):")
                # 显示前5个字段
                for col in columns[:5]:
                    print(f"     - {col[1]} ({col[2]})")
                if len(columns) > 5:
                    print(f"     ... 还有 {len(columns)-5} 个字段")
                
                # 显示用户数据
                cursor.execute(f"SELECT id, username, real_name FROM {table} LIMIT 3")
                users = cursor.fetchall()
                if users:
                    print(f"   表中的用户数据:")
                    for user in users:
                        print(f"     - ID:{user[0]}, 用户名:{user[1]}, 姓名:{user[2]}")
        else:
            print("   ⚠️  没有找到用户相关的表")
        
        # 3. 检查外键约束
        print("\n3. 外键检查:")
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        if fk_errors:
            print("   ⚠️  发现外键错误:")
            for error in fk_errors:
                print(f"   - {error}")
        else:
            print("   ✅ 外键检查正常")
        
        # 4. 数据库完整性检查
        print("\n4. 数据库完整性检查:")
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()
        print(f"   {integrity[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_database()