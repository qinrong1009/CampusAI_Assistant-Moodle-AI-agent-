# Ollama 設置指南

## 🎯 什麼是 Ollama？

**Ollama** 是一個簡單的方式在本地電腦上運行大型語言模型。它提供：

✅ **完全隱私** - 數據不上傳到任何服務器  
✅ **完全免費** - 無需 API 密鑰或付費  
✅ **完全離線** - 無需網絡連接即可運行  
✅ **超快速** - 在本地 GPU 上運行（或 CPU）  

---

## 📥 安裝 Ollama

### macOS

```bash
# 訪問 Ollama 網站下載
https://ollama.ai/download

# 或使用 Homebrew（如果已安裝）
brew install ollama

# 啟動 Ollama 後台服務
ollama serve
```

### Linux (Ubuntu/Debian)

```bash
# 官方安裝腳本
curl -fsSL https://ollama.ai/install.sh | sh

# 啟動 Ollama
ollama serve
```

### Windows

```bash
# 下載安裝程式
https://ollama.ai/download/windows

# 或使用 Scoop
scoop install ollama

# 啟動 Ollama (Windows 會自動在後台運行)
ollama serve
```

---

## 🤖 安裝視覺模型

### 推薦模型

#### 1. **LLaVA (推薦 - 最平衡)**
```bash
ollama pull llava
# ~6.3GB - 高質量，對話能力強，速度快
```

#### 2. **LLaVA 34B (更強大)**
```bash
ollama pull llava:34b
# ~20GB - 更精準，但需要 GPU，更慢
```

#### 3. **BakLLaVA (輕量版)**
```bash
ollama pull bakllava
# ~3.9GB - 更輕快，適合 CPU 運行
```

### 如何選擇？

| 模型 | 大小 | 速度 | 準確度 | GPU 需求 |
|------|------|------|--------|----------|
| LLaVA | 6.3GB | ⚡⚡⚡ | 🎯🎯🎯 | 推薦 |
| LLaVA 34B | 20GB | ⚡⚡ | 🎯🎯🎯🎯 | 必需 |
| BakLLaVA | 3.9GB | ⚡⚡⚡⚡ | 🎯🎯 | 不需 |

**推薦搭配：**
- 💻 有 GPU：使用 **llava** (標準版)
- 💾 空間有限：使用 **bakllava** (輕量版)
- 🚀 想要最好：使用 **llava:34b** (但需要高端 GPU)

---

## ⚙️ 配置校務系統 AI 助手

### 步驟 1：確認 Ollama 運行

```bash
# 新開一個終端
# Ollama 應該在後台運行

# 測試連接
curl http://localhost:11434/api/tags
```

**應該會返回類似的結果：**
```json
{
  "models": [
    {
      "name": "llava:latest",
      "digest": "...",
      "size": 6789000000,
      "modified_time": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

### 步驟 2：配置 `.env` 文件

```bash
cd Capstone/backend

# 編輯 .env 文件
nano .env
```

**添加以下配置：**
```bash
# Ollama 設定 (本地模型)
OLLAMA_ENABLED=true
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llava

# 可選：雲端 API 備選（如果 Ollama 失敗）
# QWEN_API_KEY=xxx  # 備選
```

**完整 `.env` 示例：**
```bash
# Flask 設定
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# ===== Ollama (本地) =====
OLLAMA_ENABLED=true
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llava

# ===== 雲端 API (備選) =====
QWEN_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here

# 日誌
LOG_LEVEL=INFO
```

### 步驟 3：啟動後端

```bash
# 返回項目根目錄
cd ..

# 啟動後端
python run_dev.py

# 或直接
python backend/app.py
```

**看到這行表示成功：**
```
✓ Ollama 連接成功 (模型: llava)
Running on http://127.0.0.1:5000
```

### 步驟 4：安裝 Chrome 擴展

1. 打開 Chrome 瀏覽器
2. 訪問 `chrome://extensions/`
3. 右上角打開「開發者模式」
4. 點擊「加載未打包的擴展程式」
5. 選擇 `Capstone/chrome-extension` 文件夾
6. ✅ 完成！

---

## 🧪 測試 Ollama 集成

### 方法 1：測試 API 端點

```bash
# 在新終端運行

# 檢查健康狀態
curl http://localhost:5000/health

# 列出可用模型
curl http://localhost:5000/api/models

# 返回應該包含:
{
  "models": {
    "ollama": {
      "name": "Ollama (本地)",
      "status": "available",
      "model": "llava"
    },
    ...
  }
}
```

### 方法 2：發送測試請求

```bash
# 創建測試圖片（base64 編碼）
# 或使用下面的測試腳本
```

