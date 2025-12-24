# backend/routes/ai_ppt.py
from flask import Blueprint, request, jsonify
from routes.auth import token_required
import requests

ai_ppt_bp = Blueprint('ai_ppt', __name__, url_prefix='/api/ai/ppt')

@ai_ppt_bp.route('/generate', methods=['POST'])
@token_required
def generate_ppt(current_user):
    """调用Node.js AI服务生成PPT"""
    try:
        # 调用Node.js服务的AI路由
        data = request.get_json()
        response = requests.post(
            'http://localhost:3000/ai/generate-ppt',
            json=data,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'PPT生成失败: {str(e)}'
        }), 500