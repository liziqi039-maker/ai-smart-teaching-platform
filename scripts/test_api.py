"""
测试API端点 - 更新为正确的API路径
"""
import requests
import json

# 使用正确的API前缀
BASE_URL = "http://localhost:8000/api/v1"

def test_endpoints():
    """测试主要API端点"""
    endpoints = [
        ("GET", "/health", None),
        ("GET", "/users", None),
        ("GET", "/quiz/questions", None),
    ]
    
    print("🌐 API端点测试 (v1版本)")
    print("=" * 60)
    print(f"基础URL: {BASE_URL}")
    print("=" * 60)
    
    for method, endpoint, data in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {method} {endpoint}: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   响应: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {method} {endpoint}: 连接失败（后端服务未启动？）")
        except Exception as e:
            print(f"❌ {method} {endpoint}: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # 测试登录
    print("\n🔐 测试登录功能")
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/auth/login", 
                                json=login_data, 
                                timeout=5)
        
        if response.status_code == 200:
            print("✅ 管理员登录成功")
            result = response.json()
            print(f"   消息: {result.get('message')}")
            token = result.get("access_token")
            if token:
                print(f"   获取到Token: {token[:30]}...")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")

def test_root():
    """测试根路径"""
    print("\n🏠 测试根路径")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问成功")
            data = response.json()
            print(f"   平台: {data.get('name')}")
            print(f"   版本: {data.get('version')}")
            print(f"   API端点:")
            for key, value in data.get('endpoints', {}).items():
                print(f"     - {key}: {value}")
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")

if __name__ == '__main__':
    test_root()
    test_endpoints()