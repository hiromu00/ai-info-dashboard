"""
スクレイピングモジュール
RSS フィードと Web ページからコンテンツを取得する
"""
import logging
import feedparser
from crawl4ai import AsyncWebCrawler
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config

logger = logging.getLogger(__name__)

# feedparser のネットワーク系エラー
RETRIABLE_EXCEPTIONS = (Exception,)


class Scraper:
    """情報ソースからコンテンツを取得するクラス"""

    def __init__(self):
        self._user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def fetch_rss(self, url: str) -> List[Dict]:
        """
        RSSフィードを取得してエントリのリストを返す

        Args:
            url: RSSフィードのURL

        Returns:
            エントリのリスト（タイトル、URL、要約、公開日）
        """
        logger.info(f"RSS取得中: {url}")
        feed = feedparser.parse(url, agent=self._user_agent)

        if feed.bozo and not feed.entries:
            logger.warning(f"RSSパースエラー: {url} - {feed.bozo_exception}")
            return []

        entries = []
        max_entries = config.rss_max_entries
        for entry in feed.entries[:max_entries]:
            entries.append({
                "title": getattr(entry, "title", "タイトル不明"),
                "url": getattr(entry, "link", ""),
                "summary": getattr(entry, "summary", ""),
                "published": getattr(entry, "published", ""),
            })

        logger.info(f"  → {len(entries)}件のエントリを取得")
        return entries

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=3, max=15),
        reraise=True,
    )
    async def fetch_web_content(self, url: str) -> str:
        """
        Webページのコンテンツを Crawl4AI で取得する

        Args:
            url: 取得対象のURL

        Returns:
            Markdown形式のページコンテンツ
        """
        logger.info(f"Webクロール中: {url}")
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
                content = result.markdown or ""
                logger.info(f"  → {len(content)}文字のコンテンツを取得")
                return content
        except Exception as e:
            logger.error(f"Webクロール失敗 ({url}): {e}")
            raise

    async def scrape_multiple_web(self, urls: List[str]) -> List[Dict]:
        """
        複数のWebページを取得する

        Args:
            urls: 取得対象のURLリスト

        Returns:
            URL とコンテンツのリスト
        """
        results = []
        for url in urls:
            try:
                content = await self.fetch_web_content(url)
                results.append({"url": url, "content": content})
            except Exception as e:
                logger.error(f"スクレイピングエラー ({url}): {e}")
        return results
