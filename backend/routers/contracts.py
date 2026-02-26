from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, Contract, AIConfig, Project
from schemas import ContractCreate, ContractResponse, AIConfigCreate, AIConfigResponse
from auth import get_current_user
from config import settings
import httpx
import json
import os
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from docx import Document
import PyPDF2

router = APIRouter(prefix="/api/contracts", tags=["合同管理"])

# AI配置管理
@router.post("/ai-config", response_model=AIConfigResponse)
def create_ai_config(
    config: AIConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 停用同类型的其他配置
    db.query(AIConfig).filter(
        AIConfig.provider == config.provider,
        AIConfig.config_type == config.config_type
    ).update({"is_active": False})
    
    db_config = AIConfig(
        provider=config.provider,
        api_key=config.api_key,
        api_url=config.api_url,
        config_type=config.config_type,
        is_active=True
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/ai-config", response_model=list[AIConfigResponse])
def get_ai_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    configs = db.query(AIConfig).all()
    return configs

# 生成合同
@router.post("/generate-pdf")
async def generate_contract_pdf(
    project_id: int,
    area: float,
    location: str,
    ai_provider: str,
    template_file: UploadFile = File(None),
    template_text: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成PDF格式合同
    支持上传Word/PDF模板或使用文本模板
    """
    if not current_user.is_root:
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 获取项目信息
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 处理模板
    template_content = ""
    if template_file:
        # 保存上传的模板文件
        file_ext = os.path.splitext(template_file.filename)[1].lower()
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        temp_path = os.path.join(settings.UPLOAD_DIR, "documents", temp_filename)
        
        with open(temp_path, "wb") as f:
            content = await template_file.read()
            f.write(content)
        
        # 读取模板内容
        if file_ext == ".docx":
            doc = Document(temp_path)
            template_content = "\n".join([para.text for para in doc.paragraphs])
        elif file_ext == ".pdf":
            with open(temp_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    template_content += page.extract_text()
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式，请上传Word或PDF")
    elif template_text:
        template_content = template_text
    else:
        raise HTTPException(status_code=400, detail="请提供模板文件或模板文本")
    
    # 获取AI配置
    ai_config = db.query(AIConfig).filter(
        AIConfig.provider == ai_provider,
        AIConfig.config_type == "llm",
        AIConfig.is_active == True
    ).first()
    
    if not ai_config:
        raise HTTPException(status_code=400, detail=f"未配置{ai_provider}接口")
    
    # 构建提示词
    prompt = f"""
根据以下信息生成建筑设计合同：

项目名称：{project.name}
项目地址：{location}
建筑面积：{area}平方米
项目预算：{project.budget}元

合同模板：
{template_content}

请根据以上信息，生成完整的建筑设计合同内容。
"""
    
    # 调用AI接口
    try:
        content = await call_ai_api(ai_config, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI接口调用失败: {str(e)}")
    
    # 生成PDF
    pdf_filename = f"contract_{project_id}_{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, "documents", pdf_filename)
    
    create_pdf_contract(pdf_path, content, project, area, location)
    
    # 保存合同记录
    db_contract = Contract(
        project_id=project_id,
        template=template_content,
        content=content,
        area=area,
        location=location,
        ai_provider=ai_provider,
        created_by=current_user.id
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    
    return {
        "contract_id": db_contract.id,
        "pdf_url": f"/uploads/documents/{pdf_filename}",
        "content": content
    }

@router.get("/download/{contract_id}")
def download_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载合同PDF"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    # 重新生成PDF（如果需要）
    pdf_filename = f"contract_{contract.project_id}_{contract.id}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, "documents", pdf_filename)
    
    if not os.path.exists(pdf_path):
        project = db.query(Project).filter(Project.id == contract.project_id).first()
        create_pdf_contract(pdf_path, contract.content, project, contract.area, contract.location)
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"合同_{contract.project_id}.pdf"
    )

def create_pdf_contract(pdf_path: str, content: str, project, area: float, location: str):
    """创建PDF合同"""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # 注册中文字体（使用系统字体）
    try:
        # Windows系统字体
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        font_name = 'SimSun'
    except:
        # 如果找不到中文字体，使用默认字体
        font_name = 'Helvetica'
    
    # 定义样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        alignment=1,  # 居中
        spaceAfter=30
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=12,
        leading=20,
        spaceAfter=12
    )
    
    # 添加标题
    story.append(Paragraph("建筑设计合同", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 添加项目信息
    info_text = f"""
    <b>项目名称：</b>{project.name}<br/>
    <b>项目地址：</b>{location}<br/>
    <b>建筑面积：</b>{area}平方米<br/>
    <b>项目预算：</b>{project.budget}元<br/>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 添加合同内容
    for line in content.split('\n'):
        if line.strip():
            story.append(Paragraph(line, body_style))
    
    # 生成PDF
    doc.build(story)

@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    return contract

@router.get("/project/{project_id}", response_model=list[ContractResponse])
def get_project_contracts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).filter(Contract.project_id == project_id).all()
    return contracts

# AI接口调用函数
async def call_ai_api(config: AIConfig, prompt: str) -> str:
    """调用AI接口生成内容"""
    
    if config.provider == "minimax":
        return await call_minimax(config, prompt)
    elif config.provider == "gemini":
        return await call_gemini(config, prompt)
    else:
        raise ValueError(f"不支持的AI提供商: {config.provider}")

async def call_minimax(config: AIConfig, prompt: str) -> str:
    """调用MiniMax API"""
    url = config.api_url or "https://api.minimax.chat/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "abab6.5-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise ValueError("MiniMax API返回格式错误")

async def call_gemini(config: AIConfig, prompt: str) -> str:
    """调用Gemini API"""
    url = config.api_url or f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={config.api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise ValueError("Gemini API返回格式错误")

