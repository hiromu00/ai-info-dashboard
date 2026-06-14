"""
AI Info Dashboard - メインエントリーポイント
FastAPI サーバーと定期実行スケジューラを管理する
"""
import asyncio
import logging
import threading
import time

import schedule
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router
from config import config
from models import PipelineStatus
from pipeline import Pipeline
from repository import NewsRepository, SourceRepository
from scraper import Scraper
from summarizer import Summarizer

# ── ログ設定 ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── グローバル状態 ────────────────────────────────────
pipeline_status = PipelineStatus()

# ── リポジトリ & インスタンス初期化 ─────────────────────
news_repo = NewsRepository()
source_repo = SourceRepository()
scraper = Scraper()
summarizer = None
try:
    summarizer = Summarizer()
except ValueError as e:
    logger.error(f"Summarizer 初期化失敗: {e}")
    logger.warning("要約なしモードで続行します（タイトルのみ保存）")
    pipeline_status.error = str(e)

pipeline = Pipeline(
    news_repo=news_repo,
    source_repo=source_repo,
    scraper=scraper,
    summarizer=summarizer,
    status=pipeline_status,
)

# ── FastAPI アプリ ────────────────────────────────────
app = FastAPI(
    title="AI Info Dashboard API",
    description="AI情報ダッシュボード用バックエンドAPI",
    version="1.0.0",
)

# app.state に共有インスタンスを設定（API側で参照可能にする）
app.state.news_repo = news_repo
app.state.pipeline_status = pipeline_status

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(api_router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "AI Info Dashboard API is running",
        "docs_url": "/docs",
        "health_check": "/health"
    }


def run_pipeline_sync() -> None:
    """パイプラインを同期的に実行する（スケジューラ用）"""
    asyncio.run(pipeline.run())


# ── エントリーポイント ──────────────────────────────────
def start_scheduler():
    """スケジューラをバックグラウンドスレッドで起動する"""
    logger.info(f"デーモンモード: {config.schedule_interval_hours}時間ごとに実行")
    schedule.every(config.schedule_interval_hours).hours.do(run_pipeline_sync)

    # 初回実行
    run_pipeline_sync()

    # スケジューラループ
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    mode = config.run_mode

    if mode == "daemon":
        logger.info("起動モード: DAEMON（API + スケジューラ）")

        # スケジューラをバックグラウンドスレッドで実行
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()

        # FastAPI サーバーを起動
        uvicorn.run(app, host=config.api_host, port=config.api_port)
    else:
        logger.info("起動モード: ONESHOT")
        run_pipeline_sync()
