"""
DeepSeek AI集成测试脚本
测试AI服务的各个端点是否正常工作
"""
import os
import sys
import requests
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# API配置
BASE_URL = "http://localhost:8000/api/v1/ai"
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

def test_health_check():
    """测试健康检查端点"""
    print("\n" + "="*60)
    print("测试1: 健康检查")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_status_check():
    """测试状态检查端点"""
    print("\n" + "="*60)
    print("测试2: AI服务状态检查")
    print("="*60)

    if not DEEPSEEK_API_KEY:
        print("⚠️ DEEPSEEK_API_KEY未配置，跳过此测试")
        return False

    try:
        response = requests.get(f"{BASE_URL}/status", timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_chat():
    """测试AI对话端点"""
    print("\n" + "="*60)
    print("测试3: AI对话")
    print("="*60)

    if not DEEPSEEK_API_KEY:
        print("⚠️ DEEPSEEK_API_KEY未配置，跳过此测试")
        return False

    data = {
        "messages": [
            {"role": "user", "content": "什么是人工智能？请用一句话简单回答。"}
        ]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        if result.get('success'):
            print(f"✅ 成功!")
            print(f"AI回答: {result['data'].get('content', '')[:200]}...")
        else:
            print(f"❌ 失败: {result.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_ppt_generate():
    """测试PPT生成端点"""
    print("\n" + "="*60)
    print("测试4: PPT大纲生成")
    print("="*60)

    if not DEEPSEEK_API_KEY:
        print("⚠️ DEEPSEEK_API_KEY未配置，跳过此测试")
        return False

    data = {
        "topic": "Python编程基础",
        "slides": 5,
        "style": "educational"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ppt/generate",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        if result.get('success'):
            print(f"✅ 成功!")
            print(f"主题: {result['data'].get('topic')}")
            print(f"大纲预览: {result['data'].get('outline', '')[:200]}...")
        else:
            print(f"❌ 失败: {result.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_quiz_generate():
    """测试题目生成端点"""
    print("\n" + "="*60)
    print("测试5: 测验题目生成")
    print("="*60)

    if not DEEPSEEK_API_KEY:
        print("⚠️ DEEPSEEK_API_KEY未配置，跳过此测试")
        return False

    data = {
        "content": "Python是一种高级编程语言，支持多种编程范式，包括面向对象、命令式、函数式编程。",
        "type": "multiple_choice",
        "num": 3,
        "difficulty": "easy"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/quiz/generate",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        if result.get('success'):
            print(f"✅ 成功!")
            print(f"题目类型: {result['data'].get('type')}")
            print(f"题目预览: {result['data'].get('questions', '')[:200]}...")
        else:
            print(f"❌ 失败: {result.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_analyze():
    """测试内容分析端点"""
    print("\n" + "="*60)
    print("测试6: 内容分析")
    print("="*60)

    if not DEEPSEEK_API_KEY:
        print("⚠️ DEEPSEEK_API_KEY未配置，跳过此测试")
        return False

    data = {
        "content": "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
        "analyze_type": "keywords",
        "language": "zh"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        if result.get('success'):
            print(f"✅ 成功!")
            print(f"分析类型: {result['data'].get('type')}")
            print(f"分析结果: {result['data'].get('analysis', '')[:200]}...")
        else:
            print(f"❌ 失败: {result.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "🚀 "*30)
    print("DeepSeek AI集成测试")
    print("🚀 "*30)

    # 检查配置
    print(f"\n📋 配置检查:")
    print(f"   后端URL: {BASE_URL}")
    print(f"   DeepSeek API Key: {'已配置 ✅' if DEEPSEEK_API_KEY else '未配置 ❌'}")

    if not DEEPSEEK_API_KEY:
        print("\n⚠️  警告: DeepSeek API Key未配置")
        print("   请在.env文件中设置DEEPSEEK_API_KEY")
        print("   部分测试将被跳过\n")

    # 运行测试
    results = []
    results.append(("健康检查", test_health_check()))
    results.append(("状态检查", test_status_check()))
    results.append(("AI对话", test_chat()))
    results.append(("PPT生成", test_ppt_generate()))
    results.append(("题目生成", test_quiz_generate()))
    results.append(("内容分析", test_analyze()))

    # 统计结果
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！DeepSeek AI集成成功！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置和服务状态")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
