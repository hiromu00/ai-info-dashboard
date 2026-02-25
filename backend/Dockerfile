FROM python:3.11-slim

WORKDIR /app

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    build-essential \
    git \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright ブラウザのインストール
RUN playwright install --with-deps chromium

COPY . .

# FastAPI ポートを公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
