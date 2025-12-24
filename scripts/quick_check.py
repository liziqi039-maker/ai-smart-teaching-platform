"""
快速检查API可用性
"""
import requests

def quick_check():
    """快速检查关键API"""
    print("🔍 AI教学平台快速检查")
    print("=" * 60)
    
    tests = [
        ("根路径", "http://localhost:8000/", "GET"),
        ("健康检查", "http://localhost:8000/api/v1/health", "GET"),
        ("登录页面", "http://localhost:8000/api/v1/auth/login", "POST"),
    ]
    
    for name, url, method in tests:
        try:
            if method == "GET":
                response = requests.get(url, timeout=3)
            elif method == "POST" and "login" in url:
                response = requests.post(url, json={"username": "admin", "password": "admin123"}, timeout=3)
            else:
                response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                print(f"✅ {name}: 正常 (状态码: {response.status_code})")
                if "json" in response.headers.get('Content-Type', ''):
                    data = response.json()
                    if isinstance(data, dict):
                        if data.get('success'):
                            print(f"   消息: {data.get('message')}")
            else:
                print(f"❌ {name}: 失败 (状态码: {response.status_code})")
                if response.text:
                    print(f"   响应: {response.text[:100]}")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: 连接失败 (服务可能未启动)")
        except Exception as e:
            print(f"❌ {name}: 错误 - {str(e)}")

if __name__ == '__main__':
    quick_check()