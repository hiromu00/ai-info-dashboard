"""
設定管理モジュール
環境変数と定数を一元管理する
"""
import os
from typing import List
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# プロジェクトルートの .env を読み込む（環境変数が未設定の場合のフォールバック）
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


@dataclass
class AppConfig:
    """アプリケーション設定"""

    # Google AI Studio / Gemini 設定
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # パイプライン設定
    run_mode: str = "oneshot"  # "oneshot" or "daemon"
    schedule_interval_hours: int = 6
    rss_max_entries: int = 5

    # ファイルパス
    data_file: str = "data/news.json"
    sources_file: str = "sources.json"
    log_file: str = "backend.log"

    # API 設定
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])

    # リトライ設定
    max_retries: int = 3
    retry_wait_seconds: int = 2

    # 要約設定
    max_content_chars: int = 10000

    @classmethod
    def from_env(cls) -> "AppConfig":
        """環境変数から設定を読み込む"""
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            run_mode=os.getenv("RUN_MODE", "oneshot"),
            schedule_interval_hours=int(os.getenv("SCHEDULE_INTERVAL_HOURS", "6")),
            rss_max_entries=int(os.getenv("RSS_MAX_ENTRIES", "5")),
            data_file=os.getenv("DATA_FILE", "data/news.json"),
            sources_file=os.getenv("SOURCES_FILE", "sources.json"),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8000")),
            allowed_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")],
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_wait_seconds=int(os.getenv("RETRY_WAIT_SECONDS", "2")),
            max_content_chars=int(os.getenv("MAX_CONTENT_CHARS", "10000")),
        )


# グローバルシングルトン
config = AppConfig.from_env()
