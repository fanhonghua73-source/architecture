from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from database import engine, Base
from config import settings
from routers import auth, projects, inspirations, tasks, materials, contracts, permissions, inspiration_import, project_import, ai_image, oauth, ai_oauth, project_documents, documents

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/images", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/documents", exist_ok=True)

app = FastAPI(
    title="建筑师助手API",
    description="建筑师助手应用后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 静态文件服务
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(inspirations.router)
app.include_router(tasks.router)
app.include_router(materials.router)
app.include_router(materials.supplier_router)
app.include_router(contracts.router)
app.include_router(permissions.router)
app.include_router(inspiration_import.router)
app.include_router(project_import.router)
app.include_router(ai_image.router)
app.include_router(oauth.router)
app.include_router(ai_oauth.router)
app.include_router(project_documents.router)
app.include_router(documents.router)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误: {str(exc)}"}
    )

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用建筑师助手API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

