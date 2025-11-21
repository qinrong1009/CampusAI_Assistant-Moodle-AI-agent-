# Dockerfile - Docker 容器化部署

FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY backend/requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製後端代碼
COPY backend/ .

# 暴露端口
EXPOSE 5000

# 設置環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# 啟動應用
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
