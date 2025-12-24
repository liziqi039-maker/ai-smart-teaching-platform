import sqlite3

# 直接使用相对路径
db_path = "database/ai_teaching.db"
conn = sqlite3.connect(db_path)
print("✅ 数据库连接成功")

# 执行一些操作
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"数据库中的表: {tables}")

conn.close()