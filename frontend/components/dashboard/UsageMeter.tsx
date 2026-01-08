'use client';

import React from 'react';

interface UsageMeterProps {
    current: number;
    total: number;
    label: string;
}

const UsageMeter = ({ current, total, label }: UsageMeterProps) => {
    const isUnlimited = total === -1;
    const percentage = isUnlimited ? 0 : Math.min((current / total) * 100, 100);
    const isLow = !isUnlimited && percentage > 80;

    return (
        <div className="space-y-3">
            <div className="flex justify-between items-end">
                <label className="text-sm font-black text-slate-500 uppercase tracking-widest">{label}</label>
                <span className="text-sm font-bold text-slate-900 dark:text-white">
                    {isUnlimited ? (
                        <>{current} <span className="text-slate-400">(Unlimited)</span></>
                    ) : (
                        <>{current} / {total} <span className="text-slate-400">({Math.round(percentage)}%)</span></>
                    )}
                </span>
            </div>
            <div className="h-4 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden border border-slate-200 dark:border-slate-700">
                {isUnlimited ? (
                    <div className="h-full w-full bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)] flex items-center justify-center">
                        <span className="text-xs font-black text-white">∞</span>
                    </div>
                ) : (
                    <div
                        className={`h-full transition-all duration-1000 ease-out rounded-full ${isLow ? 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]' : 'bg-indigo-600 shadow-[0_0_10px_rgba(79,70,229,0.5)]'
                            }`}
                        style={{ width: `${percentage}%` }}
                    ></div>
                )}
            </div>
            {isLow && (
                <p className="text-xs font-bold text-rose-500 animate-pulse">
                    ⚠️ You are approaching your monthly limit. Consider upgrading for more credits.
                </p>
            )}
        </div>
    );
};

export default UsageMeter;
