# backend/routes/quiz.py
from flask import Blueprint, request, jsonify
from routes.auth import token_required
from models import db, Quiz, QuizSubmission, QuizStatistics
import requests
import json
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__, url_prefix='/api/v1/quiz')

# ==================== API路由 ====================

@quiz_bp.route('/questions', methods=['GET'])
@token_required
def get_questions(current_user):
    """获取题库列表（从数据库）"""
    try:
        question_type = request.args.get('type', 'all')
        
        if question_type == 'objective':
            questions = Quiz.query.filter_by(type='objective').all()
        elif question_type == 'subjective':
            questions = Quiz.query.filter_by(type='subjective').all()
        else:
            questions = Quiz.query.all()
        
        return jsonify({
            'success': True,
            'data': {
                'objective': [q.to_dict() for q in questions if q.type == 'objective'],
                'subjective': [q.to_dict() for q in questions if q.type == 'subjective']
            }
        }), 200
    except Exception as e:
        print(f"获取题库失败，使用静态数据: {e}")
        return jsonify({
            'success': True,  # 注意这里保持success为True，因为静态数据也是有效的
            'message': f'从数据库获取题库失败，已返回静态数据: {str(e)}',
            'data': get_static_question_bank()
        }), 200

@quiz_bp.route('/submit', methods=['POST'])
@token_required
def submit_quiz(current_user):
    """提交答题"""
    try:
        data = request.get_json()
        
        if not data or not data.get('answers'):
            return jsonify({
                'success': False,
                'message': '答题数据不能为空'
            }), 400
        
        objective_answers = data.get('answers', {}).get('objective', {})
        subjective_answers = data.get('answers', {}).get('subjective', {})
        
        results = {
            'objective': {},
            'subjective': {},
            'summary': {
                'total_score': 0,
                'objective_score': 0,
                'subjective_score': 0,
                'correct_count': 0,
                'total_count': len(objective_answers) + len(subjective_answers)
            }
        }
        
        # 批改客观题
        for q_id, answer in objective_answers.items():
            try:
                # 先尝试从数据库获取题目
                try:
                    question = Quiz.query.get(int(q_id))
                except Exception as db_error:
                    print(f"数据库查询题目 {q_id} 失败: {db_error}")
                    question = None
                
                if question and question.type == 'objective':
                    is_correct = (str(answer).upper() == question.answer)
                    results['objective'][q_id] = {
                        'user_answer': answer,
                        'correct_answer': question.answer,
                        'is_correct': is_correct,
                        'explanation': question.explanation,
                        'score': 10 if is_correct else 0
                    }
                    
                    if is_correct:
                        results['summary']['objective_score'] += 10
                        results['summary']['correct_count'] += 1
                else:
                    # 如果数据库中没有题目，使用静态数据
                    static_questions = get_static_objective_questions()
                    for static_q in static_questions:
                        if str(static_q['id']) == str(q_id):
                            is_correct = (str(answer).upper() == static_q['answer'])
                            results['objective'][q_id] = {
                                'user_answer': answer,
                                'correct_answer': static_q['answer'],
                                'is_correct': is_correct,
                                'explanation': static_q['explanation'],
                                'score': 10 if is_correct else 0
                            }
                            
                            if is_correct:
                                results['summary']['objective_score'] += 10
                                results['summary']['correct_count'] += 1
                            break
            except Exception as e:
                print(f"批改客观题 {q_id} 失败: {e}")
        
        # 批改主观题
        for q_id, answer in subjective_answers.items():
            try:
                # 先尝试从数据库获取题目
                try:
                    question = Quiz.query.get(int(q_id))
                except Exception as db_error:
                    print(f"数据库查询主观题 {q_id} 失败: {db_error}")
                    question = None
                
                if question and question.type == 'subjective':
                    # 调用BERT服务计算相似度
                    try:
                        bert_response = requests.post(
                            'http://localhost:5001/api/similarity',
                            json={
                                'text1': answer,
                                'text2': question.reference_answer
                            },
                            timeout=10
                        )
                        
                        if bert_response.status_code == 200:
                            bert_data = bert_response.json()
                            similarity = bert_data.get('similarity', 0)
                            score = round(similarity * 10, 2)
                            feedback = bert_data.get('analysis', '')
                        else:
                            # 如果BERT服务响应错误，使用简单评分
                            raise Exception("BERT服务响应错误")
                    except Exception as bert_error:
                        print(f"BERT服务不可用，使用简单评分: {bert_error}")
                        # 如果BERT服务不可用，使用简单评分
                        keywords = question.reference_answer.split()[:5]
                        match_count = sum(1 for keyword in keywords if keyword in answer)
                        score = min(10, match_count * 2)
                        similarity = score / 10
                        feedback = f'关键词匹配 {match_count}/{len(keywords)}'
                    
                    results['subjective'][q_id] = {
                        'user_answer': answer,
                        'reference_answer': question.reference_answer,
                        'similarity': similarity,
                        'score': score,
                        'explanation': question.explanation,
                        'feedback': feedback
                    }
                    
                    results['summary']['subjective_score'] += score
                else:
                    # 如果数据库中没有题目，使用静态数据
                    static_questions = get_static_subjective_questions()
                    for static_q in static_questions:
                        if str(static_q['id']) == str(q_id):
                            # 简单的关键词匹配评分
                            keywords = static_q['reference_answer'].split()[:5]
                            match_count = sum(1 for keyword in keywords if keyword in answer)
                            score = min(10, match_count * 2)
                            similarity = score / 10
                            feedback = f'关键词匹配 {match_count}/{len(keywords)}'
                            
                            results['subjective'][q_id] = {
                                'user_answer': answer,
                                'reference_answer': static_q['reference_answer'],
                                'similarity': similarity,
                                'score': score,
                                'explanation': static_q['explanation'],
                                'feedback': feedback
                            }
                            
                            results['summary']['subjective_score'] += score
                            break
            except Exception as e:
                print(f"批改主观题 {q_id} 失败: {e}")
        
        # 计算总分
        results['summary']['total_score'] = results['summary']['objective_score'] + results['summary']['subjective_score']
        
        # 尝试保存提交记录到数据库
        try:
            submission = QuizSubmission(
                user_id=current_user.id,
                quiz_type='static',
                answers=json.dumps(data.get('answers', {})),
                score=results['summary']['total_score'],
                ai_feedback='自动批改完成',
                similarity_score=results['summary']['subjective_score'] / len(subjective_answers) if subjective_answers else 0,
                total_questions=results['summary']['total_count'],
                correct_questions=results['summary']['correct_count'],
                duration=data.get('duration', 0),
                detailed_results=json.dumps(results),
                graded_at=datetime.utcnow()
            )
            db.session.add(submission)
            
            # 尝试更新用户统计
            try:
                stats = QuizStatistics.query.filter_by(user_id=current_user.id, quiz_type='static').first()
                if stats:
                    stats.total_quizzes += 1
                    stats.average_score = (stats.average_score * (stats.total_quizzes - 1) + results['summary']['total_score']) / stats.total_quizzes
                    stats.best_score = max(stats.best_score, results['summary']['total_score'])
                    stats.worst_score = min(stats.worst_score, results['summary']['total_score']) if stats.total_quizzes > 1 else results['summary']['total_score']
                    stats.total_correct += results['summary']['correct_count']
                    stats.total_questions += results['summary']['total_count']
                else:
                    # 如果不存在统计记录，创建新的
                    stats = QuizStatistics(
                        user_id=current_user.id,
                        quiz_type='static',
                        total_quizzes=1,
                        average_score=results['summary']['total_score'],
                        best_score=results['summary']['total_score'],
                        worst_score=results['summary']['total_score'],
                        total_correct=results['summary']['correct_count'],
                        total_questions=results['summary']['total_count']
                    )
                    db.session.add(stats)
                
                db.session.commit()
                
                submission_id = submission.id
            except Exception as db_error:
                print(f"保存统计信息失败: {db_error}")
                db.session.rollback()
                submission_id = None
        except Exception as db_error:
            print(f"保存提交记录失败: {db_error}")
            db.session.rollback()
            submission_id = None
        
        return jsonify({
            'success': True,
            'data': results,
            'submission_id': submission_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"提交答题异常: {e}")
        return jsonify({
            'success': False,
            'message': f'提交答题失败: {str(e)}'
        }), 500

# ==================== 辅助函数（静态数据备用） ====================

def get_static_question_bank():
    """获取静态题库数据"""
    return {
        "objective": get_static_objective_questions(),
        "subjective": get_static_subjective_questions()
    }

def get_static_objective_questions():
    """获取静态客观题数据"""
    return [
        {
            "id": 1,
            "anchor": "obj1",
            "question": "Python定义函数的关键字是？",
            "options": [
                {"label": "A", "text": "def"},
                {"label": "B", "text": "function"},
                {"label": "C", "text": "func"},
                {"label": "D", "text": "define"}
            ],
            "answer": "A",
            "knowledge_point": "Python基础语法",
            "explanation": "Python中使用def（definition的缩写）关键字定义函数，function/func/define均不是Python的内置关键字。"
        },
        {
            "id": 2,
            "anchor": "obj2",
            "question": "以下哪个不是Python的数据类型？",
            "options": [
                {"label": "A", "text": "list"},
                {"label": "B", "text": "dict"},
                {"label": "C", "text": "array"},
                {"label": "D", "text": "tuple"}
            ],
            "answer": "C",
            "knowledge_point": "Python数据类型",
            "explanation": "Python内置数据类型包括list、dict、tuple等，但没有array类型，array属于numpy库。"
        },
        {
            "id": 3,
            "anchor": "obj3",
            "question": "Python中用于读取文件内容的方法是？",
            "options": [
                {"label": "A", "text": "open()"},
                {"label": "B", "text": "read()"},
                {"label": "C", "text": "write()"},
                {"label": "D", "text": "close()"}
            ],
            "answer": "B",
            "knowledge_point": "Python文件操作",
            "explanation": "open()用于打开文件，read()用于读取文件内容，write()用于写入，close()用于关闭文件。"
        },
        {
            "id": 4,
            "anchor": "obj4",
            "question": "Python中哪个关键字用于异常处理？",
            "options": [
                {"label": "A", "text": "try"},
                {"label": "B", "text": "catch"},
                {"label": "C", "text": "exception"},
                {"label": "D", "text": "error"}
            ],
            "answer": "A",
            "knowledge_point": "Python异常处理",
            "explanation": "Python使用try-except-finally结构处理异常，catch是其他语言的关键字。"
        },
        {
            "id": 5,
            "anchor": "obj5",
            "question": "Python中如何创建空列表？",
            "options": [
                {"label": "A", "text": "[]"},
                {"label": "B", "text": "list()"},
                {"label": "C", "text": "{}"},
                {"label": "D", "text": "()"}
            ],
            "answer": "A",
            "knowledge_point": "Python列表",
            "explanation": "[]是创建空列表的最简方式，list()也可以创建空列表，但[]更常用。"
        }
    ]

def get_static_subjective_questions():
    """获取静态主观题数据"""
    return [
        {
            "id": 101,
            "anchor": "sub1",
            "question": "简述Python列表与元组的区别",
            "reference_answer": "列表是可变序列（可增删改元素），用[]表示；元组是不可变序列，用()表示。列表适合存储需要修改的数据，元组适合存储固定不变的数据。",
            "knowledge_point": "Python序列类型",
            "explanation": "1. 可变性：列表可变（mutable），元组不可变（immutable）；2. 语法：列表用[]，元组用()；3. 性能：元组因不可变，遍历/访问速度略快；4. 用途：列表适合动态修改数据，元组适合存储固定不变的数据（如配置项）。"
        },
        {
            "id": 102,
            "anchor": "sub2",
            "question": "解释Python中的装饰器是什么",
            "reference_answer": "装饰器是一种函数，用于修改其他函数的行为，在不改变原函数代码的情况下增加功能。它接收函数作为参数并返回新函数。",
            "knowledge_point": "Python高级特性",
            "explanation": "装饰器是Python的高级特性，本质是接收函数作为参数并返回新函数的函数。常用于日志记录、性能测试、事务处理、缓存等场景。"
        },
        {
            "id": 103,
            "anchor": "sub3",
            "question": "什么是Python的生成器？",
            "reference_answer": "生成器是一种特殊的迭代器，使用yield关键字返回值，可以按需生成值而不是一次性生成所有值，节省内存。",
            "knowledge_point": "Python迭代器和生成器",
            "explanation": "生成器使用yield语句，每次产生一个值后暂停执行，下次从暂停处继续。与普通函数不同，生成器函数返回一个生成器对象，而不是一次性返回所有结果。"
        }
    ]