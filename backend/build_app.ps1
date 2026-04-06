# [Step 1] Initialize 
Write-Host "[INFO] Cleaning up previous builds..." -ForegroundColor Cyan
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# [Step 2] Build command
Write-Host "[INFO] Bundling the Agriculture AI Desktop App... " -ForegroundColor Cyan
Write-Host "[INFO] This may take a moment. We are bundling YOLOv8 and your custom models." -ForegroundColor Cyan

& "c:\Users\16013\Desktop\yolo\.venv_39\Scripts\pyinstaller.exe" --noconfirm --onedir --noconsole --name "YOLO_Disease_System" `
    --add-data "app;app" `
    --add-data "frontend_dist;frontend_dist" `
    --add-data "models;models" `
    --add-data "static;static" `
    --hidden-import "ultralytics" `
    --hidden-import "cv2" `
    --hidden-import "PIL" `
    --hidden-import "passlib.handlers.bcrypt" `
    --collect-all "ultralytics" `
    desktop_main.py

# [Step 3] Post-build success
Write-Host "============================" -ForegroundColor Green
Write-Host "Build Successful!" -ForegroundColor Green
Write-Host "Your customized AI model is now integrated." -ForegroundColor Green
Write-Host "The application is at: backend/dist/YOLO_Disease_System" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
pause
