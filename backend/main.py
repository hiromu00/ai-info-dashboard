"""
AI Info Dashboard - メインエントリーポイント
パイプライン（スクレイピング＋要約）と FastAPI サーバーを統合管理する
"""
import asyncio
import os
import json
import time
import threading
import logging
from typing import List, Optional
from datetime import datetime

import schedule
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import config
from models import NewsItem, PipelineStatus, HealthResponse
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

# ── FastAPI アプリ ────────────────────────────────────
app = FastAPI(
    title="AI Info Dashboard API",
    description="AI情報ダッシュボード用バックエンドAPI",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "AI Info Dashboard API is running",
        "docs_url": "/docs",
        "health_check": "/health"
    }


# ── データ永続化 ──────────────────────────────────────
def save_data(data: List[dict]) -> None:
    """ニュースデータをJSONファイルに保存する"""
    try:
        os.makedirs(os.path.dirname(config.data_file), exist_ok=True)
        with open(config.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"データ保存完了: {len(data)}件 → {config.data_file}")
    except Exception as e:
        logger.error(f"データ保存失敗: {e}")


def load_data() -> List[dict]:
    """保存済みニュースデータを読み込む"""
    try:
        with open(config.data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_sources() -> dict:
    """ソース設定をJSONから読み込む"""
    try:
        with open(config.sources_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"{config.sources_file} が見つかりません")
        return {}


def deduplicate_items(items: List[dict]) -> List[dict]:
    """URL をキーにして重複を除去する"""
    seen_urls = set()
    unique = []
    for item in items:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(item)
    return unique


# ── パイプライン処理 ──────────────────────────────────
async def process_rss_source(
    scraper: Scraper, summarizer, source: dict, category: str
) -> List[dict]:
    """RSSソースを処理してニュースアイテムのリストを返す"""
    entries = scraper.fetch_rss(source["url"])
    items = []
    for entry in entries:
        logger.info(f"    エントリ処理中: {entry['title'][:40]}...")
        if summarizer is not None:
            content_to_summarize = f"{entry['title']}\n{entry['summary']}"
            summary = summarizer.summarize_content(content_to_summarize, entry["title"])
        else:
            summary = "要約の生成に失敗しました。"
        items.append({
            "category": category.capitalize(),
            "source": source["name"],
            "title": entry["title"],
            "url": entry["url"],
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        })
    return items


async def process_web_source(
    scraper: Scraper, summarizer, source: dict, category: str
) -> List[dict]:
    """Webソースを処理してニュースアイテムのリストを返す"""
    content = await scraper.fetch_web_content(source["url"])
    if len(content) > 500:
        if summarizer is not None:
            summary = summarizer.summarize_content(
                content, f"{source['name']} 最新情報"
            )
        else:
            summary = "要約の生成に失敗しました。"
        return [{
            "category": category.capitalize(),
            "source": source["name"],
            "title": f"{source['name']} 最新情報",
            "url": source["url"],
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }]
    logger.warning(f"  コンテンツが短すぎます ({len(content)}文字): {source['name']}")
    return []


async def run_pipeline() -> None:
    """
    メインパイプライン
    全ソースからスクレイピング→要約→保存を実行する
    """
    global pipeline_status
    pipeline_status.is_running = True
    pipeline_status.error = None
    logger.info("=" * 60)
    logger.info("パイプライン開始")
    logger.info("=" * 60)

    scraper = Scraper()
    summarizer = None
    try:
        summarizer = Summarizer()
    except ValueError as e:
        logger.error(f"Summarizer 初期化失敗: {e}")
        logger.warning("要約なしモードで続行します（タイトルのみ保存）")
        pipeline_status.error = str(e)

    sources_config = load_sources()
    all_news: List[dict] = []

    for category, sources in sources_config.items():
        logger.info(f"カテゴリ処理中: {category}")
        for source in sources:
            logger.info(f"  ソース: {source['name']} ({source['type']})")
            try:
                if source["type"] == "rss":
                    new_items = await process_rss_source(
                        scraper, summarizer, source, category
                    )
                elif source["type"] == "web":
                    new_items = await process_web_source(
                        scraper, summarizer, source, category
                    )
                else:
                    logger.warning(f"  未知のソースタイプ: {source['type']}")
                    continue

                if new_items:
                    all_news.extend(new_items)
                    # 逐次保存（途中でクラッシュしてもデータが残る）
                    save_data(deduplicate_items(all_news))
                    logger.info(f"    → {len(new_items)}件を保存")

            except Exception as e:
                logger.error(f"  ソース処理エラー ({source['name']}): {e}")
                # 次のソースに続行

    # 最終保存（重複排除済み）
    all_news = deduplicate_items(all_news)
    if all_news:
        save_data(all_news)

    # ステータス更新
    failed = sum(1 for item in all_news if "失敗" in item.get("summary", ""))
    pipeline_status.is_running = False
    pipeline_status.last_run = datetime.now().isoformat()
    pipeline_status.total_items = len(all_news)
    pipeline_status.failed_summaries = failed

    logger.info("=" * 60)
    logger.info(f"パイプライン完了: {len(all_news)}件 (要約失敗: {failed}件)")
    logger.info("=" * 60)


def run_pipeline_sync() -> None:
    """パイプラインを同期的に実行する（スケジューラ用）"""
    asyncio.run(run_pipeline())


# ── API エンドポイント ────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """ヘルスチェック & パイプライン状態"""
    data = load_data()
    return HealthResponse(
        status="ok",
        pipeline=pipeline_status,
        data_file_exists=os.path.exists(config.data_file),
        total_news_items=len(data),
    )


@app.get("/api/news")
async def get_news(
    category: Optional[str] = Query(None, description="カテゴリでフィルタ"),
    search: Optional[str] = Query(None, description="キーワード検索"),
    limit: int = Query(100, ge=1, le=500, description="最大件数"),
):
    """ニュースデータを取得する"""
    data = load_data()

    # カテゴリフィルタ
    if category:
        data = [item for item in data if item.get("category", "").lower() == category.lower()]

    # キーワード検索
    if search:
        search_lower = search.lower()
        data = [
            item for item in data
            if search_lower in item.get("title", "").lower()
            or search_lower in item.get("source", "").lower()
            or search_lower in item.get("summary", "").lower()
        ]

    return data[:limit]


@app.get("/api/stats")
async def get_stats():
    """ダッシュボードの統計情報を返す"""
    data = load_data()
    categories = {}
    sources = set()
    for item in data:
        cat = item.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
        sources.add(item.get("source", ""))

    return {
        "total": len(data),
        "categories": categories,
        "sources": len(sources),
        "last_updated": pipeline_status.last_run,
        "pipeline_running": pipeline_status.is_running,
    }


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
