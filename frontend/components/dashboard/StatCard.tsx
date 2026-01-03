import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
    label: string;
    value: string | number;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color: 'indigo' | 'emerald' | 'amber' | 'rose';
}

const colorMap = {
    indigo: 'bg-indigo-500/10 text-indigo-500 border-indigo-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
};

const StatCard = ({ label, value, icon: Icon, trend, color }: StatCardProps) => {
    return (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-700/50 hover:shadow-md transition-all group overflow-hidden relative">
            <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-2xl border ${colorMap[color]} group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6" />
                </div>
                {trend && (
                    <div className={`flex items-center space-x-1 text-xs font-bold px-2 py-1 rounded-lg ${trend.isPositive ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                        <span>{trend.isPositive ? '+' : '-'}{trend.value}%</span>
                    </div>
                )}
            </div>

            <div className="space-y-1">
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</p>
                <h3 className="text-3xl font-bold text-slate-900 dark:text-white">{value}</h3>
            </div>

            {/* Background decoration */}
            <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full opacity-5 blur-2xl ${color === 'indigo' ? 'bg-indigo-500' : color === 'emerald' ? 'bg-emerald-500' : color === 'amber' ? 'bg-amber-500' : 'bg-rose-500'}`}></div>
        </div>
    );
};

export default StatCard;
