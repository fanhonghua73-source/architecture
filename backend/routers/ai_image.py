from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User, AIConfig, AIImageGeneration
from schemas import AIImageGenerationCreate, AIImageGenerationResponse
from auth import get_current_user
from config import settings
import httpx
import json
import os
import uuid
import base64

router = APIRouter(prefix="/api/ai-image", tags=["AI生图"])

@router.post("/generate", response_model=AIImageGenerationResponse)
async def generate_image(
    base_image: UploadFile = File(...),
    reference_image1: UploadFile = File(None),
    reference_image2: UploadFile = File(None),
    reference_image3: UploadFile = File(None),
    prompt: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI生图功能
    - base_image: 必需的基础图片
    - reference_image1-3: 可选的参考图片
    - prompt: 提示词
    """
    
    # 获取Banana配置
    banana_config = db.query(AIConfig).filter(
        AIConfig.provider == "banana",
        AIConfig.config_type == "image",
        AIConfig.is_active == True
    ).first()
    
    if not banana_config:
        raise HTTPException(status_code=400, detail="未配置Banana生图接口")
    
    # 保存基础图片
    base_ext = os.path.splitext(base_image.filename)[1]
    base_filename = f"{uuid.uuid4()}{base_ext}"
    base_path = os.path.join(settings.UPLOAD_DIR, "images", base_filename)
    
    with open(base_path, "wb") as f:
        content = await base_image.read()
        f.write(content)
    
    base_image_url = f"/uploads/images/{base_filename}"
    
    # 保存参考图片
    reference_images = []
    for ref_img in [reference_image1, reference_image2, reference_image3]:
        if ref_img:
            ref_ext = os.path.splitext(ref_img.filename)[1]
            ref_filename = f"{uuid.uuid4()}{ref_ext}"
            ref_path = os.path.join(settings.UPLOAD_DIR, "images", ref_filename)
            
            with open(ref_path, "wb") as f:
                content = await ref_img.read()
                f.write(content)
            
            reference_images.append(f"/uploads/images/{ref_filename}")
    
    # 如果有参考图片但没有提示词，使用LLM生成提示词
    if reference_images and not prompt:
        prompt = await generate_prompt_from_images(reference_images, db)
    
    # 调用Banana API生成图片
    try:
        result_url = await call_banana_api(banana_config, base_path, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生图失败: {str(e)}")
    
    # 保存记录
    generation = AIImageGeneration(
        user_id=current_user.id,
        base_image_url=base_image_url,
        reference_images=json.dumps(reference_images),
        prompt=prompt,
        result_image_url=result_url,
        provider="banana"
    )
    
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    return generation

@router.post("/regenerate/{generation_id}", response_model=AIImageGenerationResponse)
async def regenerate_image(
    generation_id: int,
    new_prompt: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    基于之前的生成结果进行二次对话生成
    """
    
    # 获取原始生成记录
    original = db.query(AIImageGeneration).filter(
        AIImageGeneration.id == generation_id,
        AIImageGeneration.user_id == current_user.id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="生成记录不存在")
    
    # 获取Banana配置
    banana_config = db.query(AIConfig).filter(
        AIConfig.provider == "banana",
        AIConfig.config_type == "image",
        AIConfig.is_active == True
    ).first()
    
    if not banana_config:
        raise HTTPException(status_code=400, detail="未配置Banana生图接口")
    
    # 使用原始基础图片和新提示词生成
    base_path = os.path.join(settings.UPLOAD_DIR.replace("/uploads", ""), original.base_image_url.replace("/uploads/", ""))
    
    try:
        result_url = await call_banana_api(banana_config, base_path, new_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生图失败: {str(e)}")
    
    # 创建新记录
    generation = AIImageGeneration(
        user_id=current_user.id,
        base_image_url=original.base_image_url,
        reference_images=original.reference_images,
        prompt=new_prompt,
        result_image_url=result_url,
        provider="banana"
    )
    
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    return generation

@router.get("/history", response_model=list[AIImageGenerationResponse])
def get_generation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取生图历史"""
    generations = db.query(AIImageGeneration).filter(
        AIImageGeneration.user_id == current_user.id
    ).order_by(AIImageGeneration.created_at.desc()).limit(50).all()
    
    return generations

async def generate_prompt_from_images(image_urls: list, db: Session) -> str:
    """使用LLM从参考图片生成提示词"""
    
    # 获取LLM配置
    llm_config = db.query(AIConfig).filter(
        AIConfig.config_type == "llm",
        AIConfig.is_active == True
    ).first()
    
    if not llm_config:
        return "根据参考图片生成建筑设计"
    
    prompt = f"""
请分析这些建筑设计参考图片，提取出关键的设计风格、元素和特征，
生成一个详细的设计提示词，用于指导AI生成类似风格的建筑设计图。

参考图片数量: {len(image_urls)}

请用简洁的语言描述设计风格、色彩、材质、结构特点等。
"""
    
    # 这里简化处理，实际应该调用LLM API
    return "现代简约风格建筑设计，玻璃幕墙，简洁线条"

async def call_banana_api(config: AIConfig, image_path: str, prompt: str) -> str:
    """调用Banana API生成图片"""
    
    # Banana API的正确URL格式
    api_key = config.api_key  # 这是API Key
    model_key = config.api_url  # 这里存储的是Model Key
    
    if not api_key or not model_key:
        raise ValueError("请配置Banana API Key和Model Key")
    
    url = "https://api.banana.dev/start/v4"
    
    # 读取图片并转换为base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Banana API的正确请求格式
    data = {
        "apiKey": api_key,
        "modelKey": model_key,
        "modelInputs": {
            "prompt": prompt or "architectural design, modern style",
            "image": image_data,
            "num_inference_steps": 50,
            "guidance_scale": 7.5
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Banana API返回格式: {"id": "...", "message": "success", "created": ..., "apiVersion": "...", "modelOutputs": [{"image_base64": "..."}]}
            if result.get("message") == "success" and "modelOutputs" in result:
                model_outputs = result["modelOutputs"]
                
                # 获取生成的图片
                if isinstance(model_outputs, list) and len(model_outputs) > 0:
                    output = model_outputs[0]
                    
                    # 尝试不同的字段名
                    image_base64 = output.get("image_base64") or output.get("image") or output.get("output")
                    
                    if image_base64:
                        # 移除可能的data URL前缀
                        if "," in image_base64:
                            image_base64 = image_base64.split(",")[1]
                        
                        result_image_data = base64.b64decode(image_base64)
                        result_filename = f"{uuid.uuid4()}.png"
                        result_path = os.path.join(settings.UPLOAD_DIR, "images", result_filename)
                        
                        with open(result_path, "wb") as f:
                            f.write(result_image_data)
                        
                        return f"/uploads/images/{result_filename}"
                
                raise ValueError(f"Banana API返回数据中没有图片: {model_outputs}")
            else:
                error_msg = result.get("message", "未知错误")
                raise ValueError(f"Banana API调用失败: {error_msg}")
                
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Banana API请求失败: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise ValueError(f"调用Banana API时出错: {str(e)}")

