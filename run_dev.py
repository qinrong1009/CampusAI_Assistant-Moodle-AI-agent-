"""
本地開發啟動腳本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """啟動開發環境"""
    
    # 獲取項目根目錄
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    
    print("=" * 50)
    print("校務系統 AI 助手 - 開發環境啟動")
    print("=" * 50)
    
    # 檢查必要的文件
    if not (backend_dir / 'requirements.txt').exists():
        print("❌ 找不到 requirements.txt")
        return
    
    env_file = backend_dir / '.env'
    if not env_file.exists():
        env_example = backend_dir / '.env.example'
        if env_example.exists():
            print("⚠️  .env 文件未找到")
            print("📋 請複製 .env.example 為 .env 並填入 API 密鑰")
            print(f"📍 位置: {backend_dir}")
            return
    
    # 啟動後端
    print("\n🚀 啟動 Flask 後端服務...")
    print(f"📍 工作目錄: {backend_dir}")
    print("💻 訪問地址: http://localhost:5000")
    print("📊 健康檢查: http://localhost:5000/health")
    
    os.chdir(backend_dir)
    
    # 安裝依賴
    print("\n📦 檢查依賴...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'], 
                      check=False)
    except Exception as e:
        print(f"⚠️  安裝依賴時出錯: {e}")
    
    # 啟動應用
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 開發服務已停止")

if __name__ == '__main__':
    main()
