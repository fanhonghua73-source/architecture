# -*- coding: utf-8 -*-
"""
测试项目资料和报价功能
"""
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
        print("[FAIL] 登录失败")
        return None

def create_test_project(token):
    """创建测试项目"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "测试项目-资料管理",
        "address": "北京市朝阳区建国路88号",
        "area": 50000,
        "budget": 10000000,
        "description": "用于测试项目资料和报价功能"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/projects",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        project = response.json()
        print(f"[OK] 创建项目成功，ID: {project['id']}")
        return project['id']
    else:
        print(f"[FAIL] 创建项目失败: {response.text}")
        return None

def update_quotation(token, project_id):
    """更新报价数据"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "total_building_area": 50000,
        "above_ground_area": 40000,
        "underground_area": 10000,
        "residential_units": 200,
        "commercial_units": 50,
        "supporting_area": 5000,
        "basement_estimated_area": 10000,
        "parking_area": 8000
    }
    
    response = requests.put(
        f"{BASE_URL}/api/projects/{project_id}/quotation",
        headers=headers,
        params=data
    )
    
    if response.status_code == 200:
        print("[OK] 更新报价数据成功")
        print(f"  - 总建筑面积: {data['total_building_area']}平方米")
        print(f"  - 地上面积: {data['above_ground_area']}平方米")
        print(f"  - 地下面积: {data['underground_area']}平方米")
        print(f"  - 住宅户数: {data['residential_units']}户")
        print(f"  - 商业户数: {data['commercial_units']}户")
        return True
    else:
        print(f"[FAIL] 更新报价数据失败: {response.text}")
        return False

def set_location(token, project_id):
    """设置项目位置"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "longitude": 116.404,
        "latitude": 39.915,
        "address": "北京市朝阳区建国路88号"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/location",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print("[OK] 设置项目位置成功")
        print(f"  - 地址: {data['address']}")
        print(f"  - 经度: {data['longitude']}")
        print(f"  - 纬度: {data['latitude']}")
        return True
    else:
        print(f"[FAIL] 设置项目位置失败: {response.text}")
        return False

def get_project_detail(token, project_id):
    """获取项目详情"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/projects/{project_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        project = response.json()
        print("[OK] 获取项目详情成功")
        print(f"  - 项目名称: {project['name']}")
        print(f"  - 总建筑面积: {project.get('total_building_area', '未设置')}")
        print(f"  - 住宅户数: {project.get('residential_units', '未设置')}")
        
        if project.get('baidu_location'):
            location = json.loads(project['baidu_location'])
            print(f"  - 位置: {location['address']}")
        
        return True
    else:
        print(f"[FAIL] 获取项目详情失败: {response.text}")
        return False

def main():
    print("=" * 60)
    print("测试项目资料和报价功能")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录系统")
    token = login()
    if not token:
        return
    
    # 2. 创建测试项目
    print("\n2. 创建测试项目")
    project_id = create_test_project(token)
    if not project_id:
        return
    
    # 3. 更新报价数据
    print("\n3. 更新报价数据")
    update_quotation(token, project_id)
    
    # 4. 设置项目位置
    print("\n4. 设置项目位置")
    set_location(token, project_id)
    
    # 5. 获取项目详情
    print("\n5. 获取项目详情（验证数据）")
    get_project_detail(token, project_id)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示：")
    print("- 文档上传功能需要在前端测试")
    print("- PDF转CAD功能需要上传PDF文件后测试")
    print(f"- 项目ID: {project_id}")
    print("=" * 60)

if __name__ == "__main__":
    main()

