'use client';

import React from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import {
    Search,
    Bell,
    ChevronDown,
    CircleUser,
    Zap
} from 'lucide-react';

const Header = () => {
    const { user } = useAuth();
    const plan = user?.profile?.subscription_plan?.name || 'Free';
    const remaining = user?.usage_summary?.remaining_books ?? 0;

    return (
        <header className="flex items-center justify-between mb-8">
            {/* Search Bar */}
            <div className="relative group max-w-md w-full">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                </div>
                <input
                    type="text"
                    placeholder="Search books, docs, guides..."
                    className="block w-full pl-10 pr-3 py-2 border border-transparent bg-white dark:bg-slate-800 focus:bg-white focus:ring-2 focus:ring-indigo-500 rounded-2xl shadow-sm sm:text-sm transition-all outline-none"
                />
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-6">
                {/* Usage Badge */}
                <div className="hidden md:flex items-center space-x-2 bg-indigo-50 dark:bg-indigo-900/30 px-4 py-2 rounded-2xl border border-indigo-100 dark:border-indigo-800/50">
                    <Zap className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-bold text-indigo-500/80 leading-tight">Credits</span>
                        <span className="text-sm font-semibold text-indigo-700 dark:text-indigo-300 leading-tight">
                            {remaining} Books Left
                        </span>
                    </div>
                </div>

                {/* Notifications */}
                <button className="relative p-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors">
                    <Bell className="w-6 h-6" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white dark:border-slate-900"></span>
                </button>

                {/* User Mini Profile */}
                <div className="flex items-center space-x-4 border-l border-slate-200 dark:border-slate-700 pl-6">
                    <div className="flex flex-col items-end hidden lg:block">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white leading-tight">
                            {user?.first_name} {user?.last_name}
                        </p>
                        <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">
                            {plan} Account
                        </p>
                    </div>
                    <button className="flex items-center space-x-2 group">
                        <div className="w-10 h-10 rounded-xl bg-slate-200 dark:bg-slate-800 flex items-center justify-center border border-slate-300 dark:border-slate-700 group-hover:border-indigo-400 transition-all">
                            <CircleUser className="w-6 h-6 text-slate-600 dark:text-slate-400" />
                        </div>
                        <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
