"use client";

import { ExternalLink, Clock } from "lucide-react";
import { formatRelativeTime } from "../lib/utils";
import type { NewsItem } from "../types";
import { CATEGORY_COLORS, CATEGORY_BADGE_COLORS } from "../lib/constants";

interface NewsCardProps {
    /** ニュースアイテム */
    item: NewsItem;
    /** アニメーション遅延（ms）*/
    index: number;
}

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
            className={`group relative bg-zinc-900/50 border border-zinc-800 border-l-4 ${borderColor} rounded-xl p-5 hover:border-zinc-600 hover:bg-zinc-900/80 transition-all duration-300 hover:shadow-lg hover:shadow-black/20 animate-fade-in break-words`}
            style={{ animationDelay: `${index * 50}ms` }}
        >
            {/* ヘッダー: ソース & 時刻 */}
            <div className="flex items-center justify-between gap-2 flex-wrap mb-3">
                <span
                    className={`text-xs font-medium px-2 py-1 rounded-md border truncate max-w-[150px] ${badgeColor}`}
                    title={item.source}
                >
                    {item.source}
                </span>
                <span className="flex items-center gap-1 text-xs text-zinc-500 flex-shrink-0">
                    <Clock className="w-3 h-3" />
                    {formatRelativeTime(item.timestamp)}
                </span>
            </div>

            {/* タイトル */}
            <h2 className="text-lg font-bold mb-3 leading-snug break-words">
                <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-zinc-100 hover:text-blue-400 transition-colors inline break-words"
                >
                    <span>{item.title}</span>
                    <ExternalLink className="w-3.5 h-3.5 ml-1.5 inline-block align-middle flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>
            </h2>

            {/* 要約 */}
            <div className="space-y-2 break-words">
                {isFailed ? (
                    <p className="text-sm text-zinc-500 italic">
                        要約の生成に失敗しました
                    </p>
                ) : (
                    summaryLines.map((line, i) => (
                        <p
                            key={i}
                            className="text-sm text-zinc-300 pl-3 border-l-2 border-zinc-700/50 leading-relaxed break-words"
                        >
                            {line}
                        </p>
                    ))
                )}
            </div>
        </article>
    );
}
