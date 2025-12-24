# 鍦?user.py 鏂囦欢椤堕儴娣诲姞
try:
    from . import db
except ImportError:
    from models import db

# 纭繚 db 涓嶆槸 None
if db is None:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()

# backend/models/user.py
import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# 娣诲姞 backend 鍒版ā鍧楁悳绱㈣矾寰?
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from db_instance import db


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)

    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    __tablename__ = 'permissions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    module = db.Column(db.String(50))

    def __repr__(self):
        return f'<Permission {self.code}>'


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(100))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    student_id = db.Column(db.String(50))
    employee_id = db.Column(db.String(50))

    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)

    avatar = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'role': self.role.name if self.role else None,
            'student_id': self.student_id,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'avatar': self.avatar,
            'phone': self.phone,
            'gender': self.gender,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class UserStats(db.Model):
    __tablename__ = 'user_stats'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', backref=db.backref('stats', uselist=False))

    total_study_time = db.Column(db.Integer, default=0)
    courses_enrolled = db.Column(db.Integer, default=0)
    assignments_completed = db.Column(db.Integer, default=0)
    quiz_average_score = db.Column(db.Float, default=0.0)

    questions_asked = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    forum_posts = db.Column(db.Integer, default=0)

    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_study_time': self.total_study_time,
            'courses_enrolled': self.courses_enrolled,
            'assignments_completed': self.assignments_completed,
            'quiz_average_score': self.quiz_average_score,
            'questions_asked': self.questions_asked,
            'questions_answered': self.questions_answered,
            'forum_posts': self.forum_posts,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

    def __repr__(self):
        return f'<UserStats user_id={self.user_id}>'

