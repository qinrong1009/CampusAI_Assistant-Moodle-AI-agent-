#!/usr/bin/env python3
"""
Ollama 集成測試腳本
驗證 Ollama 是否正確安裝和配置
"""

import requests
import json
import sys
import base64
from pathlib import Path

def check_ollama_service():
    """檢查 Ollama 服務是否運行"""
    print("🔍 檢查 Ollama 服務...")
    
    ollama_url = "https://primehub.aic.ncku.edu.tw/console/apps/ollama-0-13-0-i1oyy"
    
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"✅ Ollama 服務運行正常: {ollama_url}")
            models = response.json().get("models", [])
            if models:
                print(f"📦 可用模型:")
                for model in models:
                    print(f"   - {model['name']} ({model['size'] / 1e9:.1f}GB)")
                return True
            else:
                print("⚠️ 未找到已安裝的模型")
                return False
        else:
            print(f"❌ Ollama 返回錯誤: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 無法連接到 Ollama ({ollama_url})")
        print("💡 提示: 請先運行 `ollama serve`")
        return False
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return False

def check_vision_models():
    """檢查是否安裝了視覺模型"""
    print("\n🔍 檢查視覺模型...")
    
    ollama_url = "https://primehub.aic.ncku.edu.tw/console/apps/ollama-0-13-0-i1oyy"
    
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        
        vision_models = {
            "llava": "標準版 (推薦)",
            "llava:34b": "高精度版",
            "bakllava": "輕量版"
        }
        
        found_vision = False
        for model_name, desc in vision_models.items():
            if any(model_name in name for name in model_names):
                print(f"✅ 已安裝: {model_name} ({desc})")
                found_vision = True
        
        if not found_vision:
            print("⚠️ 未找到視覺模型，請運行:")
            print("   ollama pull llava")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 檢查失敗: {str(e)}")
        return False

def test_generation():
    """測試 API 調用"""
    print("\n🧪 測試 API 調用...")
    
    ollama_url = "https://primehub.aic.ncku.edu.tw/console/apps/ollama-0-13-0-i1oyy"
    
    try:
        # 簡單文本生成測試
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llava",
                "prompt": "簡潔回答: 這是什麼？",
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 調用成功")
            return True
        else:
            print(f"❌ API 返回錯誤: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("⏱️ 請求超時（可能模型太大或 GPU 不足）")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def check_backend_integration():
    """檢查後端集成"""
    print("\n🔗 檢查後端集成...")
    
    backend_url = "http://localhost:5000"
    
    try:
        # 檢查後端是否運行
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"⚠️ 後端服務未啟動或返回錯誤")
            return False
        
        print("✅ 後端服務運行正常")
        
        # 檢查可用模型
        response = requests.get(f"{backend_url}/api/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", {})
            ollama_status = models.get("ollama", {}).get("status")
            if ollama_status == "available":
                print("✅ Ollama 已在後端配置並可用")
                return True
            else:
                print(f"⚠️ Ollama 狀態: {ollama_status}")
                return False
        else:
            print("❌ 無法獲取模型列表")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️ 無法連接到後端 ({backend_url})")
        print("💡 提示: 請先運行 `python run_dev.py` 或 `python app.py`")
        return False
    except Exception as e:
        print(f"❌ 檢查失敗: {str(e)}")
        return False

def main():
    """主函數"""
    print("=" * 50)
    print("  Ollama 集成驗證工具")
    print("=" * 50)
    
    results = {
        "Ollama 服務": check_ollama_service(),
        "視覺模型": check_vision_models(),
        "API 調用": test_generation(),
        "後端集成": check_backend_integration(),
    }
    
    print("\n" + "=" * 50)
    print("  檢查結果")
    print("=" * 50)
    
    for check, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{check}: {status}")
    
    # 總體結果
    all_passed = all(results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有檢查通過！Ollama 已準備就緒")
        print("\n下一步:")
        print("1. 啟動後端: python run_dev.py")
        print("2. 在 Chrome 中加載擴展")
        print("3. 在網頁上按 Alt+A 測試")
    else:
        print("⚠️ 某些檢查失敗，請按照提示修復")
        print("\n常見問題:")
        print("- Ollama 未運行: 執行 `ollama serve`")
        print("- 缺少視覺模型: 執行 `ollama pull llava`")
        print("- 後端未運行: 執行 `python run_dev.py`")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
