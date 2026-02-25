"use client";

import { useEffect, useState, useMemo } from "react";
import type { NewsItem, CategoryKey, DashboardStats } from "./types";
import Header from "./components/Header";
import CategoryTabs from "./components/CategoryTabs";
import SearchBar from "./components/SearchBar";
import NewsCard from "./components/NewsCard";
import StatsBar from "./components/StatsBar";
import SkeletonCard from "./components/SkeletonCard";
import { AlertTriangle } from "lucide-react";

export default function Home() {
    // ── State ─────────────────────────
    const [data, setData] = useState<NewsItem[]>([]);
    const [activeTab, setActiveTab] = useState<CategoryKey>("all");
    const [searchQuery, setSearchQuery] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [stats, setStats] = useState<DashboardStats>({
        total: 0,
        categories: {},
        sources: 0,
        last_updated: null,
        pipeline_running: false,
    });

    // ── データ取得 ─────────────────────
    useEffect(() => {
        setLoading(true);

        // ニュースデータ取得（JSON ファイルから直接読み込み）
        fetch("/data/news.json")
            .then((res) => {
                if (!res.ok) throw new Error("Data not found");
                return res.json();
            })
            .then((newsData: NewsItem[]) => {
                setData(newsData);
                setError(null);

                // 統計情報をデータから計算
                const categories: Record<string, number> = {};
                const sources = new Set<string>();
                for (const item of newsData) {
                    categories[item.category] = (categories[item.category] ?? 0) + 1;
                    sources.add(item.source);
                }
                setStats((prev) => ({
                    ...prev,
                    total: newsData.length,
                    categories,
                    sources: sources.size,
                    last_updated:
                        newsData.length > 0
                            ? newsData[newsData.length - 1].timestamp
                            : null,
                }));
            })
            .catch((err) => {
                console.error("データ読み込みエラー:", err);
                setError(
                    "データを読み込めませんでした。バックエンドコンテナが起動しているか確認してください。"
                );
            })
            .finally(() => setLoading(false));
    }, []);

    // ── フィルタリング ────────────────────
    const filteredData = useMemo(() => {
        let result = data;

        // カテゴリフィルタ
        if (activeTab !== "all") {
            result = result.filter((item) => item.category === activeTab);
        }

        // 検索フィルタ
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter(
                (item) =>
                    item.title.toLowerCase().includes(q) ||
                    item.source.toLowerCase().includes(q) ||
                    item.summary.toLowerCase().includes(q)
            );
        }

        return result;
    }, [data, activeTab, searchQuery]);

    // ── カテゴリ別カウント ───────────────
    const categoryCounts = useMemo(() => {
        const counts: Record<string, number> = {};
        for (const item of data) {
            counts[item.category] = (counts[item.category] ?? 0) + 1;
        }
        return counts;
    }, [data]);

    return (
        <main className="min-h-screen bg-zinc-950 text-zinc-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
                {/* ヘッダー */}
                <Header
                    lastUpdated={stats.last_updated}
                    isRunning={stats.pipeline_running}
                />

                {/* コントロールエリア */}
                <div className="space-y-5 mb-8">
                    <CategoryTabs
                        activeTab={activeTab}
                        onTabChange={setActiveTab}
                        counts={categoryCounts}
                    />
                    <SearchBar query={searchQuery} onQueryChange={setSearchQuery} />
                    <StatsBar
                        total={stats.total}
                        categories={stats.categories}
                        sourceCount={stats.sources}
                    />
                </div>

                {/* ローディング */}
                {loading && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <SkeletonCard key={i} />
                        ))}
                    </div>
                )}

                {/* エラー */}
                {error && (
                    <div className="text-center py-16 bg-red-900/10 rounded-xl border border-red-900/30">
                        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
                        <p className="text-red-400 font-medium">{error}</p>
                        <p className="text-sm mt-2 text-zinc-500">
                            docker-compose up を実行してください
                        </p>
                    </div>
                )}

                {/* コンテンツ */}
                {!loading && !error && (
                    <>
                        {filteredData.length === 0 ? (
                            <div className="text-center py-16 text-zinc-500">
                                <p className="text-lg">
                                    {searchQuery
                                        ? `「${searchQuery}」に一致する記事が見つかりません`
                                        : "このカテゴリの記事はまだありません"}
                                </p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                                {filteredData.map((item, idx) => (
                                    <NewsCard key={`${item.url}-${idx}`} item={item} index={idx} />
                                ))}
                            </div>
                        )}
                    </>
                )}

                {/* フッター */}
                <footer className="mt-16 text-center text-xs text-zinc-600 border-t border-zinc-800/50 pt-6">
                    <p>
                        AI Info Dashboard — Powered by Gemini API, Crawl4AI & Next.js
                    </p>
                </footer>
            </div>
        </main>
    );
}
