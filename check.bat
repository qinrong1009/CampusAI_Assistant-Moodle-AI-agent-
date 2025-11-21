@echo off
REM 校務系統 AI 助手 - Windows 系統檢查腳本

setlocal enabledelayedexpansion
setlocal enableextensions

echo 🔍 校務系統 AI 助手 - 系統完整性檢查
echo ========================================
echo.

set "total=0"
set "passed=0"

REM 檢查前端
echo 📦 Chrome Extension (前端):
set "files=chrome-extension\manifest.json" "chrome-extension\src\html\popup.html" "chrome-extension\src\html\sidebar.html" "chrome-extension\src\css\popup.css" "chrome-extension\src\css\sidebar.css" "chrome-extension\src\js\background.js" "chrome-extension\src\js\content.js" "chrome-extension\src\js\popup.js" "chrome-extension\src\js\sidebar.js"

for %%f in (%files%) do (
    set /a total=!total!+1
    if exist %%f (
        echo ✓ 存在: %%f
        set /a passed=!passed!+1
    ) else (
        echo ✗ 缺失: %%f
    )
)
echo.

REM 檢查後端
echo 🐍 Python Backend:
set "files=backend\app.py" "backend\config.py" "backend\wsgi.py" "backend\requirements.txt" "backend\.env.example"

for %%f in (%files%) do (
    set /a total=!total!+1
    if exist %%f (
        echo ✓ 存在: %%f
        set /a passed=!passed!+1
    ) else (
        echo ✗ 缺失: %%f
    )
)

set "dirs=backend\app"
for %%d in (%dirs%) do (
    set /a total=!total!+1
    if exist %%d (
        echo ✓ 存在: %%d
        set /a passed=!passed!+1
    ) else (
        echo ✗ 缺失: %%d
    )
)
echo.

REM 檢查啟動腳本
echo 🔧 啟動腳本:
set "files=run_dev.py" "run_dev.sh" "run_dev.bat"

for %%f in (%files%) do (
    set /a total=!total!+1
    if exist %%f (
        echo ✓ 存在: %%f
        set /a passed=!passed!+1
    ) else (
        echo ✗ 缺失: %%f
    )
)
echo.

REM 檢查配置
echo 🐳 Docker 配置:
set "files=Dockerfile" "docker-compose.yml" ".gitignore"

for %%f in (%files%) do (
    set /a total=!total!+1
    if exist %%f (
        echo ✓ 存在: %%f
        set /a passed=!passed!+1
    ) else (
        echo ✗ 缺失: %%f
    )
)
echo.

REM 檢查文檔
echo 📚 文檔:
set "files=README.md" "QUICKSTART.md" "SETUP.md" "USAGE.md" "ARCHITECTURE.md" "DEVELOPMENT.md" "CHECKLIST.md" "READY.md" "FINAL.md" "DELIVERY_REPORT.md"

for %%f in (%files%) do (
    set /a total=!total!+1
    if exist %%f (
        echo ✓ 存在: %%f
        set /a passed=!passed!+1
    ) else (
        echo ✗ 缺失: %%f
    )
)
echo.

REM 檢查 Python
echo 🐍 Python 環境:
set /a total=!total!+1
where python >nul 2>nul
if !errorlevel! equ 0 (
    echo ✓ Python 已安裝
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo   %%i
    set /a passed=!passed!+1
) else (
    echo ✗ Python 未安裝
)
echo.

REM 最終結果
echo ========================================
echo 檢查結果: %passed%/%total%

REM 計算百分比
set /a percentage=!passed!*100/%total%
echo 完成度: %percentage%%%
echo.

if %percentage% equ 100 (
    echo 🎉 系統檢查通過！一切就緒！
    echo.
    echo 📝 下一步:
    echo   1. cd backend
    echo   2. copy .env.example .env
    echo   3. 編輯 .env 粘貼 API 密鑰
    echo   4. python run_dev.py
    echo   5. 在 Chrome 中加載 chrome-extension 文件夾
    echo.
    exit /b 0
) else if %percentage% geq 80 (
    echo ⚠️ 大部分文件已就位，請補充缺失的文件
    exit /b 1
) else (
    echo ❌ 文件缺失過多，請檢查目錄結構
    exit /b 1
)
