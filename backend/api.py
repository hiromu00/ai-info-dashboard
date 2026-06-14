"""
APIルーターモジュール
FastAPIのエンドポイント（/health, /api/news, /api/stats）を定義する
"""
import os
from typing import Optional
from fastapi import APIRouter, Query, Request

from models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """ヘルスチェック & パイプライン状態"""
    news_repo = request.app.state.news_repo
    pipeline_status = request.app.state.pipeline_status

    data = news_repo.load()
    return HealthResponse(
        status="ok",
        pipeline=pipeline_status,
        data_file_exists=os.path.exists(news_repo.data_file),
        total_news_items=len(data),
    )


@router.get("/api/news")
async def get_news(
    request: Request,
    category: Optional[str] = Query(None, description="カテゴリでフィルタ"),
    search: Optional[str] = Query(None, description="キーワード検索"),
    limit: int = Query(100, ge=1, le=500, description="最大件数"),
):
    """ニュースデータを取得する"""
    news_repo = request.app.state.news_repo
    data = news_repo.load()

    items = [item.model_dump() for item in data]

    # カテゴリフィルタ
    if category:
        items = [item for item in items if item.get("category", "").lower() == category.lower()]

    # キーワード検索
    if search:
        search_lower = search.lower()
        items = [
            item for item in items
            if search_lower in item.get("title", "").lower()
            or search_lower in item.get("source", "").lower()
            or search_lower in item.get("summary", "").lower()
        ]

    return items[:limit]


@router.get("/api/stats")
async def get_stats(request: Request):
    """ダッシュボードの統計情報を返す"""
    news_repo = request.app.state.news_repo
    pipeline_status = request.app.state.pipeline_status

    data = news_repo.load()
    categories = {}
    sources = set()
    for item in data:
        cat = item.category
        categories[cat] = categories.get(cat, 0) + 1
        sources.add(item.source)

    return {
        "total": len(data),
        "categories": categories,
        "sources": len(sources),
        "last_updated": pipeline_status.last_run,
        "pipeline_running": pipeline_status.is_running,
    }
