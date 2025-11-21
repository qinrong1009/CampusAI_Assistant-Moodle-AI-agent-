@echo off

REM 開發環境啟動腳本（Windows）

echo ================================
echo 校務系統 AI 助手 - 開發環境
echo ================================

REM 獲取項目根目錄
set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend

REM 檢查 .env 文件
if not exist "%BACKEND_DIR%\.env" (
    if exist "%BACKEND_DIR%\.env.example" (
        echo ⚠️  .env 文件未找到
        echo 📋 請複製 .env.example 為 .env 並填入 API 密鑰
        echo 📍 位置: %BACKEND_DIR%
        exit /b 1
    )
)

REM 進入後端目錄
cd /d "%BACKEND_DIR%"

echo.
echo 🚀 啟動 Flask 後端服務...
echo 📍 工作目錄: %BACKEND_DIR%
echo 💻 訪問地址: http://localhost:5000
echo 📊 健康檢查: http://localhost:5000/health
echo.

REM 安裝依賴
echo 📦 檢查依賴...
python -m pip install -q -r requirements.txt

REM 啟動應用
echo ⏳ 啟動應用中...
python app.py
