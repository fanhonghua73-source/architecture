# -*- coding: utf-8 -*-
"""
测试项目资料管理和Banana API配置
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "root",
            "password": "root123456"
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("[OK] 登录成功")
        return token
    else:
        print(f"[FAIL] 登录失败: {response.text}")
        return None

def add_banana_config(token):
    """添加Banana生图配置"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "provider": "banana",
        "config_type": "image",
        "api_key": "test_banana_api_key_12345",
        "api_url": "https://api.banana.dev/v1/generate"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/contracts/ai-config",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        config = response.json()
        print("[OK] 添加Banana配置成功")
        print(f"  - Provider: {config['provider']}")
        print(f"  - Type: {config['config_type']}")
        print(f"  - Active: {config['is_active']}")
        return config['id']
    else:
        print(f"[FAIL] 添加Banana配置失败: {response.text}")
        return None

def get_ai_configs(token):
    """获取所有AI配置"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/contracts/ai-config",
        headers=headers
    )
    
    if response.status_code == 200:
        configs = response.json()
        print(f"[OK] 获取AI配置成功，共{len(configs)}个")
        for config in configs:
            print(f"  - {config['provider']} ({config['config_type']}): {'启用' if config['is_active'] else '停用'}")
        return configs
    else:
        print(f"[FAIL] 获取AI配置失败: {response.text}")
        return []

def test_project_documents_page():
    """测试项目资料页面是否可访问"""
    print("\n提示：请在浏览器中测试以下功能：")
    print("1. 访问项目详情页")
    print("2. 点击'项目资料'按钮")
    print("3. 应该能看到报价数据和文档管理界面")
    print("4. 在AI配置页面应该能看到Banana生图选项")

def main():
    print("=" * 60)
    print("测试项目资料管理和Banana API配置")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录系统")
    token = login()
    if not token:
        print("\n请先启动后端服务: python main.py")
        return
    
    # 2. 添加Banana配置
    print("\n2. 添加Banana生图配置")
    config_id = add_banana_config(token)
    
    # 3. 获取所有配置
    print("\n3. 获取所有AI配置")
    configs = get_ai_configs(token)
    
    # 4. 检查Banana配置
    print("\n4. 验证Banana配置")
    banana_configs = [c for c in configs if c['provider'] == 'banana']
    if banana_configs:
        print(f"[OK] 找到{len(banana_configs)}个Banana配置")
        for config in banana_configs:
            print(f"  - ID: {config['id']}")
            print(f"  - Type: {config['config_type']}")
            print(f"  - Active: {config['is_active']}")
    else:
        print("[WARN] 未找到Banana配置")
    
    # 5. 前端测试提示
    print("\n5. 前端测试")
    test_project_documents_page()
    
    print("\n" + "=" * 60)
    print("后端测试完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 确保前端服务已启动: npm run dev:h5")
    print("2. 在浏览器中访问项目详情页")
    print("3. 测试项目资料管理功能")
    print("4. 在AI配置页面添加Banana配置")
    print("=" * 60)

if __name__ == "__main__":
    main()

