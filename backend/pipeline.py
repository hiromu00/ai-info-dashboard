"""
パイプライン処理モジュール
全ソースからのスクレイピングと要約、データの保存を実行する
"""
import logging
from datetime import datetime
from typing import List

from config import config
from models import NewsItem, PipelineStatus, RSSEntry, SourceConfig
from repository import NewsRepository, SourceRepository
from scraper import Scraper
from summarizer import Summarizer

logger = logging.getLogger(__name__)


class Pipeline:
    """スクレイピング、要約、保存を行うメインパイプラインクラス"""

    def __init__(
        self,
        news_repo: NewsRepository,
        source_repo: SourceRepository,
        scraper: Scraper,
        summarizer: Summarizer,
        status: PipelineStatus,
    ):
        self.news_repo = news_repo
        self.source_repo = source_repo
        self.scraper = scraper
        self.summarizer = summarizer
        self.status = status

    async def run(self) -> None:
        """
        メインパイプライン
        全ソースからスクレイピング→要約→保存を実行する
        """
        self.status.is_running = True
        self.status.error = None
        logger.info("=" * 60)
        logger.info("パイプライン開始")
        logger.info("=" * 60)

        sources_config = self.source_repo.load()
        # 既存のデータをロードして保持
        all_news: List[NewsItem] = self.news_repo.load()

        for category, sources in sources_config.items():
            logger.info(f"カテゴリ処理中: {category}")
            for source in sources:
                logger.info(f"  ソース: {source.name} ({source.type})")
                try:
                    new_items = []
                    if source.type == "rss":
                        new_items = await self._process_rss_source(source, category)
                    elif source.type == "web":
                        new_items = await self._process_web_source(source, category)
                    else:
                        logger.warning(f"  未知のソースタイプ: {source.type}")
                        continue

                    if new_items:
                        # 新しいアイテムを先頭に追加して重複排除
                        all_news = self.news_repo.deduplicate(new_items + all_news)
                        # 最大件数を制限（履歴が無限に増えるのを防ぐ）
                        all_news = all_news[:config.max_news_items]
                        # 逐次保存（途中でクラッシュしてもデータが残る）
                        self.news_repo.save(all_news)
                        logger.info(f"    → {len(new_items)}件を保存")

                except Exception as e:
                    logger.error(f"  ソース処理エラー ({source.name}): {e}")
                    # 次のソースに続行

        # 最終保存（重複排除と件数制限）
        all_news = self.news_repo.deduplicate(all_news)[:config.max_news_items]
        if all_news:
            self.news_repo.save(all_news)

        # ステータス更新
        failed = sum(1 for item in all_news if item.is_summary_failed)
        self.status.is_running = False
        self.status.last_run = datetime.now().isoformat()
        self.status.total_items = len(all_news)
        self.status.failed_summaries = failed

        logger.info("=" * 60)
        logger.info(f"パイプライン完了: {len(all_news)}件 (要約失敗: {failed}件)")
        logger.info("=" * 60)

    async def _process_rss_source(self, source: SourceConfig, category: str) -> List[NewsItem]:
        """RSSソースを処理してニュースアイテムのリストを返す"""
        entries = await self.scraper.fetch_rss(source.url)
        items = []
        for entry_data in entries:
            # 辞書またはRSSEntryの両方に対応
            if isinstance(entry_data, dict):
                entry = RSSEntry(**entry_data)
            else:
                entry = entry_data

            logger.info(f"    エントリ処理中: {entry.title[:40]}...")
            if self.summarizer is not None and not self.summarizer.disabled:
                content_to_summarize = f"{entry.title}\n{entry.summary}"
                summary = self.summarizer.summarize_content(content_to_summarize, entry.title)
            else:
                summary = "要約の生成に失敗しました。"
            
            items.append(NewsItem.from_rss_entry(entry, source.name, category, summary))
        return items

    async def _process_web_source(self, source: SourceConfig, category: str) -> List[NewsItem]:
        """Webソースを処理してニュースアイテムのリストを返す"""
        content = await self.scraper.fetch_web_content(source.url)
        if len(content) > config.min_web_content_chars:
            title = f"{source.name} 最新情報"
            if self.summarizer is not None and not self.summarizer.disabled:
                summary = self.summarizer.summarize_content(content, title)
            else:
                summary = "要約の生成に失敗しました。"
            
            return [NewsItem.from_web_content(
                source_name=source.name,
                category=category,
                title=title,
                url=source.url,
                summary=summary
            )]
        logger.warning(f"  コンテンツが短すぎます ({len(content)}文字): {source.name}")
        return []
