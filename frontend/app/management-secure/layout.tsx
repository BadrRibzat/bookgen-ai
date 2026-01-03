'use client';

import React, { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
    Users,
    TrendingUp,
    ShieldCheck,
    LogOut,
    ChevronRight,
    LayoutDashboard
} from 'lucide-react';
import { useAuth } from '@/lib/contexts/AuthContext';

interface AdminLayoutProps {
    children: ReactNode;
}

const AdminLayout = ({ children }: AdminLayoutProps) => {
    const pathname = usePathname();
    const router = useRouter();
    const { user, loading, isAuthenticated, logout } = useAuth();

    const isLoginPage = pathname === '/management-secure/login';

    // Guard: Only allow staff
    React.useEffect(() => {
        if (!loading && !isLoginPage && (!isAuthenticated || !user?.is_staff)) {
            router.push('/management-secure/login');
        }
    }, [loading, isAuthenticated, user, router, isLoginPage]);

    if (loading) return (
        <div className="h-screen bg-slate-950 flex items-center justify-center">
            <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );

    // Skip staff layout for login page
    if (isLoginPage) return <>{children}</>;

    if (!user?.is_staff) return null;

    const navItems = [
        { label: 'Overview', icon: LayoutDashboard, href: '/management-secure' },
        { label: 'User Management', icon: Users, href: '/management-secure/users' },
        { label: 'System Analytics', icon: TrendingUp, href: '/management-secure/analytics' },
    ];

    const isActive = (path: string) => pathname === path;

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex">
            {/* Admin Sidebar */}
            <aside className="w-72 h-screen bg-slate-900 text-slate-300 flex flex-col fixed left-0 top-0 z-40 border-r border-emerald-500/20 shadow-2xl">
                <div className="p-8 border-b border-slate-800">
                    <Link href="/management-secure" className="flex items-center space-x-3 group">
                        <div className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
                            <ShieldCheck className="text-white w-6 h-6" />
                        </div>
                        <div>
                            <span className="text-xl font-black text-white block leading-tight">Admin OS</span>
                            <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">Management Console</span>
                        </div>
                    </Link>
                </div>

                <nav className="flex-1 py-8 px-6 space-y-2">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center justify-between px-4 py-4 rounded-2xl transition-all duration-300 group ${isActive(item.href)
                                ? 'bg-emerald-600/10 text-emerald-400 border-l-4 border-emerald-500 rounded-l-none'
                                : 'hover:bg-slate-800 hover:text-white'
                                }`}
                        >
                            <div className="flex items-center space-x-3">
                                <item.icon className={`w-5 h-5 ${isActive(item.href) ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                                <span className="font-bold">{item.label}</span>
                            </div>
                            {isActive(item.href) && <ChevronRight className="w-4 h-4" />}
                        </Link>
                    ))}

                    <div className="pt-8 mt-8 border-t border-slate-800">
                        <Link
                            href="/dashboard"
                            className="flex items-center space-x-3 px-4 py-4 rounded-2xl text-slate-500 hover:bg-slate-800 hover:text-white transition-all"
                        >
                            <ChevronLeft className="w-5 h-5" />
                            <span className="font-bold">Return to User App</span>
                        </Link>
                    </div>
                </nav>

                <div className="p-6 border-t border-slate-800 bg-slate-900/50">
                    <button
                        onClick={() => logout()}
                        className="w-full flex items-center space-x-3 px-5 py-4 rounded-2xl text-slate-400 hover:bg-rose-500/10 hover:text-rose-400 transition-all font-bold group"
                    >
                        <LogOut className="w-5 h-5" />
                        <span>Sign Out</span>
                    </button>
                </div>
            </aside>

            {/* Admin Content */}
            <main className="flex-1 ml-72 min-h-screen">
                <header className="h-20 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl flex items-center justify-between px-10 sticky top-0 z-30">
                    <h2 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em]">
                        Security Clearance: <span className="text-emerald-500">Superuser</span>
                    </h2>
                    <div className="flex items-center space-x-4">
                        <div className="text-right">
                            <p className="text-sm font-black text-slate-900 dark:text-white leading-tight">{user?.full_name}</p>
                            <p className="text-[10px] font-bold text-slate-400 uppercase">{user?.email}</p>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold ring-4 ring-emerald-500/10">
                            {user?.email?.charAt(0).toUpperCase()}
                        </div>
                    </div>
                </header>

                <div className="p-10 max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};

// Help helper
const ChevronLeft = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
    </svg>
);

export default AdminLayout;
