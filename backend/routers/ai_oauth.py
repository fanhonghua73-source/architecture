from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, AIConfig
from auth import get_current_user
from datetime import datetime, timedelta
import httpx
import secrets

router = APIRouter(prefix="/api/ai-oauth", tags=["AI厂商OAuth授权"])

# AI厂商OAuth配置
AI_PROVIDERS = {
    "minimax": {
        "name": "MiniMax",
        "authorize_url": "https://api.minimax.chat/oauth/authorize",
        "token_url": "https://api.minimax.chat/oauth/token",
        "api_base": "https://api.minimax.chat/v1",
        "scope": "api.read api.write"
    },
    "chatgpt": {
        "name": "ChatGPT",
        "authorize_url": "https://auth.openai.com/authorize",
        "token_url": "https://auth.openai.com/oauth/token",
        "api_base": "https://api.openai.com/v1",
        "scope": "api.read api.write"
    },
    "coze": {
        "name": "小龙虾(Coze)",
        "authorize_url": "https://www.coze.cn/api/permission/oauth2/authorize",
        "token_url": "https://www.coze.cn/api/permission/oauth2/token",
        "api_base": "https://api.coze.cn/v1",
        "scope": "Bot.Chat"
    },
    "gemini": {
        "name": "Gemini",
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "api_base": "https://generativelanguage.googleapis.com/v1",
        "scope": "https://www.googleapis.com/auth/generative-language"
    },
    "banana": {
        "name": "Banana",
        "authorize_url": "https://app.banana.dev/oauth/authorize",
        "token_url": "https://app.banana.dev/oauth/token",
        "api_base": "https://api.banana.dev/v1",
        "scope": "api.generate"
    }
}

