# 农作物病害分类系统 (YOLO Disease Detection System)

这是一个基于 YOLO 目标检测模型的现代农作物病害在线识别平台。

## 系统特性
- **🌿 智能检测**: 基于 YOLO 模型，2秒内快速识别病害（目前支持番茄、玉米、苹果、马铃薯等）。
- **📊 数据看板**: 全平台检测统计，高频病害 Top 5 展示。
- **📖 全科百科**: 详尽的病害成因与防治建议知识库。
- **📜 检测流水线**: 自动保存历史记录，支持溯源分析。
- **💎 玻璃拟态设计**: 极简、现代、 premium 的用户交互界面。

## 项目结构
- `backend/`: 基于 FastAPI 的高性能异步后端。
- `frontend/`: 基于 Vue 3 + Vite 的现代化前端。

## 快速开始

### 1. 后端启动
```bash
cd backend
pip install -r requirements.txt
# 初始化数据库与百科数据
python seed_data.py
# 启动项目
uvicorn app.main:app --reload
```

### 2. 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 注意事项
- 默认检测逻辑为 Mock 模拟，如需接入真实 YOLO 模型，请在 `backend/app/api/detect.py` 中取消相关注释并放置模型权重文件于 `backend/models/` 目录下。
- 免责声明：系统识别结果仅供参考，重大灾情请结合人工鉴定。
