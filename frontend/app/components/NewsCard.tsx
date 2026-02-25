"use client";

import { ExternalLink, Clock } from "lucide-react";
import { formatRelativeTime } from "../lib/utils";
import type { NewsItem } from "../types";

interface NewsCardProps {
    /** ニュースアイテム */
    item: NewsItem;
    /** アニメーション遅延（ms）*/
    index: number;
}

/** カテゴリに応じたアクセントカラー */
const CATEGORY_COLORS: Record<string, string> = {
    Primary: "border-l-blue-500",
    Community: "border-l-emerald-500",
    Business: "border-l-amber-500",
};

const CATEGORY_BADGE_COLORS: Record<string, string> = {
    Primary: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    Community: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    Business: "bg-amber-500/10 text-amber-400 border-amber-500/20",
};

/**
 * ニュースカードコンポーネント
 * ホバーエフェクト、カテゴリ色分け、要約表示
 */
export default function NewsCard({ item, index }: NewsCardProps) {
    const borderColor = CATEGORY_COLORS[item.category] ?? "border-l-zinc-500";
    const badgeColor =
        CATEGORY_BADGE_COLORS[item.category] ??
        "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";

    // 要約の行を解析
    const summaryLines = item.summary
        .split("\n")
        .filter((line) => line.trim().startsWith("-") || line.trim().startsWith("•"))
        .map((line) => line.replace(/^[\s\-•]+/, "").trim())
        .filter(Boolean);

    const isFailed =
        item.summary.includes("失敗") || summaryLines.length === 0;

    return (
        <article
            className={`group relative bg-zinc-900/50 border border-zinc-800 border-l-4 ${borderColor} rounded-xl p-5 hover:border-zinc-600 hover:bg-zinc-900/80 transition-all duration-300 hover:shadow-lg hover:shadow-black/20 animate-fade-in`}
            style={{ animationDelay: `${index * 50}ms` }}
        >
            {/* ヘッダー: ソース & 時刻 */}
            <div className="flex items-center justify-between mb-3">
                <span
                    className={`text-xs font-medium px-2 py-1 rounded-md border ${badgeColor}`}
                >
                    {item.source}
                </span>
                <span className="flex items-center gap-1 text-xs text-zinc-500">
                    <Clock className="w-3 h-3" />
                    {formatRelativeTime(item.timestamp)}
                </span>
            </div>

            {/* タイトル */}
            <h2 className="text-lg font-bold mb-3 leading-snug">
                <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-zinc-100 hover:text-blue-400 transition-colors inline-flex items-start gap-1.5"
                >
                    <span>{item.title}</span>
                    <ExternalLink className="w-3.5 h-3.5 mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>
            </h2>

            {/* 要約 */}
            <div className="space-y-2">
                {isFailed ? (
                    <p className="text-sm text-zinc-500 italic">
                        要約の生成に失敗しました
                    </p>
                ) : (
                    summaryLines.map((line, i) => (
                        <p
                            key={i}
                            className="text-sm text-zinc-300 pl-3 border-l-2 border-zinc-700/50 leading-relaxed"
                        >
                            {line}
                        </p>
                    ))
                )}
            </div>
        </article>
    );
}