@router.get("/authorize/{provider}")
async def authorize_ai_provider(
    provider: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发起AI厂商OAuth授权
    支持: minimax, chatgpt, coze, gemini, banana
    """
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail="不支持的AI提供商")
    
    # 检查是否已配置OAuth应用
    oauth_app = db.query(AIConfig).filter(
        AIConfig.provider == f"{provider}_oauth_app",
        AIConfig.config_type == "oauth_app"
    ).first()
    
    if not oauth_app:
        raise HTTPException(
            status_code=400, 
            detail=f"请先配置{AI_PROVIDERS[provider]['name']}的OAuth应用信息"
        )
    
    client_id = oauth_app.api_key
    redirect_uri = str(request.url_for('ai_oauth_callback', provider=provider))
    state = secrets.token_urlsafe(32)
    
    # 保存state用于验证
    db.query(AIConfig).filter(
        AIConfig.provider == f"{provider}_oauth_state"
    ).delete()
    
    state_record = AIConfig(
        provider=f"{provider}_oauth_state",
        config_type="oauth_state",
        api_key=state,
        token_expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(state_record)
    db.commit()
    
    # 构建授权URL
    provider_config = AI_PROVIDERS[provider]
    auth_url = (
        f"{provider_config['authorize_url']}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={provider_config['scope']}"
        f"&state={state}"
    )
    
    return RedirectResponse(url=auth_url)

@router.get("/callback/{provider}")
async def ai_oauth_callback(
    provider: str,
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """AI厂商OAuth回调处理"""
    
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail="不支持的AI提供商")
    
    # 验证state
    state_record = db.query(AIConfig).filter(
        AIConfig.provider == f"{provider}_oauth_state",
        AIConfig.api_key == state
    ).first()
    
    if not state_record:
        raise HTTPException(status_code=400, detail="无效的state参数")
    
    if state_record.token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="state已过期")
    
    # 获取OAuth应用配置
    oauth_app = db.query(AIConfig).filter(
        AIConfig.provider == f"{provider}_oauth_app",
        AIConfig.config_type == "oauth_app"
    ).first()
    
    if not oauth_app:
        raise HTTPException(status_code=400, detail="OAuth应用配置不存在")
    
    # 交换access token
    try:
        provider_config = AI_PROVIDERS[provider]
        redirect_uri = str(request.url_for('ai_oauth_callback', provider=provider))
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                provider_config['token_url'],
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'client_id': oauth_app.api_key,
                    'client_secret': oauth_app.api_url
                }
            )
            response.raise_for_status()
            token_data = response.json()
        
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)
        
        # 保存或更新配置
        config = db.query(AIConfig).filter(
            AIConfig.provider == provider,
            AIConfig.auth_type == "oauth"
        ).first()
        
        if config:
            config.access_token = access_token
            config.refresh_token = refresh_token
            config.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            config.is_active = True
        else:
            config = AIConfig(
                provider=provider,
                config_type="llm" if provider != "banana" else "image",
                auth_type="oauth",
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
                api_url=provider_config['api_base'],
                is_active=True
            )
            db.add(config)
        
        # 删除state记录
        db.delete(state_record)
        db.commit()
        
        # 重定向到前端配置页面
        frontend_url = "http://localhost:8080/#/pages/admin/ai-oauth-config?success=true"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Token失败: {str(e)}")

@router.post("/refresh/{provider}")
async def refresh_ai_token(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刷新AI厂商的Access Token"""
    
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail="不支持的AI提供商")
    
    # 获取配置
    config = db.query(AIConfig).filter(
        AIConfig.provider == provider,
        AIConfig.auth_type == "oauth"
    ).first()
    
    if not config or not config.refresh_token:
        raise HTTPException(status_code=404, detail="未找到OAuth配置或Refresh Token")
    
    # 获取OAuth应用配置
    oauth_app = db.query(AIConfig).filter(
        AIConfig.provider == f"{provider}_oauth_app"
    ).first()
    
    if not oauth_app:
        raise HTTPException(status_code=400, detail="OAuth应用配置不存在")
    
    try:
        provider_config = AI_PROVIDERS[provider]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                provider_config['token_url'],
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': config.refresh_token,
                    'client_id': oauth_app.api_key,
                    'client_secret': oauth_app.api_url
                }
            )
            response.raise_for_status()
            token_data = response.json()
        
        config.access_token = token_data.get('access_token')
        if token_data.get('refresh_token'):
            config.refresh_token = token_data.get('refresh_token')
        
        expires_in = token_data.get('expires_in', 3600)
        config.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        db.commit()
        
        return {
            "message": "Token刷新成功",
            "expires_at": config.token_expires_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新Token失败: {str(e)}")

@router.delete("/revoke/{provider}")
async def revoke_ai_authorization(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """撤销AI厂商授权"""
    
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    config = db.query(AIConfig).filter(
        AIConfig.provider == provider,
        AIConfig.auth_type == "oauth"
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="未找到OAuth配置")
    
    db.delete(config)
    db.commit()
    
    return {"message": "授权已撤销"}

@router.get("/status")
async def get_ai_oauth_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有AI厂商的OAuth授权状态"""
    
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    status_list = []
    
    for provider_key, provider_info in AI_PROVIDERS.items():
        config = db.query(AIConfig).filter(
            AIConfig.provider == provider_key,
            AIConfig.auth_type == "oauth"
        ).first()
        
        if config:
            is_expired = config.token_expires_at < datetime.utcnow() if config.token_expires_at else True
            status_list.append({
                "provider": provider_key,
                "name": provider_info["name"],
                "authorized": True,
                "expires_at": config.token_expires_at,
                "is_expired": is_expired,
                "has_refresh_token": bool(config.refresh_token)
            })
        else:
            status_list.append({
                "provider": provider_key,
                "name": provider_info["name"],
                "authorized": False,
                "expires_at": None,
                "is_expired": False,
                "has_refresh_token": False
            })
    
    return status_list

@router.post("/config-app/{provider}")
async def config_oauth_app(
    provider: str,
    client_id: str,
    client_secret: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    配置AI厂商的OAuth应用信息
    需要先在AI厂商平台创建OAuth应用，获取Client ID和Secret
    """
    
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    if provider not in AI_PROVIDERS:
        raise HTTPException(status_code=400, detail="不支持的AI提供商")
    
    # 删除旧配置
    db.query(AIConfig).filter(
        AIConfig.provider == f"{provider}_oauth_app"
    ).delete()
    
    # 创建新配置
    oauth_app = AIConfig(
        provider=f"{provider}_oauth_app",
        config_type="oauth_app",
        api_key=client_id,
        api_url=client_secret,
        is_active=True
    )
    db.add(oauth_app)
    db.commit()
    
    return {
        "message": f"{AI_PROVIDERS[provider]['name']} OAuth应用配置成功",
        "provider": provider
    }

