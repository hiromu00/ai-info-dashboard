/**
 * 型定義
 */

/** ニュース記事 */
export interface NewsItem {
    category: string;
    source: string;
    title: string;
    url: string;
    summary: string;
    timestamp: string;
}

/** カテゴリタブ定義 */
export const CATEGORIES = [
    { key: "all", label: "すべて", icon: "🌐" },
    { key: "Primary", label: "一次ソース", icon: "📄" },
    { key: "Community", label: "コミュニティ", icon: "💬" },
    { key: "Business", label: "ビジネス", icon: "💼" },
] as const;

export type CategoryKey = (typeof CATEGORIES)[number]["key"];

/** ダッシュボード統計 */
export interface DashboardStats {
    total: number;
    categories: Record<string, number>;
    sources: number;
    last_updated: string | null;
    pipeline_running: boolean;
}
