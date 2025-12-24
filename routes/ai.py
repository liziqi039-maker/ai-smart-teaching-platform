"""
AI服务路由 - 优化使用DeepSeek API
支持智能对话、PPT生成、题目生成等功能
"""
from flask import Blueprint, request, jsonify, current_app
import requests
import json
import os
from datetime import datetime

ai_bp = Blueprint('ai', __name__, url_prefix='/api/v1/ai')

# DeepSeek API配置（OpenAI兼容格式）
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

def call_deepseek_api(messages, model=None, temperature=0.7, max_tokens=2000):
    """
    调用DeepSeek API (OpenAI兼容格式)

    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        model: 模型名称，默认使用配置的模型
        temperature: 温度参数，控制随机性 (0-2)
        max_tokens: 最大生成token数

    Returns:
        dict: API响应结果
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API Key未配置，请在.env文件中设置DEEPSEEK_API_KEY")

    url = f"{DEEPSEEK_API_URL}/chat/completions"
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': model or DEEPSEEK_MODEL,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception("DeepSeek API请求超时")
    except requests.exceptions.RequestException as e:
        raise Exception(f"DeepSeek API请求失败: {str(e)}")

@ai_bp.route('/chat', methods=['POST'])
def ai_chat():
    """
    AI对话聊天 - 使用DeepSeek模型

    请求体:
        {
            "messages": [{"role": "user", "content": "你好"}],
            "model": "deepseek-chat",  # 可选
            "temperature": 0.7,        # 可选
            "max_tokens": 2000         # 可选
        }
    """
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', DEEPSEEK_MODEL)
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)

        if not messages:
            return jsonify({
                'success': False,
                'message': '消息内容不能为空'
            }), 400

        # 调用DeepSeek API
        result = call_deepseek_api(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # 提取响应内容
        if 'choices' in result and len(result['choices']) > 0:
            message_content = result['choices'][0].get('message', {})
            return jsonify({
                'success': True,
                'data': {
                    'message': message_content,
                    'content': message_content.get('content', ''),
                    'usage': result.get('usage', {}),
                    'model': result.get('model', model)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'AI返回结果格式异常'
            }), 500

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"AI Chat错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'AI服务错误: {str(e)}'
        }), 500

@ai_bp.route('/ppt/generate', methods=['POST'])
def ppt_generate():
    """
    生成PPT大纲

    请求体:
        {
            "topic": "人工智能导论",
            "slides": 10,              # 可选，默认8页
            "style": "professional"    # 可选
        }
    """
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        slides = data.get('slides', 8)
        style = data.get('style', 'professional')

        if not topic:
            return jsonify({
                'success': False,
                'message': '主题不能为空'
            }), 400

        # 构建PPT生成提示词
        prompt = f"""请为主题"{topic}"生成一个{slides}页的PPT大纲。

要求：
1. 包含封面、目录、内容页和总结页
2. 每页需要标题和要点内容（3-5个要点）
3. 风格：{style}
4. 内容要专业、清晰、有逻辑性

请以JSON格式输出，格式如下：
{{
  "title": "PPT标题",
  "slides": [
    {{
      "page": 1,
      "title": "页面标题",
      "content": ["要点1", "要点2", "要点3"],
      "notes": "备注说明"
    }}
  ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        result = call_deepseek_api(messages, temperature=0.7, max_tokens=2000)

        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        return jsonify({
            'success': True,
            'data': {
                'topic': topic,
                'outline': content,
                'slides_count': slides,
                'style': style
            }
        })

    except Exception as e:
        current_app.logger.error(f"PPT生成错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'生成PPT失败: {str(e)}'
        }), 500

@ai_bp.route('/quiz/generate', methods=['POST'])
def quiz_generate():
    """
    生成测验题目

    请求体:
        {
            "content": "Python基础知识：变量、数据类型...",
            "type": "multiple_choice",  # 题目类型
            "num": 5,                    # 题目数量
            "difficulty": "medium"       # 可选：难度
        }
    """
    try:
        data = request.get_json()
        content = data.get('content', '')
        question_type = data.get('type', 'multiple_choice')
        num_questions = data.get('num', 5)
        difficulty = data.get('difficulty', 'medium')

        if not content:
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400

        # 题目类型映射
        type_map = {
            'multiple_choice': '单选题',
            'true_false': '判断题',
            'short_answer': '简答题',
            'fill_blank': '填空题'
        }

        type_name = type_map.get(question_type, '单选题')

        # 构建题目生成提示词
        prompt = f"""请基于以下内容生成{num_questions}道{type_name}（难度：{difficulty}）：

内容：{content}

要求：
1. 题目要准确、清晰、有针对性
2. 选项要合理，干扰项要有一定迷惑性
3. 提供正确答案和解析
4. 以JSON格式输出

输出格式：
{{
  "questions": [
    {{
      "id": 1,
      "type": "{question_type}",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "A",
      "explanation": "答案解析"
    }}
  ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        result = call_deepseek_api(messages, temperature=0.5, max_tokens=2000)

        content_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'questions': content_response,
                'type': question_type,
                'difficulty': difficulty
            }
        })

    except Exception as e:
        current_app.logger.error(f"题目生成错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'生成题目失败: {str(e)}'
        }), 500

@ai_bp.route('/analyze', methods=['POST'])
def analyze_content():
    """
    分析内容 - 通用分析接口

    请求体:
        {
            "content": "要分析的内容",
            "analyze_type": "summary|keywords|sentiment",
            "language": "zh"
        }
    """
    try:
        data = request.get_json()
        content = data.get('content', '')
        analyze_type = data.get('analyze_type', 'summary')
        language = data.get('language', 'zh')

        if not content:
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400

        # 分析类型提示词
        prompts = {
            'summary': '请对以下内容进行总结，提取核心要点：',
            'keywords': '请提取以下内容的关键词（5-10个）：',
            'sentiment': '请分析以下内容的情感倾向（正面/负面/中性）：'
        }

        prompt_prefix = prompts.get(analyze_type, prompts['summary'])
        prompt = f"{prompt_prefix}\n\n{content}"

        messages = [{"role": "user", "content": prompt}]
        result = call_deepseek_api(messages, temperature=0.3, max_tokens=1000)

        analysis = result.get('choices', [{}])[0].get('message', {}).get('content', '')

        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis,
                'type': analyze_type,
                'original_length': len(content)
            }
        })

    except Exception as e:
        current_app.logger.error(f"内容分析错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'分析失败: {str(e)}'
        }), 500

@ai_bp.route('/status', methods=['GET'])
def api_status():
    """
    检查AI服务状态
    """
    try:
        # 简单的状态检查
        if not DEEPSEEK_API_KEY:
            return jsonify({
                'success': False,
                'status': 'error',
                'message': 'DeepSeek API Key未配置'
            }), 500

        # 尝试调用API进行健康检查
        messages = [{"role": "user", "content": "你好"}]
        result = call_deepseek_api(messages, max_tokens=10)

        return jsonify({
            'success': True,
            'status': 'healthy',
            'provider': 'DeepSeek',
            'model': DEEPSEEK_MODEL,
            'api_url': DEEPSEEK_API_URL,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 健康检查（向后兼容）
@ai_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'success': True,
        'message': 'AI服务运行正常 (DeepSeek)',
        'provider': 'DeepSeek',
        'timestamp': datetime.now().isoformat()
    })
