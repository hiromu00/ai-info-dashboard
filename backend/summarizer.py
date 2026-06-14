"""
要約モジュール
Vertex AI (Gemini) を使用してコンテンツをエンジニア向けに要約する
"""
import os
import time
import logging
import logging
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config

logger = logging.getLogger(__name__)


# API レート制限の設定
RATE_LIMIT_INTERVAL_SEC = 1.0
RATE_LIMIT_BATCH_SIZE = 10
RATE_LIMIT_BATCH_WAIT_SEC = 5.0


class Summarizer:
    """Google AI Studio (Gemini API) を使ってコンテンツを要約するクラス"""

    # 要約プロンプトテンプレート
    PROMPT_TEMPLATE = """あなたは優秀なシニアソフトウェアエンジニアです。
以下の技術記事/論文の内容を、エンジニアが「読むべきか」「どう実装に活かせるか」を判断できるような日本語の3行要約にしてください。

**要約のルール**:
1. 技術的な「新規性」や「解決された課題」に焦点を当てる。
2. 実装のヒントや、使われている主要技術（ライブラリ、アルゴリズム）に触れる。
3. 抽象的な表現は避け、具体的かつ簡潔に書く。

記事タイトル: {title}
記事内容 (Markdown):
{content}

出力フォーマット:
- ポイント1
- ポイント2
- ポイント3"""

    FALLBACK_PROMPT_TEMPLATE = """以下の記事タイトルから、エンジニアに役立つ1行の概要を日本語で書いてください。
タイトル: {title}

出力フォーマット:
- 概要"""

    def __init__(self):
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY 環境変数が未設定です。Google AI Studioでキーを取得してください")

        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model_name = config.gemini_model

        logger.info(f"Google AI Studio 初期化完了: モデル={self.model_name}")
        self._request_count = 0
        self._last_request_time = 0.0

        # 連続エラーによる一時無効化のためのカウンター
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3
        self.disabled = False

    def _rate_limit(self):
        """API レート制限を考慮した待機処理"""
        self._request_count += 1
        now = time.time()
        elapsed = now - self._last_request_time

        # 連続リクエストを防止
        if elapsed < RATE_LIMIT_INTERVAL_SEC:
            wait_time = RATE_LIMIT_INTERVAL_SEC - elapsed
            logger.debug(f"レート制限: {wait_time:.1f}秒待機")
            time.sleep(wait_time)

        # 一定リクエストごとに追加待機（無料枠対応）
        if self._request_count % RATE_LIMIT_BATCH_SIZE == 0:
            logger.info(f"レート制限: {RATE_LIMIT_BATCH_SIZE}リクエスト到達、{RATE_LIMIT_BATCH_WAIT_SEC}秒待機")
            time.sleep(RATE_LIMIT_BATCH_WAIT_SEC)

        self._last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=3, max=30),
        reraise=True,
    )
    def _call_gemini(self, prompt: str) -> str:
        """
        Gemini API を呼び出す（リトライ付き）

        Args:
            prompt: 送信するプロンプト

        Returns:
            API レスポンスのテキスト
        """
        self._rate_limit()
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text

    def summarize_content(self, content: str, title: str = "") -> str:
        """
        コンテンツをエンジニア向けに3行要約する

        Args:
            content: 要約するコンテンツ
            title: 記事タイトル

        Returns:
            3行の要約テキスト
        """
        logger.info(f"要約中: {title[:50]}...")

        # コンテンツの長さを制限
        truncated_content = content[:config.max_content_chars]

        prompt = self.PROMPT_TEMPLATE.format(
            title=title,
            content=truncated_content,
        )

        try:
            result = self._call_gemini(prompt)
            logger.info(f"  → 要約完了: {title[:30]}...")
            return result
        except Exception as e:
            logger.error(f"要約失敗 ({title}): {e}")
            return self._generate_fallback(title)

    def _generate_fallback(self, title: str) -> str:
        """
        要約が失敗した場合のフォールバック

        Args:
            title: 記事タイトル

        Returns:
            タイトルから生成した簡易要約、または失敗メッセージ
        """
        logger.info(f"フォールバック要約を試行: {title[:30]}...")
        try:
            prompt = self.FALLBACK_PROMPT_TEMPLATE.format(title=title)
            return self._call_gemini(prompt)
        except Exception as e:
            logger.error(f"フォールバック要約も失敗: {e}")
            return "要約の生成に失敗しました。"
