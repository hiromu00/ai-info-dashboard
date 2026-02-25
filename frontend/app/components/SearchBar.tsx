"use client";

import { Search, X } from "lucide-react";

interface SearchBarProps {
    /** 検索クエリ */
    query: string;
    /** 検索クエリ変更ハンドラ */
    onQueryChange: (query: string) => void;
}

/**
 * 検索バーコンポーネント
 * タイトル・ソース名でのリアルタイムフィルタリング
 */
export default function SearchBar({ query, onQueryChange }: SearchBarProps) {
    return (
        <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
                type="text"
                placeholder="タイトル・ソースで検索..."
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                className="w-full pl-10 pr-10 py-2.5 bg-zinc-800/60 border border-zinc-700/50 rounded-xl text-sm text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
            />
            {query && (
                <button
                    onClick={() => onQueryChange("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                    <X className="w-4 h-4" />
                </button>
            )}
        </div>
    );
}
