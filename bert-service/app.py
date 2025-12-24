from flask import Flask, request, jsonify
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)

# 加载BERT模型
print("正在加载BERT中文语义模型...")
tokenizer = None
model = None

try:
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    model = BertModel.from_pretrained("bert-base-chinese")
    print("✅ BERT模型加载完成！")
except Exception as e:
    print(f"⚠️ 模型加载失败：{e}")
    print("请确保网络正常，首次加载需要下载模型文件")

def get_text_embedding(text):
    """将文本转为BERT语义向量"""
    if not tokenizer or not model:
        return None
    
    try:
        inputs = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :].numpy()
    except Exception as e:
        print(f"生成文本向量失败: {e}")
        return None

def calculate_similarity(text1, text2):
    """计算两个文本的语义相似度"""
    try:
        emb1 = get_text_embedding(text1)
        emb2 = get_text_embedding(text2)
        
        if emb1 is None or emb2 is None:
            return None
        
        return cosine_similarity(emb1, emb2)[0][0]
    except Exception as e:
        print(f"计算相似度失败: {e}")
        return None

@app.route('/api/similarity', methods=['POST'])
def api_calculate_similarity():
    """计算两个文本的语义相似度API"""
    try:
        data = request.get_json()
        text1 = data.get('text1', '')
        text2 = data.get('text2', '')
        
        if not text1 or not text2:
            return jsonify({
                'success': False,
                'message': '需要两个文本参数'
            }), 400
        
        if not tokenizer or not model:
            return jsonify({
                'success': False,
                'message': 'AI模型未加载'
            }), 503
        
        similarity = calculate_similarity(text1, text2)
        
        if similarity is None:
            return jsonify({
                'success': False,
                'message': '计算失败'
            }), 500
        
        return jsonify({
            'success': True,
            'similarity': float(similarity),
            'score': round(similarity * 100, 2),
            'analysis': get_analysis_by_score(similarity * 100)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'计算失败: {str(e)}'
        }), 500

def get_analysis_by_score(score):
    """根据分数返回分析结果"""
    if score >= 90:
        return "答案非常准确，完全理解了问题核心"
    elif score >= 80:
        return "答案基本正确，涵盖了主要知识点"
    elif score >= 70:
        return "答案部分正确，需要补充细节"
    elif score >= 60:
        return "答案方向正确，但表述不够准确"
    else:
        return "答案需要改进，建议重新学习相关知识点"

@app.route('/api/batch-similarity', methods=['POST'])
def batch_calculate_similarity():
    """批量计算语义相似度"""
    try:
        data = request.get_json()
        student_answers = data.get('student_answers', [])
        reference_answers = data.get('reference_answers', [])
        
        if len(student_answers) != len(reference_answers):
            return jsonify({
                'success': False,
                'message': '学生答案和参考答案数量不匹配'
            }), 400
        
        if not tokenizer or not model:
            return jsonify({
                'success': False,
                'message': 'AI模型未加载'
            }), 503
        
        results = []
        for i in range(len(student_answers)):
            similarity = calculate_similarity(student_answers[i], reference_answers[i])
            if similarity is not None:
                score = round(similarity * 100, 2)
                results.append({
                    'index': i,
                    'similarity': float(similarity),
                    'score': score,
                    'analysis': get_analysis_by_score(score)
                })
            else:
                results.append({
                    'index': i,
                    'similarity': 0,
                    'score': 0,
                    'analysis': '计算失败'
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'average_score': round(sum(r['score'] for r in results) / len(results), 2) if results else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'批量计算失败: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'success': True,
        'service': 'BERT语义分析服务',
        'model_loaded': tokenizer is not None and model is not None,
        'status': 'running'
    })

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'service': 'BERT语义分析服务',
        'version': '1.0.0',
        'endpoints': {
            'similarity': '/api/similarity',
            'batch_similarity': '/api/batch-similarity',
            'health': '/health'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('BERT_SERVICE_PORT', 5001))
    host = os.environ.get('BERT_SERVICE_HOST', '0.0.0.0')
    print(f"🚀 BERT语义服务启动在 http://{host}:{port}")
    app.run(host=host, port=port, debug=True)