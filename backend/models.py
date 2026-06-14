"""
データモデル定義
Pydanticによる型安全なデータ構造
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class SourceConfig(BaseModel):
    """情報ソースの設定"""
    type: Literal["rss", "web"]
    url: str
    name: str


class RSSEntry(BaseModel):
    """RSS フィードのエントリ"""
    title: str
    url: str
    summary: str = ""
    published: str = ""


class NewsItem(BaseModel):
    """ニュース記事モデル"""
    category: str
    source: str
    title: str
    url: str
    summary: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @property
    def is_summary_failed(self) -> bool:
        """要約が失敗しているか判定"""
        return self.summary in ("要約の生成に失敗しました。", "", "(要約の生成に失敗しました)")

    @classmethod
    def from_rss_entry(cls, entry: RSSEntry, source_name: str, category: str, summary: str) -> "NewsItem":
        """RSSEntryからNewsItemを生成する"""
        return cls(
            category=category.capitalize(),
            source=source_name,
            title=entry.title,
            url=entry.url,
            summary=summary,
        )

    @classmethod
    def from_web_content(cls, source_name: str, category: str, title: str, url: str, summary: str) -> "NewsItem":
        """WebコンテンツからNewsItemを生成する"""
        return cls(
            category=category.capitalize(),
            source=source_name,
            title=title,
            url=url,
            summary=summary,
        )


class PipelineStatus(BaseModel):
    """パイプラインの実行状態"""
    is_running: bool = False
    last_run: Optional[str] = None
    total_items: int = 0
    failed_summaries: int = 0
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str = "ok"
    pipeline: PipelineStatus = Field(default_factory=PipelineStatus)
    data_file_exists: bool = False
    total_news_items: int = 0
