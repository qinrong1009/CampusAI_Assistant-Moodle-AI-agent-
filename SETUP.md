# 校務系統 AI 助手 - 完整安裝指南

## 📋 目錄

1. [系統要求](#系統要求)
2. [後端設置](#後端設置)
3. [Chrome 擴展安裝](#chrome-擴展安裝)
4. [配置和使用](#配置和使用)
5. [故障排除](#故障排除)

---

## 系統要求

### 軟件要求

| 組件 | 最低版本 | 推薦版本 |
|------|---------|---------|
| Chrome | 88 | 最新版本 |
| Python | 3.8 | 3.10+ |
| Git | 2.0 | 最新版本 |

### 硬件要求

- **RAM**: 2GB 最低，4GB 推薦
- **儲存空間**: 1GB 最小
- **網絡**: 穩定的互聯網連接

---

## 後端設置

### 步驟 1: 安裝 Python

**Windows:**
```bash
# 訪問 https://www.python.org/ 下載安裝程序
# 安裝時勾選 "Add Python to PATH"
```

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

### 步驟 2: 克隆或下載項目

```bash
# 如果使用 Git
git clone <repository-url>
cd Capstone

# 或直接下載並解壓縮
unzip Capstone.zip
cd Capstone
```

### 步驟 3: 創建虛擬環境

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

### 步驟 4: 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

**輸出示例：**
```
Successfully installed flask-3.0.0 flask-cors-4.0.0 python-dotenv-1.0.0 ...
```

### 步驟 5: 配置 AI 模型

#### 複製環境文件
```bash
cp .env.example .env
```

#### 編輯 `.env` 文件

使用你喜歡的編輯器打開 `backend/.env`：

```bash
# 編輯 .env 文件
nano .env          # Linux/macOS
# 或
code .env          # VS Code
```

#### 方式 A: 使用 Ollama（推薦 - 無需 API 密鑰）

**優點：完全免費 · 完全隱私 · 可完全離線**

1. 首先安裝 Ollama：
   ```bash
   # 訪問 https://ollama.ai 下載並安裝
   ```

2. 拉取視覺模型：
   ```bash
   ollama pull llava
   ```

3. 在 `.env` 中配置：
   ```
   OLLAMA_ENABLED=true
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llava
   ```

4. 啟動 Ollama：
   ```bash
   ollama serve  # 在另一個終端運行
   ```

**詳細指南：** 見 [OLLAMA_SETUP.md](OLLAMA_SETUP.md)

#### 方式 B: 使用雲端 AI 模型（選一個）

**選項 1: Qwen 2.5（推薦 - 最快）**

1. 訪問 [阿里巴巴 DashScope](https://dashscope.console.aliyun.com/)
2. 登錄或註冊賬戶
3. 創建 API 密鑰
4. 複製密鑰到 `.env`:

```env
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

**選項 2: GPT-4V（最精準）**

1. 訪問 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 創建 API 密鑰
3. 複製到 `.env`:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

**選項 3: Claude 3 Vision（全面分析）**

1. 訪問 [Anthropic Console](https://console.anthropic.com/)
2. 創建 API 密鑰
3. 複製到 `.env`:

```env
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

**模型對比表：**

| 特性 | Ollama | Qwen | GPT-4V | Claude |
|------|--------|------|--------|--------|
| 成本 | 💰 免費 | 💰 便宜 | 💵 中等 | 💵 中等 |
| 隱私 | 🔐 完全 | ❌ 雲端 | ❌ 雲端 | ❌ 雲端 |
| 離線 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 |
| 速度 | ⚡ 快 | ⚡ 快 | ⚡ 中等 | ⚡⚡ 快 |
| 準確度 | 🎯 良好 | 🎯 優秀 | 🎯 最佳 | 🎯 優秀 |

**推薦組合：** Ollama 作為主要 + Qwen 作為備選

### 步驟 6: 啟動後端服務

**方法 1: 使用 Python 腳本（推薦）**

```bash
# 從項目根目錄
cd ..
python run_dev.py
```

**方法 2: 直接運行 Flask**

```bash
cd backend
python app.py
```

**方法 3: 使用 Shell 腳本 (macOS/Linux)**

```bash
./run_dev.sh
```

**預期輸出：**
```
WARNING in app.run_simple ...
 * Serving Flask app ...
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### 驗證後端正常運行

在新的終端窗口打開：

```bash
# 方法 1: 使用 curl
curl http://localhost:5000/health

# 方法 2: 訪問瀏覽器
# 打開 http://localhost:5000/health
```

**成功回應：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00.000000",
  "version": "1.0.0"
}
```

---

## Chrome 擴展安裝

### 步驟 1: 打開開發者模式

1. 打開 Chrome 瀏覽器
2. 訪問 `chrome://extensions/`
3. 在右上角找到「開發者模式」開關
4. **啟用開發者模式**

### 步驟 2: 加載擴展

1. 點擊「加載未打包的擴展程式」按鈕
2. 導航到 `Capstone/chrome-extension` 文件夾
3. 選擇該文件夾
4. 點擊「選擇文件夾」

### 步驟 3: 驗證安裝

- 擴展應該出現在 `chrome://extensions/` 列表中
- 名稱: "校務系統AI助手"
- 狀態應該是「啟用」

---

## 配置和使用

### 首次配置

1. 點擊 Chrome 工具欄中的擴展圖標
2. 彈窗會出現「校務系統AI助手」
3. 點擊「⚙️ 設定」按鈕
4. 填入以下信息：
   - **API 網址**: `http://localhost:5000`
   - **AI 模型**: 選擇你配置的模型（Qwen/GPT/Claude）
5. 點擊「保存設定」

### 使用流程

#### 快速方式（推薦）
1. 在任何網頁上按 **Alt+A**
2. 側邊欄會在右側打開
3. 點擊「📸 截圖」
4. 輸入你的問題
5. 點擊「發送」

#### 完整方式
1. 點擊工具欄的擴展圖標
2. 點擊「啟動助手」
3. 按上述步驟 3-5

### 範例使用場景

**場景 1: 不知道如何修改選課**

```
問題: 我想添加新的課程到我的選課清單，怎麼做？
[截圖選課頁面]
發送 → AI 會分析截圖並提供步驟指引
```

**場景 2: 找不到成績查詢**

```
問題: 我在哪裡可以查看我的期末成績？
[截圖校務系統首頁]
發送 → AI 會告訴你具體位置和操作步驟
```

---

## 故障排除

### 問題 1: 後端啟動失敗

**錯誤信息:**
```
ModuleNotFoundError: No module named 'flask'
```

**解決方案:**
```bash
# 確保已激活虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate.bat # Windows

# 重新安裝依賴
pip install -r requirements.txt
```

### 問題 2: 端口已被占用

**錯誤信息:**
```
OSError: [Errno 48] Address already in use
```

**解決方案:**

**macOS/Linux:**
```bash
# 查找占用 5000 端口的進程
lsof -i :5000

# 殺死該進程
kill -9 <PID>
```

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 問題 3: 無法連接到 API

**症狀:** 提示「發送失敗」或「無法連接」

**檢查清單:**
- [ ] 後端服務正在運行 (終端有 "Running on" 消息)
- [ ] 擴展設定中的 API 網址正確 (`http://localhost:5000`)
- [ ] 防火牆允許 5000 端口
- [ ] 檢查瀏覽器控制台有無錯誤

**解決方案:**
```bash
# 在新終端測試連接
curl http://localhost:5000/health

# 如果失敗，檢查後端日誌尋找錯誤
```

### 問題 4: 截圖為空

**症狀:** 顯示「截圖失敗」

**解決方案:**
- 確保頁面完全加載
- 嘗試重新截圖
- 檢查瀏覽器控制台 (F12) 有無紅色錯誤信息
- 清除瀏覽器快取並重新加載擴展

### 問題 5: AI 回應很慢

**症狀:** 處理時間超過 10 秒

**優化建議:**
- 使用 Qwen 模型（通常最快）
- 檢查網絡連接
- 確保 API 密鑰有效
- 減少截圖大小（擴展會自動縮放 50%）

### 問題 6: API 密鑰錯誤

**錯誤信息:**
```
Invalid API key
Authentication failed
```

**解決方案:**
1. 雙檢查 API 密鑰是否複製正確
2. 確保 `.env` 文件保存了
3. 重啟後端服務 (Ctrl+C 然後重新運行)
4. 檢查 API 密鑰是否已過期或被禁用

---

## 進階配置

### 修改後端端口

編輯 `backend/.env`:

```env
PORT=8000  # 改為 8000
```

然後更新擴展設定中的 API 網址為 `http://localhost:8000`

### 生產部署

**使用 Gunicorn (推薦):**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**使用 Docker:**

```bash
# 構建 Docker 鏡像
docker build -t ncku-ai-assistant .

# 運行容器
docker run -p 5000:5000 --env-file .env ncku-ai-assistant
```

---

## 獲取幫助

如遇到問題，請：

1. 查看 [README.md](README.md) 的常見問題部分
2. 檢查瀏覽器控制台錯誤 (F12)
3. 查看後端日誌輸出
4. 在 GitHub Issues 中提交問題

---

**版本**: 1.0.0  
**最後更新**: 2024 年 10 月 31 日
