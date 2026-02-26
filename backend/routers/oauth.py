from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from database import get_db
from models import User, AIConfig
from auth import create_access_token, get_password_hash
from datetime import timedelta
from config import settings
import secrets

router = APIRouter(prefix="/api/oauth", tags=["OAuth登录"])

# OAuth配置
config = Config('.env')
oauth = OAuth(config)

# 注册OAuth提供商
def register_oauth_providers(db: Session):
    """从数据库读取OAuth配置并注册"""
    providers = db.query(AIConfig).filter(
        AIConfig.config_type == "oauth",
        AIConfig.is_active == True
    ).all()
    
    for provider in providers:
        if provider.provider == "github":
            oauth.register(
                name='github',
                client_id=provider.api_key,
                client_secret=provider.api_url,  # 这里存储client_secret
                access_token_url='https://github.com/login/oauth/access_token',
                authorize_url='https://github.com/login/oauth/authorize',
                api_base_url='https://api.github.com/',
                client_kwargs={'scope': 'user:email'},
            )
        elif provider.provider == "google":
            oauth.register(
                name='google',
                client_id=provider.api_key,
                client_secret=provider.api_url,
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                client_kwargs={'scope': 'openid email profile'},
            )
        elif provider.provider == "wechat":
            oauth.register(
                name='wechat',
                client_id=provider.api_key,  # AppID
                client_secret=provider.api_url,  # AppSecret
                access_token_url='https://api.weixin.qq.com/sns/oauth2/access_token',
                authorize_url='https://open.weixin.qq.com/connect/qrconnect',
                api_base_url='https://api.weixin.qq.com/',
                client_kwargs={'scope': 'snsapi_login'},
            )

@router.get("/login/{provider}")
async def oauth_login(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    发起OAuth登录
    支持的提供商: github, google, wechat
    """
    # 注册OAuth提供商
    register_oauth_providers(db)
    
    if provider not in ['github', 'google', 'wechat']:
        raise HTTPException(status_code=400, detail="不支持的OAuth提供商")
    
    # 检查是否配置了该提供商
    oauth_config = db.query(AIConfig).filter(
        AIConfig.provider == provider,
        AIConfig.config_type == "oauth",
        AIConfig.is_active == True
    ).first()
    
    if not oauth_config:
        raise HTTPException(status_code=400, detail=f"未配置{provider} OAuth")
    
    # 生成回调URL
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    
    # 重定向到OAuth提供商
    return await getattr(oauth, provider).authorize_redirect(request, redirect_uri)

@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """OAuth回调处理"""
    # 注册OAuth提供商
    register_oauth_providers(db)
    
    try:
        # 获取access token
        token = await getattr(oauth, provider).authorize_access_token(request)
        
        # 获取用户信息
        if provider == 'github':
            resp = await getattr(oauth, provider).get('user', token=token)
            user_info = resp.json()
            email = user_info.get('email')
            username = user_info.get('login')
            avatar = user_info.get('avatar_url')
            
        elif provider == 'google':
            user_info = token.get('userinfo')
            email = user_info.get('email')
            username = user_info.get('name')
            avatar = user_info.get('picture')
            
        elif provider == 'wechat':
            resp = await getattr(oauth, provider).get('sns/userinfo', token=token)
            user_info = resp.json()
            email = None  # 微信不提供邮箱
            username = user_info.get('nickname')
            avatar = user_info.get('headimgurl')
        
        # 查找或创建用户
        user = db.query(User).filter(User.email == email).first() if email else None
        
        if not user:
            # 创建新用户
            # 生成唯一用户名
            base_username = username or f"{provider}_user"
            unique_username = base_username
            counter = 1
            while db.query(User).filter(User.username == unique_username).first():
                unique_username = f"{base_username}_{counter}"
                counter += 1
            
            # 生成随机密码
            random_password = secrets.token_urlsafe(16)
            
            user = User(
                username=unique_username,
                email=email or f"{unique_username}@{provider}.oauth",
                password_hash=get_password_hash(random_password),
                avatar=avatar,
                is_approved=True  # OAuth用户自动审批
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 生成JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # 重定向到前端，带上token
        frontend_url = f"http://localhost:8080/#/pages/index/index?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth登录失败: {str(e)}")

@router.post("/config")
def create_oauth_config(
    provider: str,
    client_id: str,
    client_secret: str,
    db: Session = Depends(get_db)
):
    """
    配置OAuth提供商
    provider: github, google, wechat
    client_id: OAuth应用的Client ID
    client_secret: OAuth应用的Client Secret
    """
    # 停用同类型的其他配置
    db.query(AIConfig).filter(
        AIConfig.provider == provider,
        AIConfig.config_type == "oauth"
    ).update({"is_active": False})
    
    config = AIConfig(
        provider=provider,
        config_type="oauth",
        api_key=client_id,
        api_url=client_secret,  # 存储client_secret
        is_active=True
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return {
        "message": f"{provider} OAuth配置已保存",
        "provider": provider
    }

@router.get("/providers")
def get_oauth_providers(db: Session = Depends(get_db)):
    """获取已配置的OAuth提供商列表"""
    providers = db.query(AIConfig).filter(
        AIConfig.config_type == "oauth",
        AIConfig.is_active == True
    ).all()
    
    return [
        {
            "provider": p.provider,
            "name": {
                "github": "GitHub",
                "google": "Google",
                "wechat": "微信"
            }.get(p.provider, p.provider)
        }
        for p in providers
    ]

