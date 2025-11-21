# 校務系統 AI 助手 - 快速開始 (5 分鐘)

## ⚡ 快速設置 (4 步)

### 1️⃣ 選擇 AI 模型 (可選)

**推薦：使用 Ollama 本地模型**

Ollama 是最簡單的方式 - 無需 API 密鑰，完全隱私，可離線使用！

```bash
# 安裝 Ollama (macOS/Linux/Windows)
# https://ollama.ai

# 安裝視覺模型 (推薦)
ollama pull llava

# 在後台運行 Ollama
ollama serve
```

**或者：使用雲端 API（可選）**

如果不想用 Ollama，可以選擇這些中的一個：

#### Qwen 2.5 (最快)
```bash
# 1. 訪問: https://dashscope.console.aliyun.com/
# 2. 登錄或註冊
# 3. 創建 API 密鑰
```

#### GPT-4V
```bash
# 1. 訪問: https://platform.openai.com/api-keys
# 2. 創建 API 密鑰
```

#### Claude 3
```bash
# 1. 訪問: https://console.anthropic.com/
# 2. 創建 API 密鑰
```

### 2️⃣ 配置後端 (1 分鐘)

```bash
# 進入項目目錄
cd Capstone/backend

# 複製環境文件
cp .env.example .env

# 編輯 .env 文件並粘貼你的 API 密鑰
# macOS/Linux:
nano .env

# Windows:
notepad .env

# 粘貼你的 API 密鑰到相應行
```

### 3️⃣ 啟動後端 (1 分鐘)

```bash
# macOS/Linux:
cd .. && python run_dev.py

# 或 Windows:
python run_dev.py

# 或直接在 backend 目錄:
python app.py
```

**看到這個消息表示成功：**
```
Running on http://127.0.0.1:5000
```

### 4️⃣ 安裝 Chrome 擴展 (1 分鐘)

1. 打開 Chrome 瀏覽器
2. 訪問 `chrome://extensions/`
3. 右上角打開「開發者模式」
4. 點擊「加載未打包的擴展程式」
5. 選擇 `Capstone/chrome-extension` 文件夾
6. ✅ 完成！

---

## 🎯 現在開始使用

### 激活助手

在任何網頁上：
- **快捷鍵方式**：按 `Alt+A`
- **或點擊圖標**：點擊工具欄中的擴展圖標

### 提出問題

1. 點擊「📸 截圖」捕捉頁面
2. 輸入你的問題
3. 點擊「發送」
4. 等待 AI 回應（通常 2-5 秒）

---

## 💡 使用示例

### 示例 1：查詢成績

```
問題: 我如何查看我的學期成績？
[截圖校務系統]
→ AI: 根據截圖，我看到校務系統首頁。請按以下步驟操作：
   1. 點擊左側菜單中的"成績查詢"
   2. 選擇學年和學期
   3. 點擊"查詢"按鈕
```

### 示例 2：選課問題

```
問題: 為什麼我無法添加這個課程？
[截圖選課頁面]
→ AI: 我看到錯誤提示"時間衝突"。這意味著...
```

### 示例 3：系統操作

```
問題: 怎樣修改我的個人信息？
[截圖個人資料頁面]
→ AI: 點擊"編輯"按鈕，然後修改相應字段，最後點擊"保存"。
```

---

## 📊 模型對比表

| 特性 | Ollama | Qwen 2.5 | GPT-4V | Claude 3 |
|------|--------|---------|--------|----------|
| **API 密鑰** | ❌ 無需 | ✅ 需要 | ✅ 需要 | ✅ 需要 |
| **隱私** | 🔐 完全隱私 | ❌ 上傳到雲 | ❌ 上傳到雲 | ❌ 上傳到雲 |
| **離線** | ✅ 支持 | ❌ 需要網絡 | ❌ 需要網絡 | ❌ 需要網絡 |
| **成本** | 💰 免費 | 💰 低 | 💰 中等 | 💰 中等 |
| **速度** | ⚡ 快 | ⚡ 快 | ⚡ 快 | ⚡ 中等 |
| **準確度** | 🎯 較好 | 🎯 優秀 | 🎯 最佳 | 🎯 優秀 |

**推薦搭配：**
- 💡 優先使用 Ollama (本地隱私)
- 🔄 備用 Qwen 2.5 (快速備選)

---

## ✅ 驗證一切正常

### 後端健康檢查

```bash
# 在新終端運行
curl http://localhost:5000/health

# 應該返回:
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 檢查可用模型

```bash
curl http://localhost:5000/api/models

# 應該返回你配置的模型
```

---

## 🆘 快速故障排除

| 問題 | 解決方案 |
|------|---------|
| **Ollama 連接失敗** | 確保 Ollama 已啟動: `ollama serve` |
| **Ollama 模型缺失** | 拉取模型: `ollama pull llava` |
| **後端無法啟動** | 檢查虛擬環境是否激活: `source venv/bin/activate` |
| **端口已被占用** | 改變 PORT 設定或殺死現有進程 |
| **擴展不出現** | 重新加載擴展或清除快取 |
| **截圖失敗** | 確保頁面完全加載 |
| **API 連接失敗** | 檢查後端是否運行: `curl localhost:5000/health` |
| **API 密鑰錯誤** | 檢查 `.env` 文件中的密鑰是否正確 |

---

## 📚 更多幫助

- **完整安裝指南**: 見 [SETUP.md](SETUP.md)
- **開發文檔**: 見 [DEVELOPMENT.md](DEVELOPMENT.md)  
- **主要文檔**: 見 [README.md](README.md)
- **Ollama 設置**: 見 [OLLAMA_SETUP.md](OLLAMA_SETUP.md) (即將提供)

---

**🎉 你現在已經準備好使用校務系統 AI 助手了！**

有任何問題，請參考上面的故障排除部分或查看完整文檔。
