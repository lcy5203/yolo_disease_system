from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import sys

# 处理 PyInstaller 打包后的文件路径
def get_resource_path(relative_path):
    # 获取 main.py 所在的后端根目录
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

from app.api import auth, detect, history, encyclopedia, stats, admin, ai_chat
from app.db.session import engine
from app.db.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="农作物病害分类系统", description="基于 YOLO 的长效农作物健康管理平台")

# Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Static files for uploads (images, result images)
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理后台"])
app.include_router(detect.router, prefix="/api/detect", tags=["病害检测"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["AI 专家对话"])
app.include_router(history.router, prefix="/api/history", tags=["检测流水线"])
app.include_router(encyclopedia.router, prefix="/api/encyclopedia", tags=["百科查询"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计分析"])

# 3. Mount Frontend static files (assets)
frontend_path = get_resource_path("frontend_dist")
if os.path.exists(frontend_path):
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# 4. Serve Frontend entry point (index.html)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # If the path looks like an API call or static file (handled above), ignore it.
    if full_path.startswith("api/") or full_path.startswith("static/") or full_path.startswith("assets/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Return index.html for everything else to support Vue/React Router
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    
    return {"message": "农作物病害分类系统后端 API 正常运行中 (前端尚未构建)"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
