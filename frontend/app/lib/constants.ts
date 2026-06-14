/**
 * フロントエンド共通定数
 */

/** カテゴリに応じたアクセントカラー */
export const CATEGORY_COLORS: Record<string, string> = {
    Primary: "border-l-blue-500",
    Community: "border-l-emerald-500",
    Business: "border-l-amber-500",
} as const;

export const CATEGORY_BADGE_COLORS: Record<string, string> = {
    Primary: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    Community: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    Business: "bg-amber-500/10 text-amber-400 border-amber-500/20",
} as const;

/** ローディング時のプレースホルダーカード数 */
export const SKELETON_COUNT = 6;
