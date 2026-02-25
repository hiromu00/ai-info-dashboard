"use client";

import { cn } from "../lib/utils";
import { CATEGORIES, type CategoryKey } from "../types";

interface CategoryTabsProps {
    /** 現在選択中のカテゴリ */
    activeTab: CategoryKey;
    /** カテゴリ変更ハンドラ */
    onTabChange: (tab: CategoryKey) => void;
    /** カテゴリ別記事数 */
    counts: Record<string, number>;
}

/**
 * カテゴリタブコンポーネント
 * アクティブ状態のアニメーション付きタブ切り替え
 */
export default function CategoryTabs({
    activeTab,
    onTabChange,
    counts,
}: CategoryTabsProps) {
    return (
        <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
            {CATEGORIES.map(({ key, label, icon }) => {
                const isActive = activeTab === key;
                const count =
                    key === "all"
                        ? Object.values(counts).reduce((a, b) => a + b, 0)
                        : counts[key] ?? 0;

                return (
                    <button
                        key={key}
                        onClick={() => onTabChange(key)}
                        className={cn(
                            "group relative px-4 sm:px-5 py-2 sm:py-2.5 rounded-xl text-sm font-medium transition-all duration-300",
                            isActive
                                ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20"
                                : "bg-zinc-800/60 text-zinc-400 hover:bg-zinc-700/80 hover:text-zinc-200 border border-zinc-700/50"
                        )}
                    >
                        <span className="flex items-center gap-1.5">
                            <span className="text-base">{icon}</span>
                            <span>{label}</span>
                            {count > 0 && (
                                <span
                                    className={cn(
                                        "ml-1 text-xs px-1.5 py-0.5 rounded-full",
                                        isActive
                                            ? "bg-white/20 text-white"
                                            : "bg-zinc-700 text-zinc-400"
                                    )}
                                >
                                    {count}
                                </span>
                            )}
                        </span>
                    </button>
                );
            })}
        </div>
    );
}
