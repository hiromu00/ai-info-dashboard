"use client";

import { Newspaper, Layers, Rss } from "lucide-react";

interface StatsBarProps {
    /** 合計記事数 */
    total: number;
    /** カテゴリ別記事数 */
    categories: Record<string, number>;
    /** ソース数 */
    sourceCount: number;
}

/**
 * 統計バーコンポーネント
 * カテゴリ別記事数とソース数を表示
 */
export default function StatsBar({
    total,
    categories,
    sourceCount,
}: StatsBarProps) {
    if (total === 0) return null;

    return (
        <div className="flex flex-wrap justify-center gap-4 sm:gap-6 text-xs text-zinc-500">
            <div className="flex items-center gap-1.5">
                <Newspaper className="w-3.5 h-3.5" />
                <span>
                    合計 <strong className="text-zinc-300">{total}</strong> 件
                </span>
            </div>
            <div className="flex items-center gap-1.5">
                <Rss className="w-3.5 h-3.5" />
                <span>
                    <strong className="text-zinc-300">{sourceCount}</strong> ソース
                </span>
            </div>
            <div className="flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                <span>
                    <strong className="text-zinc-300">
                        {Object.keys(categories).length}
                    </strong>{" "}
                    カテゴリ
                </span>
            </div>
        </div>
    );
}
