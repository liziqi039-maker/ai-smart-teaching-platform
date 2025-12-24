"""
测验模型
整合自: py fl/app.py 和 lyj3/lyj3.py
"""
from datetime import datetime
import json

# 统一使用从 models 导入的方式
try:
    from . import db
except ImportError:
    try:
        from models import db
    except ImportError:
        from backend import db


class Quiz(db.Model):
    """测验题目"""
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=True)  # 可以为空，表示独立测验
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON格式存储选项
    answer = db.Column(db.String(200))
    type = db.Column(db.String(20), default='objective')  # objective, subjective
    timestamp = db.Column(db.Integer, nullable=True)  # 视频中的时间点（秒），可为空
    
    # 从 lyj3.py 添加的字段
    anchor = db.Column(db.String(50))  # 页面锚点，如 "obj1", "sub1"
    knowledge_point = db.Column(db.String(200))
    explanation = db.Column(db.Text)
    reference_answer = db.Column(db.Text)  # 主观题参考答案
    
    # 相似题目信息（JSON格式）
    similar_questions = db.Column(db.Text)
    
    # 题目难度和分类
    difficulty = db.Column(db.Integer, default=1)  # 1-5级难度
    category = db.Column(db.String(100))  # 分类，如 "Python基础语法"
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Quiz, self).__init__(**kwargs)
        if not self.anchor:
            self.anchor = f"{self.type}_{self.id}"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'question': self.question,
            'options': json.loads(self.options) if self.options else [],
            'answer': self.answer,
            'type': self.type,
            'anchor': self.anchor or f"{self.type}_{self.id}",
            'knowledge_point': self.knowledge_point,
            'explanation': self.explanation,
            'reference_answer': self.reference_answer,
            'similar_questions': json.loads(self.similar_questions) if self.similar_questions else [],
            'difficulty': self.difficulty,
            'category': self.category,
            'video_id': self.video_id,
            'timestamp': self.timestamp,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Quiz {self.id}: {self.question[:30]}>'


class QuizSubmission(db.Model):
    """测验提交记录"""
    __tablename__ = 'quiz_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)  # 可以为空，用于静态题库
    answers = db.Column(db.Text)  # JSON格式存储所有答案
    score = db.Column(db.Float)
    ai_feedback = db.Column(db.Text)
    similarity_score = db.Column(db.Float)  # BERT相似度得分
    
    # 测验类型：static（静态题库）或 video（视频随堂测验）
    quiz_type = db.Column(db.String(20), default='static')
    
    # 额外信息
    total_questions = db.Column(db.Integer, default=0)
    correct_questions = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)  # 用时（秒）
    
    # 详细结果（JSON格式）
    detailed_results = db.Column(db.Text)
    
    # 时间戳
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'quiz_type': self.quiz_type,
            'score': self.score,
            'ai_feedback': self.ai_feedback,
            'similarity_score': self.similarity_score,
            'total_questions': self.total_questions,
            'correct_questions': self.correct_questions,
            'duration': self.duration,
            'answers': json.loads(self.answers) if self.answers else {},
            'detailed_results': json.loads(self.detailed_results) if self.detailed_results else {},
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None
        }

    def __repr__(self):
        return f'<QuizSubmission user_id={self.user_id} quiz_type={self.quiz_type} score={self.score}>'


class QuizSimilarQuestion(db.Model):
    """相似题目关系"""
    __tablename__ = 'quiz_similar_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    similar_quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    similarity_score = db.Column(db.Float)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    quiz = db.relationship('Quiz', foreign_keys=[quiz_id], backref='related_similarities')
    similar_quiz = db.relationship('Quiz', foreign_keys=[similar_quiz_id])

    def __repr__(self):
        return f'<QuizSimilarQuestion quiz_id={self.quiz_id} similar_id={self.similar_quiz_id}>'


class QuizStatistics(db.Model):
    """测验统计"""
    __tablename__ = 'quiz_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_type = db.Column(db.String(20), default='static')
    
    # 统计数据
    total_quizzes = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    best_score = db.Column(db.Float, default=0.0)
    worst_score = db.Column(db.Float, default=0.0)
    total_correct = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    
    # 按知识点统计（JSON格式）
    knowledge_statistics = db.Column(db.Text)
    
    # 按难度统计（JSON格式）
    difficulty_statistics = db.Column(db.Text)
    
    # 弱项分析（JSON格式）
    weak_areas = db.Column(db.Text)
    
    # 时间戳
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('quiz_statistics', lazy=True))

    def to_dict(self):
        """转换为字典格式"""
        return {
            'user_id': self.user_id,
            'quiz_type': self.quiz_type,
            'total_quizzes': self.total_quizzes,
            'average_score': self.average_score,
            'best_score': self.best_score,
            'worst_score': self.worst_score,
            'accuracy_rate': self.total_correct / self.total_questions * 100 if self.total_questions > 0 else 0,
            'knowledge_statistics': json.loads(self.knowledge_statistics) if self.knowledge_statistics else {},
            'difficulty_statistics': json.loads(self.difficulty_statistics) if self.difficulty_statistics else {},
            'weak_areas': json.loads(self.weak_areas) if self.weak_areas else [],
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<QuizStatistics user_id={self.user_id} avg_score={self.average_score}>'