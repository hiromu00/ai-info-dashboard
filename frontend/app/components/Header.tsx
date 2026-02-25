"use client";

import { Activity } from "lucide-react";

interface HeaderProps {
    /** 最終更新日時 */
    lastUpdated: string | null;
    /** パイプライン実行中フラグ */
    isRunning: boolean;
}

/**
 * ダッシュボードヘッダー
 * ロゴ、タイトル、パイプラインステータス表示
 */
export default function Header({ lastUpdated, isRunning }: HeaderProps) {
    return (
        <header className="mb-10 text-center relative">
            {/* 背景グロー */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[200px] bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

            <div className="relative">
                <h1 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 tracking-tight">
                    AI Info Dashboard
                </h1>
                <p className="text-zinc-400 mt-3 text-lg">
                    エンジニアのためのAI情報ハブ
                </p>

                {/* パイプラインステータス */}
                <div className="flex items-center justify-center gap-2 mt-4">
                    {isRunning ? (
                        <span className="flex items-center gap-1.5 text-xs text-amber-400 bg-amber-400/10 px-3 py-1.5 rounded-full border border-amber-400/20">
                            <Activity className="w-3 h-3 animate-pulse" />
                            データ収集中...
                        </span>
                    ) : lastUpdated ? (
                        <span className="text-xs text-zinc-500">
                            最終更新:{" "}
                            {new Date(lastUpdated).toLocaleString("ja-JP", {
                                month: "2-digit",
                                day: "2-digit",
                                hour: "2-digit",
                                minute: "2-digit",
                            })}
                        </span>
                    ) : null}
                </div>
            </div>
        </header>
    );
}
