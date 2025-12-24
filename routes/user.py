# backend/routes/user.py
"""
用户管理路由
"""
from flask import Blueprint, request, jsonify
from routes.auth import token_required
from models import User, db

user_bp = Blueprint('user', __name__)

# ========== 现有路由保持不变 ==========

@user_bp.route('/', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'real_name': user.real_name,
                'role': user.role.name if user.role else None,
                'is_active': user.is_active
            } for user in users]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'real_name': user.real_name,
                'role': user.role.name if user.role else None,
                'student_id': user.student_id,
                'employee_id': user.employee_id,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

# ========== 新增current路由 ==========

@user_bp.route('/current', methods=['GET'])
@token_required
def get_current_user(current_user):
    """获取当前登录用户信息（v1版本）"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'real_name': current_user.real_name,
                'role': current_user.role.name if current_user.role else None,
                'student_id': current_user.student_id,
                'employee_id': current_user.employee_id,
                'is_active': current_user.is_active,
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取当前用户信息失败: {str(e)}'
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """更新用户信息（需要token）"""
    try:
        # 权限检查：只能修改自己的信息，或者管理员
        if current_user.id != user_id and not current_user.is_admin:
            return jsonify({
                'success': False,
                'message': '没有权限修改该用户信息'
            }), 403
        
        data = request.get_json()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 更新允许修改的字段
        allowed_fields = ['real_name', 'email']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户信息更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'email': user.email
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新用户信息失败: {str(e)}'
        }), 500