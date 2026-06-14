"use client";

import Header from "./components/Header";
import CategoryTabs from "./components/CategoryTabs";
import SearchBar from "./components/SearchBar";
import NewsCard from "./components/NewsCard";
import StatsBar from "./components/StatsBar";
import SkeletonCard from "./components/SkeletonCard";
import { AlertTriangle } from "lucide-react";
import { useNews } from "./hooks/useNews";
import { SKELETON_COUNT } from "./lib/constants";

export default function Home() {
    const {
        activeTab,
        setActiveTab,
        searchQuery,
        setSearchQuery,
        loading,
        error,
        stats,
        filteredData,
        categoryCounts,
    } = useNews();

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
                        {Array.from({ length: SKELETON_COUNT }).map((_, i) => (
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
