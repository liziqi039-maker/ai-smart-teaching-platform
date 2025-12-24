"""
JWT工具函数
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

# 修复导入路径 - 这是关键
try:
    from models import User
except ImportError:
    # 备用导入路径
    import sys
    from pathlib import Path
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent
    sys.path.insert(0, str(backend_dir))
    from models import User


def token_required(f):
    """JWT Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)

            if not current_user:
                return jsonify({'error': '用户不存在'}), 404

            if not current_user.is_active:
                return jsonify({'error': '账户已被禁用'}), 403

            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token验证失败', 'message': str(e)}), 401

    return decorated


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)

            if not current_user:
                return jsonify({'error': '用户不存在'}), 404

            # 假设 User 模型有 role 字段，且是字符串
            if not current_user.role or current_user.role not in ['admin', 'teacher', 'ai_assistant']:
                return jsonify({'error': '权限不足'}), 403

            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token验证失败', 'message': str(e)}), 401

    return decorated


def teacher_required(f):
    """教师权限验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)

            if not current_user:
                return jsonify({'error': '用户不存在'}), 404

            if not current_user.role or current_user.role != 'teacher':
                return jsonify({'error': '只有教师可以访问'}), 403

            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token验证失败', 'message': str(e)}), 401

    return decorated
def roles_required(*roles):
    """角色权限验证装饰器"""
    from functools import wraps
    from flask import jsonify
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # 这里需要根据你的用户模型获取用户角色
                from models import User
                current_user = User.query.get(current_user_id)
                
                if not current_user or not current_user.role:
                    return jsonify({'error': '用户没有分配角色'}), 403
                
                # 检查用户角色是否在允许的角色列表中
                if current_user.role.name not in roles:
                    return jsonify({'error': '权限不足'}), 403
                    
                return f(current_user, *args, **kwargs)
            except Exception as e:
                return jsonify({'error': '权限验证失败', 'message': str(e)}), 401
        return decorated_function
    return decorator