# backend/routes/gateway.py
from flask import Blueprint, request, jsonify, redirect
import requests

gateway_bp = Blueprint('gateway', __name__, url_prefix='/api')

# AI服务路由转发
@gateway_bp.route('/ai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def ai_proxy(path):
    """将所有/ai/*请求转发到Node.js AI服务"""
    node_service_url = f'http://localhost:3000/ai/{path}'
    
    try:
        # 获取请求数据
        data = request.get_json() if request.is_json else request.form
        files = request.files
        
        # 转发请求到Node.js服务
        response = requests.request(
            method=request.method,
            url=node_service_url,
            json=data if request.is_json else None,
            data=data if not request.is_json else None,
            files=files,
            headers={key: value for key, value in request.headers 
                    if key != 'Host'},
            stream=True
        )
        
        # 返回响应
        return (
            response.content,
            response.status_code,
            response.headers.items()
        )
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'message': 'AI服务暂时不可用',
            'fallback': True
        }), 503