<div align="center">

# CampusAI Assistant Local

🚀 全本地、支援視覺 + 文字、多模型切換的校務系統 AI 助手 —— 幫助師生更快理解介面與操作流程。

</div>

## 目錄

1. 簡介  
2. 核心特性  
3. 架構概覽  
4. 快速開始 (5 分鐘)  
5. 安裝與設定  
6. 使用流程  
7. API 端點  
8. 檔案結構  
9. 開發指引  
10. 測試與驗證  
11. 部署 (本地 / Docker)  
12. Roadmap  
13. 常見問題  
14. 貢獻與授權  
15. 延伸建議  

---

## 1. 簡介

CampusAI Assistant Local 是一個結合 Chrome 擴展 + Flask 後端 + 視覺/語言推理的智能助手。支援：

- 本地 Ollama 視覺/多模態模型（LLaVA / BakLLaVA / Qwen 系列）
- 雲端備選（GPT-4V、Claude 3 Vision）
- 輕量級知識檢索（`knowledge_base.json` 關鍵字 → Prompt 增強）
- 校務常見操作諮詢（選課、成績、課表、教室預約等）

所有截圖與內容可在本機完成推理，提高隱私安全性。

---

## 2. 核心特性

| 類型 | 說明 |
|------|------|
| 本地推理 | Ollama + 視覺模型（無 API 密鑰，離線可用） |
| 多模型切換 | llava / bakllava / qwen2.5 / gpt / claude |
| 截圖理解 | 擴展自動截圖 → 視覺 + 語言聯合推理 |
| Prompt 增強 | 關鍵字檢索（可替換向量資料庫） |
| API First | 清晰的 REST 端點設計 |
| 隱私優先 | 可完全拒絕雲端模型使用 |
| 擴展性 | 模型與檢索器抽象，易於替換 |

---

## 3. 架構概覽

```text
Chrome Extension
    ├─ 截圖 (html2canvas)
    ├─ 問題輸入
    └─ 呼叫後端 /api/ask
               ↓
Flask Backend
    ├─ 路由層 api_routes.py
    ├─ 檢索 LightweightRetriever (keywords)
    ├─ 模型調度 AIModel (Ollama / Cloud)
    └─ 回傳答案 JSON
               ↓
使用者畫面側邊欄顯示回應
```

資料流：`問題 + 截圖` → `檢索上下文` → `組合 Prompt` → 模型生成 → 回應。

---

## 4. 快速開始（5 分鐘）

```bash
# 1. 取得專案
git clone <your-repo-url>
cd Capstone

# 2. 啟動 Ollama 並拉模型（推薦 llava）
ollama pull llava
ollama serve &

# 3. 安裝後端依賴
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 4. 啟動後端
python app.py  # 或 python ../run_dev.py

# 5. 安裝 Chrome 擴展
# Chrome → chrome://extensions → 開發者模式 → 加載未打包 → 選擇 chrome-extension/
```

驗證：
```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/models
```

---

## 5. 安裝與設定

`.env` 範例：
```
PORT=5000
OLLAMA_ENABLED=true
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llava
QWEN_API_KEY= # 可選
OPENAI_API_KEY= # 可選
CLAUDE_API_KEY= # 可選
```

前端請求中的 `model` 可用：`llava` / `bakllava` / `qwen2.5` / `gpt` / `claude`。

---

## 6. 使用流程

1. 啟動後端與擴展。  
2. 任意校務網頁上按 `Alt+A` 或點擴展圖示。  
3. 點「📸 截圖」→ 輸入問題 → 發送。  
4. 2–5 秒內返回回應。  

---

## 7. API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/health` | 健康檢查 |
| GET | `/api/models` | 可用模型列表 |
| POST | `/api/ask` | 問答（核心端點） |
| POST | `/api/analyze` | `/ask` 別名 |
| GET | `/api/test` | 簡單測試 |

請求：
```json
{
   "question": "如何查詢我的選課記錄？",
   "screenshot": "data:image/png;base64,...",
   "model": "llava"
}
```

回應：
```json
{
   "status": "success",
   "response": "在校務系統中請前往...",
   "model": "llava",
   "timestamp": "2025-11-21T12:00:00Z"
}
```

---

## 8. 檔案結構

```text
backend/
   app.py                  # Flask 入口
   config.py               # 配置類
   requirements.txt        # 依賴
   app/
      routes/api_routes.py  # API 路由
      models/
         ai_model.py         # 模型調度
         retriever.py        # 關鍵字檢索
         data_models.py      # 資料結構
      knowledge/knowledge_base.json # 關鍵字片段
chrome-extension/
   manifest.json
   src/js/{popup,sidebar,content,background}.js
   src/html/{popup,sidebar}.html
   src/css/{popup,sidebar}.css
```

---

## 9. 開發指引

```bash
cd backend
source .venv/bin/activate
export FLASK_ENV=development
python app.py
```

Chrome 擴展修改後 → `重新載入`。  
日誌包含：模型呼叫 / 檢索命中 / 錯誤堆疊。  

---

## 10. 測試與驗證

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/models | jq .
```

Python 測試：
```python
import requests, base64
with open("sample.png","rb") as f:
      b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode()
r = requests.post("http://localhost:5000/api/ask", json={
   "question": "這頁面是在做什麼？",
   "screenshot": b64,
   "model": "llava"
})
print(r.json())
```

---

## 11. 部署

Docker：
```bash
docker-compose up --build
```

Production 建議：Nginx 反向代理、HTTPS、日誌輪替、加監控。  

---

## 12. Roadmap

| 狀態 | 項目 | 說明 |
|------|------|------|
| ✅ | 多模型支援 | Ollama + 雲端備選 |
| ✅ | 基礎檢索 | 關鍵字匹配 |
| ⏳ | 向量檢索 | Embedding + 向量資料庫 |
| ⏳ | 角色記憶 | Session 對話上下文 |
| ⏳ | 使用者管理 | Token / Rate Limit |
| ⏳ | 監控儀表 | 延遲 / QPS / 錯誤率 |
| ⏳ | CI/CD | GitHub Actions |
| ⏳ | 英文 README | 雙語文件 |

---

## 13. 常見問題

| 問題 | 排查 |
|------|------|
| Ollama 連不上 | 確認 `ollama serve`、埠 11434 可訪問 |
| 回應很慢 | 換 `bakllava`、縮圖、檢查資源 |
| 模型列表空 | `OLLAMA_ENABLED=true`? 模型已 pull? |
| 擴展不載入 | chrome://extensions 是否正確路徑 |


---

**最後更新**：2025-11-21  

> 歡迎提交 Issue 或 PR。

