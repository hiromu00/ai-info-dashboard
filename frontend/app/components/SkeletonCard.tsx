"use client";

/**
 * スケルトンカードコンポーネント
 * ローディング中のプレースホルダー表示
 */
export default function SkeletonCard() {
    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 animate-pulse">
            {/* ヘッダー */}
            <div className="flex items-center justify-between mb-4">
                <div className="h-5 w-24 bg-zinc-800 rounded-md" />
                <div className="h-4 w-16 bg-zinc-800 rounded-md" />
            </div>

            {/* タイトル */}
            <div className="space-y-2 mb-4">
                <div className="h-5 w-full bg-zinc-800 rounded-md" />
                <div className="h-5 w-3/4 bg-zinc-800 rounded-md" />
            </div>

            {/* 要約 */}
            <div className="space-y-2">
                <div className="h-4 w-full bg-zinc-800/60 rounded-md" />
                <div className="h-4 w-5/6 bg-zinc-800/60 rounded-md" />
                <div className="h-4 w-4/6 bg-zinc-800/60 rounded-md" />
            </div>
        </div>
    );
}
