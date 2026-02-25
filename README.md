# AI Information Dashboard

「一次ソース」「コミュニティ」「ビジネスニュース」の3層からAI関連情報を網羅的に収集・要約し、エンジニアにとって価値のある情報を即座に把握できるダッシュボードです。

## 🚀 特徴

- **3層構造の自動収集**: 論文(arXiv)、企業ブログ(Google DeepMind / OpenAI / AWS / Anthropic)、コミュニティ(Reddit / Hacker News / Hugging Face)、ニュースレター(Ben's Bites)を自動巡回
- **エンジニア視点の要約**: Gemini API を活用した「実装のポイント」「革新性」に焦点を当てた3行要約
- **リアルタイム検索**: タイトル・ソース・要約のキーワード検索
- **カテゴリフィルタ**: 一次ソース / コミュニティ / ビジネスの3カテゴリで絞り込み
- **ヘルスチェック API**: パイプラインの実行状態をモニタリング
- **Docker Compose**: コンテナ構成で1コマンドデプロイ

## 🛠 技術スタック

### Backend: Python + FastAPI + Crawl4AI + Gemini

| コンポーネント | 役割 |
|---|---|
| **FastAPI** | REST API (`/health`, `/api/news`, `/api/stats`) |
| **Crawl4AI** | Playwright内蔵Webクローラー（JavaScript実行後のページをMarkdown変換） |
| **feedparser** | RSSフィード解析 |
| **Gemini API** | エンジニア向け3行要約の生成 |
| **tenacity** | 指数バックオフ付きリトライ処理 |
| **python-dotenv** | `.env` からの環境変数読み込み |
| **schedule** | 定期実行パイプライン（デーモンモード） |

### Frontend: Next.js (App Router) + TailwindCSS

| コンポーネント | 役割 |
|---|---|
| **Header** | ダッシュボードタイトル、最終更新日時の表示 |
| **CategoryTabs** | カテゴリ別フィルタリングタブ |
| **SearchBar** | キーワード検索入力 |
| **NewsCard** | ニュース記事カード（タイトル・ソース・要約・リンク） |
| **StatsBar** | 統計情報バー（総数・カテゴリ別件数・ソース数） |
| **SkeletonCard** | ローディング状態のプレースホルダー |

- データは `/data/news.json` から直接読み込み（バックエンドとフロントエンドで共有ボリューム）
- `useMemo` によるフィルタリング・検索のパフォーマンス最適化

### Infrastructure: Docker Compose

- ヘルスチェック付きコンテナ構成（`restart: always`）
- バックエンド（API + スケジューラ）とフロントエンドの分離
- 共有ボリューム `./data` でJSON データを受け渡し

## 📦 ディレクトリ構造

```
.
├── backend/
│   ├── config.py          # 設定管理（環境変数 + dotenv）
│   ├── models.py          # Pydantic データモデル
│   ├── scraper.py         # RSS / Web スクレイピング
│   ├── summarizer.py      # Gemini 要約（リトライ + レート制限）
│   ├── main.py            # FastAPI + パイプライン統合
│   ├── sources.json       # 情報ソース定義
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/    # UI コンポーネント群
│   │   ├── types/         # TypeScript 型定義
│   │   ├── lib/           # ユーティリティ関数
│   │   ├── page.tsx       # メインページ
│   │   ├── layout.tsx     # レイアウト
│   │   └── globals.css    # グローバルスタイル
│   ├── Dockerfile
│   └── package.json
├── data/
│   └── news.json          # パイプライン出力（自動生成）
├── docker-compose.yml
├── .env                   # 環境変数（GEMINI_API_KEY 等）
├── .env.example
└── .devcontainer/
```

## 📡 情報ソース

| カテゴリ | ソース | 取得方法 |
|---------|--------|---------|
| **一次ソース** | arXiv (cs.AI) | RSS |
| | Google DeepMind Blog | RSS |
| | OpenAI Blog | RSS |
| | AWS Machine Learning Blog | RSS |
| | Anthropic News | Web クロール |
| **コミュニティ** | Hugging Face Blog | Web クロール |
| | Reddit (r/LocalLLaMA) | RSS |
| | Hacker News | RSS |
| **ビジネス** | Ben's Bites | Web クロール |

## 📡 API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/health` | ヘルスチェック＆パイプライン状態 |
| GET | `/api/news` | ニュースデータ取得（`?category=`, `?search=`, `?limit=`） |
| GET | `/api/stats` | ダッシュボード統計情報 |

## 🚀 開発の始め方

### 必須要件
- Docker Desktop (or Engine)
- Git
- Gemini API キー（[Google AI Studio](https://aistudio.google.com/) で取得）

### 手順
1. リポジトリをクローン
2. `.env.example` を `.env` にコピーし `GEMINI_API_KEY` を設定
   ```bash
   cp .env.example .env
   # .env の GEMINI_API_KEY を編集
   ```
3. `docker-compose up` を実行
   ```bash
   docker-compose up -d --build
   ```
4. `http://localhost:3000` でダッシュボードにアクセス
5. `http://localhost:8000/health` でバックエンド状態を確認

### ポート一覧

| サービス | ポート | URL |
|---------|--------|-----|
| フロントエンド | 3000 | http://localhost:3000 |
| バックエンド API | 8000 | http://localhost:8000 |

## 🔧 トラブルシューティング

### 要約が「要約の生成に失敗しました。」と表示される

1. `.env` に有効な `GEMINI_API_KEY` が設定されているか確認
2. バックエンドコンテナを再ビルドして再起動
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```
3. ログで Gemini API の呼び出し状況を確認
   ```bash
   docker-compose logs -f backend
   ```

### データが更新されない

- バックエンドのデーモンモードは **6時間ごと** に自動実行されます
- 手動で即時実行したい場合はバックエンドコンテナを再起動してください

### コンテナが起動しない

- `docker-compose logs backend` でエラーログを確認
- Playwright（Chromium）のインストールに時間がかかる場合があります（初回ビルド時）

## ⚙️ 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|-----------|------|
| `GEMINI_API_KEY` | ✅ | - | Gemini API キー |
| `GEMINI_MODEL` | - | `gemini-1.5-flash` | 使用するGeminiモデル |
| `RUN_MODE` | - | `oneshot` | 実行モード（`oneshot` / `daemon`） |
| `SCHEDULE_INTERVAL_HOURS` | - | `6` | 定期実特間隔（時間） |
| `RSS_MAX_ENTRIES` | - | `5` | RSS最大取得件数 |
