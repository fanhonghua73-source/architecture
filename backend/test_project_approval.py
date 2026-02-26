# -*- coding: utf-8 -*-
"""
测试项目审批功能
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

BASE_URL = "http://localhost:8000"

def login(username, password):
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": username,
            "password": password
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"[OK] {username} 登录成功")
        return token
    else:
        print(f"[FAIL] {username} 登录失败: {response.text}")
        return None

def create_project(token, name):
    """创建项目"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "address": "测试地址",
        "area": 1000,
        "budget": 500000,
        "description": "测试项目审批功能"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/projects",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        project = response.json()
        print(f"[OK] 创建项目成功")
        print(f"  - 项目ID: {project['id']}")
        print(f"  - 项目名称: {project['name']}")
        print(f"  - 审批状态: {project['approval_status']}")
        return project['id']
    else:
        print(f"[FAIL] 创建项目失败: {response.text}")
        return None

def get_pending_projects(token):
    """获取待审批项目"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/projects/pending/list",
        headers=headers
    )
    
    if response.status_code == 200:
        projects = response.json()
        print(f"[OK] 获取待审批项目成功，共{len(projects)}个")
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']})")
        return projects
    else:
        print(f"[FAIL] 获取待审批项目失败: {response.text}")
        return []

def approve_project(token, project_id, approved):
    """审批项目"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/approve?approved={str(approved).lower()}",
        headers=headers
    )
    
    action = "批准" if approved else "拒绝"
    if response.status_code == 200:
        print(f"[OK] {action}项目成功")
        return True
    else:
        print(f"[FAIL] {action}项目失败: {response.text}")
        return False

def get_all_projects(token, username):
    """获取项目列表"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/projects",
        headers=headers
    )
    
    if response.status_code == 200:
        projects = response.json()
        print(f"[OK] {username} 可以看到{len(projects)}个项目")
        for project in projects:
            print(f"  - {project['name']} (状态: {project['approval_status']})")
        return projects
    else:
        print(f"[FAIL] 获取项目列表失败: {response.text}")
        return []

def main():
    print("=" * 60)
    print("测试项目审批功能")
    print("=" * 60)
    
    # 1. root用户登录
    print("\n1. Root用户登录")
    root_token = login("root", "root123456")
    if not root_token:
        print("\n请先启动后端服务并创建root用户")
        return
    
    # 2. 创建测试用户（假设已存在已审批用户）
    print("\n2. 普通用户登录并创建项目")
    # 这里假设有一个测试用户，实际使用时需要先创建
    print("  提示：请确保有已审批的测试用户")
    
    # 3. Root用户创建项目（自动批准）
    print("\n3. Root用户创建项目（应自动批准）")
    root_project_id = create_project(root_token, "Root用户的项目")
    
    # 4. 获取待审批项目
    print("\n4. 获取待审批项目列表")
    pending = get_pending_projects(root_token)
    
    # 5. 审批项目
    if pending:
        print("\n5. 审批第一个待审批项目")
        approve_project(root_token, pending[0]['id'], True)
        
        print("\n6. 再次查看待审批项目")
        get_pending_projects(root_token)
    else:
        print("\n5. 没有待审批项目")
    
    # 7. 查看所有项目
    print("\n7. Root用户查看所有项目")
    get_all_projects(root_token, "root")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n功能说明：")
    print("1. Root用户创建的项目自动批准")
    print("2. 普通用户创建的项目需要等待审批")
    print("3. Root用户可以审批项目")
    print("4. 已审批用户可以查看所有已批准的项目（只读）")
    print("5. 只有项目创建者和root用户可以编辑项目")
    print("=" * 60)

if __name__ == "__main__":
    main()

