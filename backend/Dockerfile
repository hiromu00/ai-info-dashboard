# ── ビルド/インストールステージ ──────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ── 実行用ステージ ──────────────────────────────────
FROM python:3.11-slim AS runner

WORKDIR /app

# Playwright実行に必要なランタイム依存関係とcurlをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# builderステージからインストールしたライブラリをコピー
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Playwrightのブラウザおよびそのシステム依存関係をインストール
RUN playwright install --with-deps chromium && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# FastAPI ポートを公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
