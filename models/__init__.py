"""
数据库模型模块
统一导入所有模型，避免循环导入问题
"""

# ========== 修复：使用统一的db实例 ==========
try:
    from db_instance import db
    print("✅ models/__init__.py: 从db_instance导入统一的db实例")
except ImportError as e:
    print(f"⚠️  models/__init__.py: 无法导入db_instance: {e}")
    # 创建临时db实例（应该不会执行到这里）
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
# ===========================================

# 现在导入所有模型 - 确保在 db 定义之后
try:
    from .user import User, Role, Permission, UserStats
    print("✅ 导入User模型")
except ImportError as e:
    print(f"⚠️  导入用户模型失败: {e}")
    User = Role = Permission = UserStats = None

# 导入其他模型（如果文件存在）
try:
    from .course import Course
    print("✅ 导入Course模型")
except ImportError as e:
    Course = None
    print(f"⚠️  导入Course模型失败: {e}")

try:
    from .video import Video
    print("✅ 导入Video模型")
except ImportError as e:
    Video = None
    print(f"⚠️  导入Video模型失败: {e}")

try:
    from .progress import UserProgress
    # 为兼容性添加别名
    Progress = UserProgress
    print("✅ 导入Progress模型")
except ImportError as e:
    Progress = None
    UserProgress = None
    print(f"⚠️  导入Progress模型失败: {e}")

# ========== 修复：完整导入测验相关模型 ==========
try:
    from .quiz import Quiz, QuizSubmission, QuizSimilarQuestion, QuizStatistics
    print("✅ 导入Quiz模型")
    print("✅ 导入QuizSubmission模型")
    print("✅ 导入QuizSimilarQuestion模型")
    print("✅ 导入QuizStatistics模型")
except ImportError as e:
    Quiz = None
    QuizSubmission = None
    QuizSimilarQuestion = None
    QuizStatistics = None
    print(f"⚠️  导入测验模型失败: {e}")
# ===============================================

try:
    from .note import Note, SubtitleTranslation
    print("✅ 导入Note模型")
except ImportError as e:
    Note = None
    SubtitleTranslation = None
    print(f"⚠️  导入Note模型失败: {e}")

# ==== 简单定义 Chapter 类（就在这里定义，不导入）====
class Chapter(db.Model):
    """课程章节"""
    __tablename__ = 'chapters'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Chapter {self.title}>'
# =================================================

# 导出所有模型
__all__ = [
    'db', 'User', 'Role', 'Permission', 'UserStats',
    'Course', 'Video', 'Progress', 'UserProgress', 
    'Quiz', 'QuizSubmission', 'QuizSimilarQuestion', 'QuizStatistics',
    'Note', 'SubtitleTranslation', 'Chapter'
]