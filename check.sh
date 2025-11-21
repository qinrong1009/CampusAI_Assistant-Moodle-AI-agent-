#!/bin/bash
# 校務系統 AI 助手 - 系統檢查腳本

echo "🔍 校務系統 AI 助手 - 系統完整性檢查"
echo "========================================"
echo ""

# 設定顏色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 計數器
total=0
passed=0

# 檢查函數
check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} 存在: $1"
        passed=$((passed + 1))
    else
        echo -e "${RED}❌${NC} 缺失: $1"
    fi
}

check_directory() {
    total=$((total + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} 存在: $1"
        passed=$((passed + 1))
    else
        echo -e "${RED}❌${NC} 缺失: $1"
    fi
}

# 檢查前端
echo "📦 Chrome Extension (前端):"
check_file "chrome-extension/manifest.json"
check_file "chrome-extension/src/html/popup.html"
check_file "chrome-extension/src/html/sidebar.html"
check_file "chrome-extension/src/css/popup.css"
check_file "chrome-extension/src/css/sidebar.css"
check_file "chrome-extension/src/js/background.js"
check_file "chrome-extension/src/js/content.js"
check_file "chrome-extension/src/js/popup.js"
check_file "chrome-extension/src/js/sidebar.js"
echo ""

# 檢查後端
echo "🐍 Python Backend:"
check_file "backend/app.py"
check_file "backend/config.py"
check_file "backend/wsgi.py"
check_file "backend/requirements.txt"
check_file "backend/.env.example"
check_directory "backend/app"
check_file "backend/app/__init__.py"
check_file "backend/app/models/ai_model.py"
check_file "backend/app/routes/api_routes.py"
echo ""

# 檢查啟動腳本
echo "🔧 啟動腳本:"
check_file "run_dev.py"
check_file "run_dev.sh"
check_file "run_dev.bat"
echo ""

# 檢查配置
echo "🐳 Docker 配置:"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file ".gitignore"
echo ""

# 檢查文檔
echo "📚 文檔:"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "SETUP.md"
check_file "USAGE.md"
check_file "ARCHITECTURE.md"
check_file "DEVELOPMENT.md"
check_file "CHECKLIST.md"
check_file "READY.md"
check_file "FINAL.md"
check_file "DELIVERY_REPORT.md"
check_file "PROJECT_SUMMARY.md"
echo ""

# 檢查 Python 環境
echo "🐍 Python 環境:"
total=$((total + 1))
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅${NC} Python 已安裝: $python_version"
    passed=$((passed + 1))
else
    echo -e "${RED}❌${NC} Python 未安裝"
fi
echo ""

# 檢查 Chrome
echo "🌐 Chrome 瀏覽器:"
total=$((total + 1))
if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null; then
    echo -e "${GREEN}✅${NC} Chrome/Chromium 已安裝"
    passed=$((passed + 1))
else
    echo -e "${YELLOW}⚠️${NC} Chrome 未找到 (可能需要手動安裝)"
fi
echo ""

# 最終結果
echo "========================================"
echo "檢查結果: $passed/$total"
percentage=$((passed * 100 / total))
echo "完成度: $percentage%"
echo ""

if [ $percentage -eq 100 ]; then
    echo -e "${GREEN}🎉 系統檢查通過！一切就緒！${NC}"
    echo ""
    echo "📝 下一步:"
    echo "  1. cd backend"
    echo "  2. cp .env.example .env"
    echo "  3. 編輯 .env 粘貼 API 密鑰"
    echo "  4. python run_dev.py"
    echo "  5. 在 Chrome 中加載 chrome-extension 文件夾"
    echo ""
    exit 0
elif [ $percentage -ge 80 ]; then
    echo -e "${YELLOW}⚠️ 大部分文件已就位，請補充缺失的文件${NC}"
    exit 1
else
    echo -e "${RED}❌ 文件缺失過多，請檢查目錄結構${NC}"
    exit 1
fi
