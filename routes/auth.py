# backend/routes/auth.py
import sys
import os

# 动态添加 backend 到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import datetime
import re

from db_instance import db
from models import User, Role, UserStats
from utils.decorators import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        required_fields = ['username', 'password', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少{field}字段'}), 400

        username = data['username'].strip()
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度需在3-20个字符之间'}), 400

        password = data['password']
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6位'}), 400

        email = data['email'].strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'success': False, 'message': '邮箱格式不正确'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '用户名已存在'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': '邮箱已被注册'}), 409

        role = Role.query.filter_by(name=data['role']).first()
        if not role:
            return jsonify({'success': False, 'message': '无效的角色'}), 400

        user = User(
            username=username,
            email=email,
            real_name=data.get('real_name', ''),
            role_id=role.id,
            student_id=data.get('student_id'),
            employee_id=data.get('employee_id'),
            is_active=True,
            is_verified=False,
            is_teacher=(role.name == 'teacher')
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        user_stats = UserStats(user_id=user.id)
        db.session.add(user_stats)

        db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'success': True,
            'message': '注册成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        if not user.check_password(password):
            return jsonify({'success': False, 'message': '密码错误'}), 401
        if not user.is_active:
            return jsonify({'success': False, 'message': '账户已被禁用'}), 403

        user.last_login = datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'success': True,
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({'success': True, 'user': current_user.to_dict()})


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({'success': True, 'message': '登出成功'})


@auth_bp.route('/check-username', methods=['GET'])
def check_username():
    username = request.args.get('username')
    if not username:
        return jsonify({'available': False, 'message': '请输入用户名'})

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'available': False, 'message': '用户名已存在'})
    if len(username) < 3:
        return jsonify({'available': False, 'message': '用户名至少3个字符'})
    if len(username) > 20:
        return jsonify({'available': False, 'message': '用户名不能超过20个字符'})

    return jsonify({'available': True, 'message': '用户名可用'})


@auth_bp.route('/check-email', methods=['GET'])
def check_email():
    email = request.args.get('email')
    if not email:
        return jsonify({'available': False, 'message': '请输入邮箱'})
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'available': False, 'message': '邮箱格式不正确'})
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'available': False, 'message': '邮箱已被注册'})
    return jsonify({'available': True, 'message': '邮箱可用'})
