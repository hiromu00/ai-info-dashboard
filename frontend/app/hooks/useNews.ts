"use client";

import { useState, useEffect, useMemo } from "react";
import type { NewsItem, CategoryKey, DashboardStats } from "../types";

/**
 * ニュースデータ収集とフィルタリングの状態・ロジックを管理するカスタムフック
 */
export function useNews() {
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
                setStats((prev: DashboardStats) => ({
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
            result = result.filter((item: NewsItem) => item.category === activeTab);
        }

        // 検索フィルタ
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter(
                (item: NewsItem) =>
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

    return {
        data,
        activeTab,
        setActiveTab,
        searchQuery,
        setSearchQuery,
        loading,
        error,
        stats,
        filteredData,
        categoryCounts,
    };
}
