# Ollama 部署檢查清單

## ✅ 快速檢查

### 步驟 1: Ollama 安裝 (5 分鐘)

```bash
# 訪問
https://ollama.ai/download

# 或 macOS Homebrew
brew install ollama

# 驗證安裝
ollama --version
```

- [ ] Ollama 已安裝
- [ ] `ollama --version` 可以運行

### 步驟 2: 拉取視覺模型 (10-30 分鐘)

```bash
# 選擇一個模型

# 推薦 - 平衡 (6.3GB)
ollama pull llava

# 或輕量版 (3.9GB)
ollama pull bakllava

# 或高精度 (20GB)
ollama pull llava:34b
```

- [ ] 至少一個視覺模型已安裝
- [ ] 運行 `ollama list` 確認

### 步驟 3: 啟動 Ollama (1 分鐘)

```bash
# 新開一個終端運行（或後台運行）
ollama serve

# 驗證
# 應該看到: "Listening on 127.0.0.1:11434"
```

- [ ] Ollama 正在運行
- [ ] 監聽 `localhost:11434`

### 步驟 4: 配置後端 (2 分鐘)

```bash
cd backend

# 複製環境文件
cp .env.example .env

# .env 應已包含:
# OLLAMA_ENABLED=true
# OLLAMA_URL=http://localhost:11434
# OLLAMA_MODEL=llava
```

- [ ] `.env` 文件已創建
- [ ] Ollama 配置已驗證

### 步驟 5: 安裝 Python 依賴 (2 分鐘)

```bash
cd backend

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

- [ ] 虛擬環境已創建
- [ ] 依賴已安裝

### 步驟 6: 啟動後端 (1 分鐘)

```bash
# 從 backend 目錄
python app.py

# 或從項目根目錄
python run_dev.py
```

**應該看到：**
```
✅ Ollama 連接成功
Running on http://127.0.0.1:5000
```

- [ ] 後端服務已啟動
- [ ] Ollama 連接成功
- [ ] 運行在 `http://localhost:5000`

### 步驟 7: 安裝 Chrome 擴展 (2 分鐘)

```bash
# 1. 打開 Chrome
# 2. 訪問 chrome://extensions/
# 3. 啟用「開發者模式」（右上角）
# 4. 點擊「加載未打包的擴展程式」
# 5. 選擇 chrome-extension 文件夾
# 6. 完成！
```

- [ ] 擴展已加載
- [ ] 擴展圖標可見

### 步驟 8: 測試功能 (2 分鐘)

```bash
# 在任何網頁上:
# 1. 按 Alt+A 或點擊擴展圖標
# 2. 確認 Ollama 已選為模型
# 3. 點擊「📸 截圖」
# 4. 輸入一個問題，例如「這個頁面是做什麼的？」
# 5. 點擊「發送」
# 6. 等待 Ollama 回應
```

- [ ] 側邊欄彈出
- [ ] 截圖功能工作
- [ ] Ollama 回應成功

---

## 🧪 驗證工具

### 運行集成測試

```bash
# 從項目根目錄
python test_ollama_integration.py
```

應該看到：
```
✅ Ollama 服務: 通過
✅ 視覺模型: 通過  
✅ API 調用: 通過
✅ 後端集成: 通過
```

- [ ] 所有測試通過

---

## 🔧 常見問題

### Ollama 無法連接

```bash
# 檢查 Ollama 是否運行
curl http://localhost:11434/api/tags

# 如果失敗，啟動 Ollama
ollama serve
```

### 模型不存在

```bash
# 列出已安裝的模型
ollama list

# 如果沒有，拉取模型
ollama pull llava
```

### 後端報錯 "無法連接到 Ollama"

```bash
# 確保 .env 中的配置正確
grep OLLAMA backend/.env

# 應該是:
# OLLAMA_ENABLED=true
# OLLAMA_URL=http://localhost:11434
```

### 超時或性能不佳

```bash
# 嘗試輕量版模型
ollama pull bakllava

# 在 .env 中更改
OLLAMA_MODEL=bakllava
```

---

## 📊 系統要求

| 項目 | 要求 | 推薦 |
|------|------|------|
| CPU | 現代 Intel/AMD | i7/Ryzen 7+ |
| RAM | 4GB | 8GB+ |
| GPU | 可選 | NVIDIA/M1+ |
| 存儲 | 20GB | 30GB+ |
| 網絡 | 下載時 | 100Mbps+ |

---

## 🚀 性能預期

### 首次使用
- 啟動延遲: 3-10 秒（模型加載）
- API 響應時間: 5-20 秒（取決於硬件）

### 正常使用
- 啟動延遲: <1 秒
- API 響應時間: 2-10 秒

### 優化建議
1. 確保 GPU 驅動最新
2. 使用 bakllava 如果性能不佳
3. 關閉其他應用以釋放資源

---

## 📞 需要幫助？

### 文檔
- **完整指南**: `OLLAMA_SETUP.md`
- **集成說明**: `OLLAMA_INTEGRATION_SUMMARY.md`
- **使用指南**: `USAGE.md`

### 測試
```bash
python test_ollama_integration.py
```

### 日誌查看
```bash
# 後端日誌會顯示 Ollama 連接狀態
tail -f backend/app.log  # 如果啟用日誌
```

---

## ✨ 成功標誌

✅ 所有步驟完成  
✅ 測試工具通過  
✅ Chrome 擴展工作  
✅ Ollama 回應成功  

**恭喜！你已經成功設置了 Ollama 集成！** 🎉

現在你可以：
- 完全隱私地使用 AI 助手
- 完全離線工作
- 無限制地提問
- 完全控制你的數據

**享受校務系統 AI 助手！** 🚀
