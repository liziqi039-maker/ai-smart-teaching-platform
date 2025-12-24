"""
工具函数模块
提供 JWT 认证装饰器和其他工具函数
"""

from .decorators import token_required, admin_required, teacher_required, roles_required

__all__ = [
    'token_required',
    'admin_required', 
    'teacher_required',
    'roles_required'
]

# 可选：添加模块说明
__version__ = '1.0.0'
__author__ = 'AI Teaching Platform Team'
__description__ = '工具函数和装饰器模块'
