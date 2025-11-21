#!/bin/bash

# 開發環境啟動腳本（Mac/Linux）

echo "================================"
echo "校務系統 AI 助手 - 開發環境"
echo "================================"

# 獲取項目根目錄
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 檢查 .env 文件
if [ ! -f "$BACKEND_DIR/.env" ]; then
    if [ -f "$BACKEND_DIR/.env.example" ]; then
        echo "⚠️  .env 文件未找到"
        echo "📋 請複製 .env.example 為 .env 並填入 API 密鑰"
        echo "📍 位置: $BACKEND_DIR"
        exit 1
    fi
fi

# 進入後端目錄
cd "$BACKEND_DIR"

echo ""
echo "🚀 啟動 Flask 後端服務..."
echo "📍 工作目錄: $BACKEND_DIR"
echo "💻 訪問地址: http://localhost:5000"
echo "📊 健康檢查: http://localhost:5000/health"
echo ""

# 安裝依賴
echo "📦 檢查依賴..."
python3 -m pip install -q -r requirements.txt

# 啟動應用
echo "⏳ 啟動應用中..."
python3 app.py
