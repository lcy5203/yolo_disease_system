import webview
import multiprocessing
import uvicorn
import sys
import os
import time

# 切换工作目录到 backend 根目录，确保相对路径正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def start_backend():
    # 启动 FastAPI 后端服务
    # 使用 8000 端口，关闭日志减少资源占用
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def main():
    # 1. 开启后端子进程
    p = multiprocessing.Process(target=start_backend)
    p.daemon = True
    p.start()

    # 2. 等待后端完全就位
    time.sleep(2) 

    # 3. 启动前端窗口 (PyWebView)
    # 注意：现在指向 Vite 开发服务器 (5173)，即改即现
    window = webview.create_window(
        'Agriculture Disease AI System (YOLO) - [Dev Mode]', 
        'http://localhost:5173',
        width=1200, 
        height=800,
        resizable=True
    )
    
    # 4. 运行窗口并捕获关闭动作
    webview.start()
    
    # 5. 窗口关闭后，强制干掉后端进程
    p.terminate()

if __name__ == '__main__':
    # PyInstaller 打包多进程应用必须加这行
    multiprocessing.freeze_support()
    main()
