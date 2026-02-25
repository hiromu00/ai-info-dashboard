"""
要約モジュール
Vertex AI (Gemini) を使用してコンテンツをエンジニア向けに要約する
"""
import os
import time
import logging
import vertexai
from vertexai.generative_models import GenerativeModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import config

logger = logging.getLogger(__name__)


class Summarizer:
    """Vertex AI (Gemini) を使ってコンテンツを要約するクラス"""

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
        if not config.gcp_project_id:
            raise ValueError("GCP_PROJECT_ID 環境変数が未設定です")

        vertexai.init(
            project=config.gcp_project_id,
            location=config.gcp_location,
        )
        logger.info(f"Vertex AI 初期化完了: project={config.gcp_project_id}, location={config.gcp_location}")
        logger.info(f"Gemini モデル: {config.gemini_model}")
        self.model = GenerativeModel(config.gemini_model)
        self._request_count = 0
        self._last_request_time = 0.0

    def _rate_limit(self):
        """API レート制限を考慮した待機処理"""
        self._request_count += 1
        now = time.time()
        elapsed = now - self._last_request_time

        # 1秒以内の連続リクエストを防止
        if elapsed < 1.0:
            wait_time = 1.0 - elapsed
            logger.debug(f"レート制限: {wait_time:.1f}秒待機")
            time.sleep(wait_time)

        # 10リクエストごとに追加待機（無料枠対応）
        if self._request_count % 10 == 0:
            logger.info("レート制限: 10リクエスト到達、5秒待機")
            time.sleep(5)

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
        response = self.model.generate_content(prompt)
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
