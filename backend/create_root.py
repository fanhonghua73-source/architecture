"""
创建默认root用户的脚本
运行此脚本将创建一个默认的root管理员账户
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
from auth import get_password_hash

def create_root_user():
    # 删除所有表并重新创建
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 不需要检查，直接创建
        # existing_root = db.query(User).filter(User.username == "root").first()
        # if existing_root:
        #     print("Root用户已存在")
        #     return
        
        # 创建root用户
        root_user = User(
            username="root",
            email="root@architect.com",
            password_hash=get_password_hash("root123456"),  # 默认密码
            is_root=True,
            is_approved=True,
            company="系统管理",
            position="超级管理员"
        )
        
        db.add(root_user)
        db.commit()
        db.refresh(root_user)
        
        print("=" * 50)
        print("Root用户创建成功！")
        print("=" * 50)
        print(f"用户名: root")
        print(f"密码: root123456")
        print(f"邮箱: root@architect.com")
        print("=" * 50)
        print("请尽快登录并修改默认密码！")
        print("=" * 50)
        
    except Exception as e:
        print(f"创建root用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_root_user()

