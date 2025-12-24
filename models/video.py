"""
视频模型
整合自: py fl/app.py
"""
from datetime import datetime
# 统一使用从 models 导入的方式
try:
    from . import db
except ImportError:
    try:
        from models import db
    except ImportError:
        from backend import db


class Video(db.Model):
    """教学视频"""
    __tablename__ = 'videos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    duration = db.Column(db.Integer, default=0)  # 视频时长（秒）
    order_index = db.Column(db.Integer, default=0)
    is_free = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Video {self.title}>'

# ===== 删除从这里开始的所有内容 =====
# 不要有第二个 class Video(db.Model) 定义！
# ====================================
