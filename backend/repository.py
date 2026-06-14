"""
データアクセス層モジュール
ニュースデータと情報ソース設定の読み書きを一元管理する
"""
import os
import json
import logging
import threading
from typing import List, Dict
from config import config
from models import NewsItem, SourceConfig

logger = logging.getLogger(__name__)


class NewsRepository:
    """ニュースデータの永続化を管理するリポジトリ"""

    def __init__(self, data_file: str = None):
        self.data_file = data_file or config.data_file
        self._lock = threading.Lock()

    def load(self) -> List[NewsItem]:
        """保存済みニュースデータを読み込む（スレッドセーフ）"""
        try:
            with self._lock:
                if not os.path.exists(self.data_file):
                    return []
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # pydantic v2 の場合、model_validate もしくはキーワード引数で展開
                    return [NewsItem(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        except Exception as e:
            logger.error(f"データ読み込み失敗: {e}")
            return []

    def save(self, items: List[NewsItem]) -> None:
        """ニュースデータをJSONファイルに保存する（アトミック書き込み＋スレッドセーフ）"""
        tmp_file = f"{self.data_file}.tmp"
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            # シリアライズ (Pydantic v2 の model_dump)
            data = [item.model_dump() for item in items]
            with self._lock:
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_file, self.data_file)
            logger.info(f"データ保存完了: {len(items)}件 → {self.data_file}")
        except Exception as e:
            logger.error(f"データ保存失敗: {e}")
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass

    def deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """URL をキーにして重複を除去する"""
        seen_urls = set()
        unique = []
        for item in items:
            if item.url and item.url not in seen_urls:
                seen_urls.add(item.url)
                unique.append(item)
        return unique


class SourceRepository:
    """ソース設定の読み込みを管理するリポジトリ"""

    def __init__(self, sources_file: str = None):
        self.sources_file = sources_file or config.sources_file

    def load(self) -> Dict[str, List[SourceConfig]]:
        """ソース設定をJSONから読み込み、SourceConfigの辞書を返す"""
        try:
            with open(self.sources_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                result = {}
                for category, sources in data.items():
                    result[category] = [SourceConfig(**src) for src in sources]
                return result
        except FileNotFoundError:
            logger.error(f"{self.sources_file} が見つかりません")
            return {}
        except Exception as e:
            logger.error(f"ソース設定読み込み失敗: {e}")
            return {}
