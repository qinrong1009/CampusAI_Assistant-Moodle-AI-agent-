# 🚀 本地 Qwen2.5 快速指南

## 📋 概要

您現在可以使用 **完全本地的 Ollama 運行 Qwen2.5**，無需任何 API 密鑰或雲端連接！

---

## 🎯 支持的本地模型

| 模型 | 大小 | 用途 | 命令 |
|------|------|------|------|
| **LLaVA** | 6.3GB | 視覺分析（圖片） | `ollama pull llava` |
| **Qwen 2.5** | 3.5GB | 多功能、快速 | `ollama pull qwen2.5` |
| **BakLLaVA** | 3.9GB | 輕量視覺 | `ollama pull bakllava` |

---

## 📥 安裝 Qwen2.5

### 步驟 1：下載 Qwen2.5

```bash
# 確保 Ollama 已啟動
ollama serve

# 在新終端下載 Qwen2.5
ollama pull qwen2.5

# 等待下載完成 (~3-5GB)
```

### 步驟 2：驗證安裝

```bash
# 查看已安裝的模型
ollama list

# 應該看到:
# qwen2.5:latest    ...
# llava:latest      ... (如果已安裝)
```

### 步驟 3：配置後端

```bash
# 編輯 backend/.env
nano backend/.env

# 確保配置如下:
OLLAMA_ENABLED=true
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llava  # 默認使用 LLaVA，也可改成 qwen2.5
```

---

## ✨ 使用方式

### 方式 1：在設定中選擇

1. 在網頁上按 **Alt+A** 啟動助手
2. 點擊「⚙️ 設定」
3. 模型選擇中選擇：
   - **🖥️ LLaVA** - 視覺分析（推薦用於圖片）
   - **🖥️ Qwen 2.5** - 多功能分析（推薦用於文本）
   - **🖥️ BakLLaVA** - 輕量版（推薦用於 CPU）
4. 點擊「保存設定」

### 方式 2：設置默認模型

```bash
# 編輯 backend/.env
OLLAMA_MODEL=qwen2.5  # 設置 Qwen2.5 為默認

# 重啟後端
python run_dev.py
```

---

## 🎯 何時使用哪個模型？

| 場景 | 推薦模型 | 原因 |
|------|---------|------|
| **查詢校務系統功能** | LLaVA | 需要理解界面布局 |
| **分析系統消息** | Qwen 2.5 | 文本理解能力強 |
| **查詢流程步驟** | Qwen 2.5 | 邏輯推理好 |
| **設備性能有限** | BakLLaVA | 更輕量、更快 |

---

## ⚡ 性能對比

### 響應時間

| 模型 | GPU (V100) | M1/M2 Mac | CPU (i7) |
|------|-----------|----------|----------|
| **LLaVA** | 2-3 秒 | 8-10 秒 | 20-30 秒 |
| **Qwen 2.5** | 1-2 秒 | 5-8 秒 | 15-20 秒 |
| **BakLLaVA** | 1-2 秒 | 3-5 秒 | 10-15 秒 |

### 資源占用

| 模型 | VRAM | RAM |
|------|------|-----|
| **LLaVA** | 4GB | 4GB |
| **Qwen 2.5** | 2-3GB | 3GB |
| **BakLLaVA** | 2GB | 3GB |

---

## 🔍 測試 Qwen2.5

### 快速測試

```bash
# 直接調用 Qwen2.5
curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "qwen2.5",
    "prompt": "你好，請介紹一下 Qwen2.5 模型",
    "stream": false
  }'
```

### 通過後端測試

```bash
# 後端應已啟動，發送測試請求
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "這是什麼系統？",
    "image": "data:image/png;base64,...",
    "model_type": "qwen2.5"
  }'
```

---

## 🔧 常見問題

### Q1：Qwen2.5 下載失敗怎麼辦？

```bash
# 檢查網絡連接
# 重試下載
ollama pull qwen2.5

# 如果還是失敗，嘗試輕量版
ollama pull bakllava
```

### Q2：Qwen2.5 響應很慢？

```bash
# 檢查是否有其他程式占用 GPU
# 或嘗試輕量版
OLLAMA_MODEL=bakllava

# 或減少並發
export OLLAMA_NUM_PARALLEL=1
```

### Q3：如何切換模型？

```bash
# 方式 1：通過 UI 設定
# Alt+A → 設定 → 選擇模型

# 方式 2：編輯 .env
OLLAMA_MODEL=qwen2.5
# 然後重啟後端

# 方式 3：通過 API 指定
# 發送請求時設置 model_type
```

### Q4：可以同時運行多個模型嗎？

```bash
# 可以，但需要足夠資源
# Ollama 會自動加載/卸載模型

# 控制並發模型數量
export OLLAMA_MAX_LOADED_MODELS=2
```

---

## 📊 推薦配置

### 隱私優先（推薦）

```env
OLLAMA_ENABLED=true
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llava  # 或 qwen2.5
# 不配置任何雲端 API 密鑰
# 完全本地，完全隱私
```

### 多模型混搭

```env
OLLAMA_ENABLED=true
OLLAMA_MODEL=llava

# 支持多個本地模型選擇
# LLaVA (視覺)
# Qwen 2.5 (文本)
# BakLLaVA (輕量)
```

### 保留雲端備選（可選）

```env
OLLAMA_ENABLED=true
OLLAMA_MODEL=llava

# 可選：如果想要雲端備選
OPENAI_API_KEY=sk-xxx  # 備選用 GPT-4V
```

---

## 🎉 完成檢查

- [ ] Ollama 已安裝
- [ ] Qwen2.5 已下載 (`ollama list` 中可見)
- [ ] Ollama 正在運行 (`ollama serve`)
- [ ] 後端已配置 (OLLAMA_ENABLED=true)
- [ ] 後端已啟動 (`python run_dev.py`)
- [ ] Chrome 擴展已加載
- [ ] 設定中可以選擇 Qwen 2.5
- [ ] 测试成功

---

## 📖 相關文檔

- **快速開始**: QUICKSTART.md
- **安裝指南**: OLLAMA_SETUP.md
- **使用手冊**: USAGE.md
- **故障排除**: OLLAMA_SETUP.md (故障排除部分)

---

## 🚀 立即開始

1. **下載 Qwen2.5**
   ```bash
   ollama pull qwen2.5
   ```

2. **啟動 Ollama**
   ```bash
   ollama serve
   ```

3. **啟動後端**
   ```bash
   python run_dev.py
   ```

4. **測試**
   - 在網頁上按 Alt+A
   - 設定中選擇 Qwen 2.5
   - 提問測試

**享受本地 Qwen2.5！** 🎊
