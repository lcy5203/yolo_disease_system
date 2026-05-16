# [Step 0] Always run from this script's directory
Set-Location $PSScriptRoot
$frontendDir = Resolve-Path (Join-Path $PSScriptRoot "..\frontend")
$frontendDistSource = Join-Path $frontendDir "dist"
$frontendDistTarget = Join-Path $PSScriptRoot "frontend_dist"

# [Step 1] Initialize 
Write-Host "[INFO] Cleaning up previous builds..." -ForegroundColor Cyan
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# [Step 2] Build frontend for production
Write-Host "[INFO] Building frontend assets..." -ForegroundColor Cyan
Push-Location $frontendDir
& npm.cmd run build
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "============================" -ForegroundColor Red
    Write-Host "Build Failed! Frontend build exited with code $LASTEXITCODE." -ForegroundColor Red
    Write-Host "============================" -ForegroundColor Red
    pause
    exit $LASTEXITCODE
}
Pop-Location

Write-Host "[INFO] Syncing frontend dist to backend/frontend_dist..." -ForegroundColor Cyan
if (Test-Path $frontendDistTarget) { Remove-Item -Recurse -Force $frontendDistTarget }
New-Item -ItemType Directory -Force -Path $frontendDistTarget | Out-Null
Copy-Item -Recurse -Force (Join-Path $frontendDistSource "*") $frontendDistTarget

# [Step 3] Build command
Write-Host "[INFO] Bundling the Agriculture AI Desktop App... " -ForegroundColor Cyan
Write-Host "[INFO] This may take a moment. We are bundling YOLO and your custom models." -ForegroundColor Cyan

& "c:\Users\16013\Desktop\yolo\.venv_39\Scripts\pyinstaller.exe" --noconfirm --onedir --noconsole --name "YOLO_Disease_System" `
    --add-data "app;app" `
    --add-data "frontend_dist;frontend_dist" `
    --add-data "models;models" `
    --add-data "static;static" `
    --hidden-import "ultralytics" `
    --hidden-import "cv2" `
    --hidden-import "PIL" `
    --hidden-import "passlib.handlers.pbkdf2" `
    --hidden-import "passlib.handlers.bcrypt" `
    --exclude-module "onnx" `
    --exclude-module "onnx.reference" `
    --exclude-module "onnxruntime" `
    --exclude-module "onnxslim" `
    --exclude-module "torchaudio" `
    --exclude-module "PyQt5" `
    --collect-all "ultralytics" `
    desktop_main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "============================" -ForegroundColor Red
    Write-Host "Build Failed! PyInstaller exited with code $LASTEXITCODE." -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
    Write-Host "============================" -ForegroundColor Red
    pause
    exit $LASTEXITCODE
}

$appPath = Join-Path $PSScriptRoot "dist\YOLO_Disease_System"
$exePath = Join-Path $appPath "YOLO_Disease_System.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "============================" -ForegroundColor Red
    Write-Host "Build Failed! The exe was not generated." -ForegroundColor Red
    Write-Host "Expected exe path: $exePath" -ForegroundColor Red
    Write-Host "============================" -ForegroundColor Red
    pause
    exit 1
}

# [Step 4] Post-build success
Write-Host "============================" -ForegroundColor Green
Write-Host "Build Successful!" -ForegroundColor Green
Write-Host "Your customized AI model is now integrated." -ForegroundColor Green
Write-Host "The application is at: $appPath" -ForegroundColor Green
Write-Host "Executable: $exePath" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
pause
