"""
笔记和字幕翻译模型
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


class Note(db.Model):
    """学习笔记"""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    content = db.Column(db.Text)
    timestamp = db.Column(db.Integer)  # 笔记在视频中的时间点
    summary = db.Column(db.Text)  # AI生成的摘要

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Note user_id={self.user_id} video_id={self.video_id}>'


class SubtitleTranslation(db.Model):
    """字幕翻译缓存"""
    __tablename__ = 'subtitle_translations'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    source_lang = db.Column(db.String(10))
    target_lang = db.Column(db.String(10))
    original_text = db.Column(db.Text)
    translated_text = db.Column(db.Text)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SubtitleTranslation video_id={self.video_id} {self.source_lang}->{self.target_lang}>'
