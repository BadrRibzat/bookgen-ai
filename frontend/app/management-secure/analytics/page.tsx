'use client';

import React, { useState, useEffect } from 'react';
import AdminLayout from '../layout';
import { adminGetAnalytics, AdminAnalytics } from '@/lib/api/admin';
import StatCard from '@/components/dashboard/StatCard';
import {
    Users,
    BookCopy,
    DollarSign,
    TrendingUp,
    Activity,
    ShieldCheck,
    Zap,
    Clock
} from 'lucide-react';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip
} from 'recharts';

const AdminAnalyticsPage = () => {
    const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const data = await adminGetAnalytics();
                setAnalytics(data);
            } catch (err) {
                console.error('Failed to fetch admin analytics', err);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, []);

    if (loading) return (
        <AdminLayout>
            <div className="space-y-10 animate-pulse">
                <div className="h-12 w-1/3 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[1, 2, 3].map(i => <div key={i} className="h-40 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>)}
                </div>
            </div>
        </AdminLayout>
    );

    const chartData = [
        { name: 'Mon', usage: 45 },
        { name: 'Tue', usage: 52 },
        { name: 'Wed', usage: 48 },
        { name: 'Thu', usage: 61 },
        { name: 'Fri', usage: 55 },
        { name: 'Sat', usage: 67 },
        { name: 'Sun', usage: 72 },
    ];

    const revenueDisplay = analytics ? `${analytics.revenue.currency}${analytics.revenue.estimated_monthly}` : '$0';

    return (
        <AdminLayout>
            <div className="space-y-10 animate-fade-in">
                <div>
                    <h2 className="text-4xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">System Intelligence</h2>
                    <p className="text-slate-500 font-medium">Platform-wide performance and engagement metrics.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <StatCard
                        label="Total Operatives"
                        value={analytics?.users.total || 0}
                        icon={Users}
                        color="indigo"
                        trend={{ value: 8, isPositive: true }}
                    />
                    <StatCard
                        label="Books Persistent"
                        value={analytics?.books.total_generated || 0}
                        icon={BookCopy}
                        color="emerald"
                        trend={{ value: 15, isPositive: true }}
                    />
                    <StatCard
                        label="Est. Monthly Income"
                        value={revenueDisplay}
                        icon={DollarSign}
                        color="amber"
                        trend={{ value: 24, isPositive: true }}
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                    {/* Activity Chart */}
                    <div className="bg-white dark:bg-slate-900 p-8 rounded-[3rem] border border-slate-200 dark:border-slate-800 shadow-xl">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-lg font-black text-slate-800 dark:text-white flex items-center space-x-2">
                                <Activity className="w-5 h-5 text-emerald-500" />
                                <span>Generation Volume (7 Days)</span>
                            </h3>
                            <span className="text-xs font-black text-emerald-500 bg-emerald-500/10 px-3 py-1 rounded-full uppercase">Update: Realtime</span>
                        </div>

                        <div className="h-72 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#33415510" />
                                    <XAxis
                                        dataKey="name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 700 }}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 700 }}
                                    />
                                    <Tooltip
                                        contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)' }}
                                    />
                                    <Area type="monotone" dataKey="usage" stroke="#10b981" strokeWidth={4} fillOpacity={1} fill="url(#colorUsage)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Health Stats */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div className="bg-emerald-600 rounded-[2.5rem] p-8 text-white relative overflow-hidden shadow-2xl">
                            <ShieldCheck className="w-12 h-12 mb-6 opacity-20" />
                            <h4 className="text-lg font-black mb-1">System Integrity</h4>
                            <p className="text-3xl font-black mb-4">99.9%</p>
                            <div className="flex items-center space-x-2 text-xs font-bold bg-white/10 w-fit px-3 py-1.5 rounded-full">
                                <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
                                <span>All services nominal</span>
                            </div>
                            <Zap className="absolute -right-4 -bottom-4 w-32 h-32 opacity-10" />
                        </div>

                        <div className="bg-slate-900 rounded-[2.5rem] p-8 text-white relative overflow-hidden border border-slate-800 shadow-2xl">
                            <Clock className="w-12 h-12 mb-6 opacity-20 text-indigo-400" />
                            <h4 className="text-lg font-black mb-1">Wait Time (Avg)</h4>
                            <p className="text-3xl font-black mb-4">42s</p>
                            <div className="flex items-center space-x-2 text-xs font-bold bg-indigo-500/20 w-fit px-3 py-1.5 rounded-full text-indigo-300">
                                <span>-12% from last week</span>
                            </div>
                            <TrendingUp className="absolute -right-4 -bottom-4 w-32 h-32 opacity-10 text-indigo-400" />
                        </div>

                        <div className="sm:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200 dark:border-slate-800 shadow-xl flex items-center justify-between">
                            <div>
                                <h4 className="text-xl font-black text-slate-900 dark:text-white mb-2">Operation Status</h4>
                                <p className="text-slate-500 font-medium text-sm italic">"The matrix is stable. No anomalies detected."</p>
                            </div>
                            <div className="flex -space-x-3">
                                {[1, 2, 3, 4].map(i => (
                                    <div key={i} className={`w-12 h-12 rounded-full border-4 border-white dark:border-slate-900 bg-slate-200 dark:bg-slate-800 flex items-center justify-center font-bold text-slate-400 ${i === 4 ? 'z-40' : i === 3 ? 'z-30' : i === 2 ? 'z-20' : 'z-10'}`}>
                                        {i}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
};

export default AdminAnalyticsPage;
