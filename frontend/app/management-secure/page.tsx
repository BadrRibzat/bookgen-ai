'use client';

import React, { useState, useEffect } from 'react';
import AdminLayout from './layout';
import { adminGetUsers, adminGetBooks, adminGetAnalytics, AdminAnalytics } from '@/lib/api/admin';
import { User, Book } from '@/shared/types';
import Link from 'next/link';
import {
    BookCopy,
    ArrowUpRight,
    ShieldAlert,
    Zap,
    Activity,
    UserCheck,
    PlusCircle
} from 'lucide-react';
import { format } from 'date-fns';

const AdminOverviewPage = () => {
    const [data, setData] = useState<{
        users: User[];
        books: Book[];
        analytics: AdminAnalytics | null;
    }>({
        users: [],
        books: [],
        analytics: null
    });

    useEffect(() => {
        const fetchOverview = async () => {
            try {
                const [usersRes, booksRes, analyticsRes] = await Promise.all([
                    adminGetUsers(),
                    adminGetBooks(),
                    adminGetAnalytics()
                ]);
                setData({
                    users: usersRes.results.slice(0, 5),
                    books: booksRes.slice(0, 5),
                    analytics: analyticsRes
                });
            } catch (err) {
                console.error('Overview fetch failed', err);
            }
        };
        fetchOverview();
    }, []);

    const totalUsers = data.analytics?.users.total || 0;
    const totalBooks = data.analytics?.books.total_generated || 0;
    const estimatedRevenue = data.analytics?.revenue.estimated_monthly || 0;

    return (
        <AdminLayout>
            <div className="space-y-12 animate-fade-in">
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <h2 className="text-5xl font-black text-slate-900 dark:text-white mb-3 tracking-tighter">Grand Command</h2>
                        <p className="text-slate-500 font-medium max-w-lg italic">
                            "Power is nothing without control. Welcome to the heart of BookGen AI."
                        </p>
                    </div>
                    <div className="flex items-center space-x-3">
                        <div className="flex items-center -space-x-2">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="w-8 h-8 rounded-full border-2 border-slate-50 dark:border-slate-950 bg-slate-200 dark:bg-slate-800"></div>
                            ))}
                        </div>
                        <span className="text-xs font-black text-slate-400 uppercase tracking-widest pl-2">3 Admins Online</span>
                    </div>
                </header>

                {/* Quick Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <div className="bg-emerald-600 rounded-[2.5rem] p-8 text-white shadow-2xl relative overflow-hidden group">
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-70 mb-1 block">Live Operatives</span>
                        <p className="text-4xl font-black mb-4">{totalUsers}</p>
                        <Activity className="absolute -right-4 -bottom-4 w-24 h-24 opacity-10 group-hover:scale-120 transition-transform" />
                    </div>

                    <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200 dark:border-slate-800 shadow-xl relative overflow-hidden group">
                        <span className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-[0.2em] mb-1 block">Stored Codexes</span>
                        <p className="text-4xl font-black text-slate-900 dark:text-white mb-4">{totalBooks}</p>
                        <BookCopy className="absolute -right-4 -bottom-4 w-24 h-24 text-slate-500/5 group-hover:scale-120 transition-transform" />
                    </div>

                    <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200 dark:border-slate-800 shadow-xl relative overflow-hidden group">
                        <span className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-[0.2em] mb-1 block">Monthly Fuel</span>
                        <p className="text-4xl font-black text-slate-900 dark:text-white mb-4">${estimatedRevenue}</p>
                        <Zap className="absolute -right-4 -bottom-4 w-24 h-24 text-slate-500/5 group-hover:scale-120 transition-transform" />
                    </div>

                    <div className="bg-slate-100 dark:bg-slate-800 rounded-[2.5rem] p-8 flex flex-col justify-center items-center border-2 border-dashed border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-all cursor-pointer group">
                        <PlusCircle className="w-10 h-10 text-slate-400 mb-2 group-hover:text-emerald-500 transition-colors" />
                        <span className="text-sm font-black text-slate-500 uppercase tracking-widest">New Deployment</span>
                    </div>
                </div>

                {/* Recent Activity Sections */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                    {/* Recent Users */}
                    <div className="bg-white dark:bg-slate-900 rounded-[3rem] p-10 shadow-xl border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-2xl font-black text-slate-900 dark:text-white flex items-center space-x-3">
                                <UserCheck className="w-6 h-6 text-emerald-500" />
                                <span>Recent Operatives</span>
                            </h3>
                            <Link href="/management-secure/users" className="text-xs font-black text-emerald-500 hover:underline uppercase tracking-widest">View Roster →</Link>
                        </div>

                        <div className="space-y-4">
                            {data.users.map((u) => (
                                <div key={u.id} className="flex items-center justify-between p-4 rounded-[1.5rem] bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all group">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-700 flex items-center justify-center font-black text-slate-400 border border-slate-200 dark:border-slate-600">
                                            {u.email.charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <p className="text-sm font-black text-slate-900 dark:text-white">{u.full_name || u.email}</p>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase">{format(new Date(u.date_joined), 'MMM dd, yyyy')}</p>
                                        </div>
                                    </div>
                                    <ArrowUpRight className="w-5 h-5 text-slate-300 group-hover:text-emerald-500 transition-colors" />
                                </div>
                            ))}
                            {data.users.length === 0 && <p className="text-slate-500 italic text-center py-10">Waiting for first recruitment...</p>}
                        </div>
                    </div>

                    {/* Recent Books */}
                    <div className="bg-white dark:bg-slate-900 rounded-[3rem] p-10 shadow-xl border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-2xl font-black text-slate-900 dark:text-white flex items-center space-x-3">
                                <BookCopy className="w-6 h-6 text-indigo-500" />
                                <span>Latest Transmutations</span>
                            </h3>
                            <span className="text-xs font-black text-indigo-500 uppercase tracking-widest">Manifest</span>
                        </div>

                        <div className="space-y-4">
                            {data.books.map((b) => (
                                <div key={b.id} className="flex items-center justify-between p-4 rounded-[1.5rem] bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all group">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-700 flex items-center justify-center text-slate-400 border border-slate-200 dark:border-slate-600">
                                            <Zap className={`w-5 h-5 ${b.status === 'completed' ? 'text-emerald-500' : 'text-amber-500'}`} />
                                        </div>
                                        <div className="max-w-[180px]">
                                            <p className="text-sm font-black text-slate-900 dark:text-white truncate">{b.title}</p>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase">{b.status}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Archive ID</p>
                                        <p className="text-xs font-bold text-slate-900 dark:text-white leading-none">#{b.id.slice(-4).toUpperCase()}</p>
                                    </div>
                                </div>
                            ))}
                            {data.books.length === 0 && <p className="text-slate-500 italic text-center py-10">No Codexes found in the archives.</p>}
                        </div>
                    </div>
                </div>

                {/* Security Alert Placeholder */}
                <div className="bg-slate-900 rounded-[2.5rem] p-10 flex items-center space-x-8 border-l-8 border-emerald-500 relative overflow-hidden shadow-2xl">
                    <div className="relative z-10 w-16 h-16 bg-emerald-500/20 rounded-2xl flex items-center justify-center flex-shrink-0">
                        <ShieldAlert className="w-10 h-10 text-emerald-500" />
                    </div>
                    <div className="relative z-10 flex-1">
                        <h4 className="text-xl font-black text-white mb-2">Platform Integrity Protocol Alpha</h4>
                        <p className="text-slate-400 text-sm font-medium leading-relaxed">
                            All systems are currently operating within nominal parameters. Automated failovers are primed.
                            No manual intervention is required at this cycle. Stay vigilant, Commander.
                        </p>
                    </div>
                    <div className="absolute right-10 top-1/2 -translate-y-1/2 flex items-center space-x-4 opacity-20 hover:opacity-100 transition-opacity">
                        <button className="bg-white/10 text-white px-6 py-3 rounded-xl font-black text-xs uppercase tracking-widest">Protocol Log</button>
                        <button className="bg-emerald-600 text-white px-6 py-3 rounded-xl font-black text-xs uppercase tracking-widest">System Check</button>
                    </div>
                    <Activity className="absolute -left-10 -bottom-10 w-64 h-64 text-emerald-500/5" />
                </div>
            </div>
        </AdminLayout>
    );
};

export default AdminOverviewPage;
