# 校務系統 AI 助手 - 完整安裝檢查清單

## ✅ 安裝前檢查

### 系統要求
- [ ] Python 3.8+ 已安裝
- [ ] Chrome 瀏覽器已安裝
- [ ] pip (Python 包管理器) 可用
- [ ] 終端/命令行可用

### API 密鑰準備
- [ ] 選擇了 AI 模型 (Qwen/GPT/Claude)
- [ ] 獲得了相應的 API 密鑰
- [ ] 密鑰格式正確且有效

---

## 📦 後端安裝檢查

### Python 環境
```bash
# ✅ 檢查 Python 版本
python --version  # 應返回 3.8+

# ✅ 檢查 pip
pip --version

# ✅ 進入後端目錄
cd backend
```

### 創建虛擬環境
```bash
# macOS/Linux
source venv/bin/activate  # 提示符應顯示 (venv)
# 或
python3 -m venv venv && source venv/bin/activate

# Windows
venv\Scripts\activate.bat  # 提示符應顯示 (venv)
```

### 安裝依賴
```bash
# ✅ 安裝 requirements.txt
pip install -r requirements.txt

# ✅ 驗證安裝
pip list | grep flask  # 應返回 Flask 3.0.0+
```

### 配置環境變數
```bash
# ✅ 複製示例文件
cp .env.example .env

# ✅ 編輯 .env
nano .env  # 或 vim, notepad 等

# ✅ 填入 API 密鑰 (3 選 1)
# - QWEN_API_KEY=your_key
# - OPENAI_API_KEY=your_key  
# - CLAUDE_API_KEY=your_key
```

### 測試後端啟動
```bash
# ✅ 啟動應用
python app.py

# 看到類似輸出表示成功:
# Running on http://127.0.0.1:5000
```

### 驗證後端功能
```bash
# ✅ 新開終端運行健康檢查
curl http://localhost:5000/health

# 預期返回 (HTTP 200):
# {"status": "healthy", "version": "1.0.0", ...}

# ✅ 檢查模型列表
curl http://localhost:5000/api/models

# ✅ 測試端點
curl http://localhost:5000/api/test
```

---

## 🎨 Chrome 擴展安裝檢查

### 檔案結構驗證
```
chrome-extension/
├── manifest.json              # ✅ 必須存在
├── src/
│   ├── html/
│   │   ├── popup.html         # ✅ 必須存在
│   │   └── sidebar.html       # ✅ 必須存在
│   ├── css/
│   │   ├── popup.css          # ✅ 必須存在
│   │   └── sidebar.css        # ✅ 必須存在
│   └── js/
│       ├── background.js      # ✅ 必須存在
│       ├── content.js         # ✅ 必須存在
│       ├── popup.js           # ✅ 必須存在
│       └── sidebar.js         # ✅ 必須存在
```

### Chrome 安裝步驟
```
1. ✅ 打開 Chrome 瀏覽器
2. ✅ 訪問 chrome://extensions/
3. ✅ 右上角打開「開發者模式」
4. ✅ 點擊「加載未打包的擴展程式」
5. ✅ 選擇 Capstone/chrome-extension 文件夾
6. ✅ 出現「校務系統AI助手」擴展
```

### 擴展驗證
```
確認以下內容出現:
✅ 擴展名稱: 「校務系統AI助手」
✅ 版本: 1.0.0
✅ 狀態: 已啟用 (藍色開關)
✅ 圖標: 出現在工具欄
✅ 無錯誤提示
```

---

## 🔧 配置驗證

### Chrome 擴展設定
```
1. ✅ 點擊擴展圖標 (工具欄)
2. ✅ 看到彈窗 (「啟動助手」按鈕)
3. ✅ 點擊設定 (⚙️ 按鈕)
4. ✅ API 網址: http://localhost:5000
5. ✅ AI 模型: 與後端配置一致
```

### 快捷鍵配置
```
驗證快捷鍵設定:
- Windows/Linux: Alt+A
- macOS: Command+Shift+A

如需修改:
1. Chrome 進入 chrome://extensions/
2. 點擊「鍵盤快捷鍵」
3. 找到「校務系統AI助手」
4. 修改快捷鍵
```

---

## 🧪 功能測試

### 測試項目清單

#### 1️⃣ 擴展啟動
- [ ] 快捷鍵可以打開側邊欄 (Alt+A)
- [ ] 點擊圖標可以打開彈窗
- [ ] 彈窗「啟動助手」按鈕可工作
- [ ] 側邊欄可以關閉

#### 2️⃣ 截圖功能
- [ ] 點擊「📸 截圖」按鈕
- [ ] 看到「截圖中...」提示
- [ ] 截圖預覽出現
- [ ] 可以「重新截圖」

#### 3️⃣ 提問功能
- [ ] 可以在文本框輸入問題
- [ ] 字數統計正常工作
- [ ] 輸入問題後「發送」按鈕啟用
- [ ] 未截圖時「發送」按鈕禁用

