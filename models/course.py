"""
课程模型
"""

# 修复导入 - 这是关键
try:
    # 从 models 包导入 db
    from . import db
except ImportError:
    # 备用方案
    from models import db

# 确保 db 不是 None
if db is None:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()

class Course(db.Model):
    """课程模型"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(50))
    level = db.Column(db.String(20))  # beginner, intermediate, advanced
    duration = db.Column(db.Integer)  # 分钟
    price = db.Column(db.Float, default=0.0)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    # 关系
    teacher = db.relationship('User', backref='taught_courses')
    videos = db.relationship('Video', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'category': self.category,
            'level': self.level,
            'duration': self.duration,
            'price': self.price,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
