import shutil

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, ai_chat, auth, detect, encyclopedia, history, stats
from app.core.paths import bundle_root, resource_path, runtime_root
from app.db.base import Base
from app.db.seed import seed_defaults
from app.db.session import SessionLocal, engine


def get_resource_path(relative_path: str) -> str:
    return str(resource_path(relative_path))


def prepare_runtime_static() -> None:
    bundled_static = bundle_root() / "static"
    runtime_static = runtime_root() / "static"
    runtime_static.mkdir(parents=True, exist_ok=True)
    if bundled_static.exists():
        shutil.copytree(bundled_static, runtime_static, dirs_exist_ok=True)
    (runtime_static / "uploads").mkdir(parents=True, exist_ok=True)


prepare_runtime_static()
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_defaults(db)
finally:
    db.close()

app = FastAPI(
    title="农作物病害分类系统",
    description="基于 YOLO 的农作物健康管理平台",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(runtime_root() / "static")), name="static")

app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理后台"])
app.include_router(detect.router, prefix="/api/detect", tags=["病害检测"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["AI 专家对话"])
app.include_router(history.router, prefix="/api/history", tags=["检测流水线"])
app.include_router(encyclopedia.router, prefix="/api/encyclopedia", tags=["百科查询"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计分析"])

frontend_path = get_resource_path("frontend_dist")
assets_path = resource_path("frontend_dist/assets")
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith(("api/", "static/", "assets/")):
        raise HTTPException(status_code=404, detail="Not found")

    index_file = resource_path("frontend_dist/index.html")
    if index_file.exists():
        return FileResponse(str(index_file))

    return {"message": "农作物病害分类系统后端 API 正常运行，前端尚未构建"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