#### 4️⃣ AI 回應
- [ ] 點擊「發送」後顯示加載動畫
- [ ] 2-5 秒後收到 AI 回應
- [ ] 回應文本正確顯示
- [ ] 可以「清除」結果
- [ ] 可以進行新的提問

#### 5️⃣ 設定保存
- [ ] 修改 API 網址
- [ ] 修改 AI 模型
- [ ] 點擊保存
- [ ] 刷新後設定保留

---

## 🐛 問題排查

### 問題 1: 後端無法啟動

```bash
# ❌ 症狀: "ModuleNotFoundError: No module named 'flask'"

# ✅ 解決:
source venv/bin/activate  # 確保虛擬環境激活
pip install -r requirements.txt
python app.py
```

### 問題 2: 端口已被占用

```bash
# ❌ 症狀: "Address already in use"

# ✅ 解決 (macOS/Linux):
lsof -i :5000  # 找出佔用進程
kill -9 <PID>

# 或改變端口:
PORT=5001 python app.py
# 然後在擴展設定中修改為 http://localhost:5001
```

### 問題 3: Chrome 擴展不出現

```
❌ 症狀: 工具欄沒看到圖標

✅ 解決:
1. 進入 chrome://extensions/
2. 檢查「開發者模式」是否開啟
3. 重新加載擴展 (刷新按鈕)
4. 清除 Chrome 快取 (Ctrl+Shift+Delete)
5. 重新加載擴展
```

### 問題 4: 截圖失敗

```
❌ 症狀: 點擊截圖後沒反應或報錯

✅ 解決:
1. 檢查瀏覽器控制台 (F12)
2. 確保頁面完全加載
3. 嘗試刷新頁面
4. 檢查 html2canvas CDN 是否可訪問
```

### 問題 5: API 連接失敗

```bash
# ❌ 症狀: "Error: API 連接失敗" 或 "Cannot reach server"

# ✅ 排查步驟:
1. 檢查後端是否運行:
   curl http://localhost:5000/health

2. 如果無響應，後端可能未啟動:
   python app.py  # 在 backend 目錄

3. 檢查防火牆設定:
   - Windows: 允許 Python 通過防火牆
   - macOS: 系統偏好設定 > 安全性與隱私

4. 檢查 API 網址設定:
   - 擴展設定中應該是 http://localhost:5000
```

### 問題 6: API 密鑰無效

```
❌ 症狀: "API 密鑰錯誤" 或 "Authentication failed"

✅ 解決:
1. 檢查 .env 文件中的密鑰
2. 確保密鑰沒有多餘空格
3. 驗證密鑰還未過期
4. 嘗試更新密鑰
```

---

## 📊 驗收測試

### 完整流程測試

```
1. ✅ 導航到校務系統頁面 (例如選課系統)
2. ✅ 按 Alt+A 打開 AI 助手
3. ✅ 點擊「📸 截圖」
4. ✅ 看到頁面截圖預覽
5. ✅ 在文本框輸入問題: "這個頁面是什麼？"
6. ✅ 點擊「發送」
7. ✅ 看到加載動畫
8. ✅ 2-5 秒後收到 AI 回應
9. ✅ 回應包含有用信息
10. ✅ 可以清除結果並進行新提問
```

### 多模型測試 (如果已配置)

```
# 如果你配置了多個模型:
1. ✅ 打開擴展設定
2. ✅ 切換到 "GPT-4V"
3. ✅ 保存設定
4. ✅ 進行新提問
5. ✅ 驗證使用了不同模型
6. ✅ 切換回 "Qwen 2.5"
7. ✅ 驗證設定保持
```

---

## 🎉 完成檢查清單

### 所有項完成？

如果上述所有檢查都通過了，恭喜！✅ 你的系統已完全就位！

### 現在可以:

- [x] 使用擴展在校務系統中提問
- [x] 自動截圖和分析
- [x] 獲得 AI 智能回應
- [x] 切換不同 AI 模型
- [x] 保存用戶設定
- [x] 離線或在線使用

### 下一步:

1. 📖 閱讀 [使用指南](USAGE.md) 深入瞭解功能
2. 🔧 查看 [開發文檔](DEVELOPMENT.md) 如需自定義
3. 📞 遇到問題查看 [故障排除](SETUP.md#故障排除)

---

## 📞 需要幫助？

- **快速問題**: 查看 [常見問題](README.md#常見問題)
- **詳細問題**: 查看 [故障排除指南](SETUP.md#故障排除)
- **技術細節**: 查看 [架構文檔](ARCHITECTURE.md)
- **開發**: 查看 [開發指南](DEVELOPMENT.md)

---

**完成日期**: _______________  
**系統版本**: 1.0.0  
**狀態**: ✅ 準備投入使用