**Python 測試腳本：**
```python
import requests
import json

# 打開一張圖片
with open('test_image.png', 'rb') as f:
    import base64
    image_data = base64.b64encode(f.read()).decode('utf-8')

# 發送請求
response = requests.post('http://localhost:5000/api/ask', json={
    'question': '這張圖片中有什麼？',
    'image': image_data,
    'model_type': 'ollama'
})

print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

### 方法 3：使用 Chrome 擴展測試

1. 在任何網頁上按 `Alt+A` 啟動助手
2. 點擊「📸 截圖」
3. 輸入問題，例如「這個頁面是做什麼的？」
4. 點擊「發送」
5. 等待 Ollama 回應

---

## 🔧 故障排除

### 問題 1：Ollama 連接失敗

**症狀：** 後端啟動時出現 `Ollama 連接失敗` 錯誤

**解決方案：**
```bash
# 確保 Ollama 在運行
ollama serve

# 確保 OLLAMA_URL 正確
# 檢查 .env 中的設置
echo $OLLAMA_URL  # 應該是 http://localhost:11434
```

### 問題 2：模型不存在

**症狀：** `错误: 模型 'llava' 不存在`

**解決方案：**
```bash
# 拉取模型
ollama pull llava

# 等待下載完成
# 查看已安裝的模型
ollama list
```

### 問題 3：內存不足

**症狀：** `CUDA out of memory` 或進程被殺死

**解決方案：**
```bash
# 使用更輕量的模型
ollama pull bakllava

# 或限制 Ollama 的 GPU 內存使用
export OLLAMA_MAX_LOADED_MODELS=1  # 同時只加載 1 個模型
```

### 問題 4：速度非常慢

**症狀：** 回應需要 30 秒以上

**解決方案：**

1. **檢查是否使用 GPU：**
   ```bash
   ollama list  # 查看加載的模型
   ```

2. **使用更輕量的模型：**
   ```bash
   ollama pull bakllava  # 比標準版快 2-3 倍
   ```

3. **增加 GPU 內存：**
   - 編輯 `.env` 添加：`OLLAMA_NUM_GPU=-1`

4. **檢查電腦資源：**
   - 確保沒有其他程式佔用 GPU

### 問題 5：截圖後沒有回應

**症狀：** 發送請求後一直等待

**解決方案：**

```bash
# 1. 檢查後端日誌
# 查看是否有錯誤信息

# 2. 測試 Ollama 直接調用
curl http://localhost:11434/api/generate \
  -d '{
    "model": "llava",
    "prompt": "What is in this image?",
    "stream": false
  }' -X POST
```

---

## 🚀 性能優化

### 1. 啟用 GPU 加速

```bash
# 查看 GPU 使用情況
export OLLAMA_DEBUG=1
ollama serve

# 對於 NVIDIA GPU
export OLLAMA_CUDA=1

# 對於 Apple Silicon (M1/M2/M3)
# 自動檢測，無需額外配置
```

### 2. 預加載模型

```bash
# 在啟動後端前，預加載模型到內存
ollama run llava "Warm up"

# 這樣首次請求會更快
```

### 3. 並行化設置

```bash
# 在 .env 中添加
# 允許多個並發請求
OLLAMA_NUM_PARALLEL=4
```

---

## 📊 模型選擇建議

### 根據硬件選擇

**GPU 充足（6GB+ VRAM）：**
```bash
ollama pull llava          # 標準版 - 最平衡
```

**GPU 有限（4GB VRAM）：**
```bash
ollama pull bakllava       # 輕量版 - 更快
```

**無 GPU（只有 CPU）：**
```bash
ollama pull bakllava       # 必須用輕量版
# 或使用雲端模型作為備選
```

**超高端 GPU（24GB+ VRAM）：**
```bash
ollama pull llava:34b      # 最強版 - 最精準
```

### 根據用途選擇

| 用途 | 推薦模型 | 理由 |
|------|---------|------|
| 校務系統查詢 | **llava** | 平衡速度和準確度 |
| 快速推斷 | **bakllava** | 最快，適合實時交互 |
| 複雜分析 | **llava:34b** | 最精準，慢但可靠 |
| 教學/研究 | **llava:34b** | 理解力最好 |

---

## 📚 更多資源

- **Ollama 官網**: https://ollama.ai
- **模型庫**: https://ollama.ai/library
- **GitHub**: https://github.com/ollama/ollama
- **論壇**: https://github.com/ollama/ollama/discussions

---

## ✅ 檢查清單

- [ ] Ollama 已安裝
- [ ] 視覺模型已下載 (llava/bakllava/llava:34b)
- [ ] Ollama 正在後台運行 (`ollama serve`)
- [ ] `.env` 文件已配置正確
- [ ] 後端可以成功連接到 Ollama
- [ ] Chrome 擴展已加載
- [ ] 在網頁上測試成功 (Alt+A)

**全部完成後，你就可以完全離線使用校務系統 AI 助手了！** 🎉

---

## 💡 下一步

1. **備選方案** - 如果想要備選的雲端模型：
   - 參考 [README.md](README.md) 的 API 密鑰配置部分

2. **開發** - 如果想要修改或擴展：
   - 參考 [DEVELOPMENT.md](DEVELOPMENT.md)

3. **故障排除** - 遇到其他問題：
   - 參考 [SETUP.md](SETUP.md) 的故障排除部分
