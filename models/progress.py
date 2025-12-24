"""
学习进度模型
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


class UserProgress(db.Model):
    """用户学习进度"""
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # 观看进度（秒）
    completed = db.Column(db.Boolean, default=False)
    playback_rate = db.Column(db.Float, default=1.0)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'video_id', name='uq_user_video'),
    )

    def __repr__(self):
        return f'<UserProgress user_id={self.user_id} video_id={self.video_id}>'


# 为兼容性添加别名
Progress = UserProgress
