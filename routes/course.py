# backend/routes/course.py
from flask import Blueprint, request, jsonify
from routes.auth import token_required

course_bp = Blueprint('course', __name__, url_prefix='/api/courses')

@course_bp.route('/', methods=['GET'])
@token_required
def get_courses(current_user):
    """获取课程列表"""
    # 根据用户角色返回不同课程列表
    pass

@course_bp.route('/', methods=['POST'])
@token_required
def create_course(current_user):
    """创建课程（教师权限）"""
    pass

@course_bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course_detail(current_user, course_id):
    """获取课程详情"""
    pass