"""
测试root用户登录
"""
import requests

# 登录
login_data = {
    "username": "root",
    "password": "root123456"
}

print("正在测试root用户登录...")
print(f"用户名: {login_data['username']}")
print(f"密码: {login_data['password']}")
print("-" * 50)

try:
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print("[OK] 登录成功！")
        print(f"Token: {result['access_token'][:50]}...")
        print(f"Token类型: {result['token_type']}")
        
        # 测试获取用户信息
        print("\n" + "=" * 50)
        print("正在获取用户信息...")
        headers = {
            "Authorization": f"Bearer {result['access_token']}"
        }
        profile_response = requests.get("http://localhost:8000/api/auth/profile", headers=headers)
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print("[OK] 获取用户信息成功！")
            print(f"用户名: {profile['username']}")
            print(f"邮箱: {profile['email']}")
            print(f"是否为Root: {profile.get('is_root', False)}")
            print(f"是否已审批: {profile.get('is_approved', False)}")
        else:
            print(f"[ERROR] 获取用户信息失败: {profile_response.text}")
    else:
        print(f"[ERROR] 登录失败！")
        print(f"状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"[ERROR] 请求失败: {e}")
    print("\n请确保后端服务已启动: python main.py")

