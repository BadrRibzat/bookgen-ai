'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    BookOpen,
    PlusCircle,
    Settings,
    Users,
    LogOut,
    ChevronRight,
    TrendingUp
} from 'lucide-react';
import { useAuth } from '@/lib/contexts/AuthContext';


const Sidebar = () => {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    const navItems = [
        { label: 'Overview', icon: LayoutDashboard, href: '/dashboard' },
        { label: 'Generate Book', icon: PlusCircle, href: '/dashboard/generate' },
        { label: 'My Library', icon: BookOpen, href: '/dashboard/history' },
        { label: 'Settings', icon: Settings, href: '/dashboard/settings' },
    ];

    const adminItems = [
        { label: 'Admin Panel', icon: Users, href: '/management-secure' },
        { label: 'Analytics', icon: TrendingUp, href: '/management-secure/analytics' },
    ];

    const isActive = (path: string) => pathname === path;

    return (
        <aside className="w-64 h-screen bg-slate-950 text-slate-300 flex flex-col fixed left-0 top-0 z-40 border-r border-slate-800 shadow-xl">
            {/* Logo */}
            <div className="p-6 border-b border-slate-800/50">
                <Link href="/dashboard" className="flex items-center space-x-3 group">
                    <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform">
                        <BookOpen className="text-white w-6 h-6" />
                    </div>
                    <span className="text-xl font-bold text-white tracking-tight">BookGen AI</span>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
                <div>
                    <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">
                        Management
                    </p>
                    <div className="space-y-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group ${isActive(item.href)
                                    ? 'bg-indigo-600/10 text-indigo-400 font-medium border-l-2 border-indigo-500 rounded-l-none'
                                    : 'hover:bg-slate-900 hover:text-white'
                                    }`}
                            >
                                <div className="flex items-center space-x-3">
                                    <item.icon className={`w-5 h-5 ${isActive(item.href) ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                                    <span>{item.label}</span>
                                </div>
                                {isActive(item.href) && <ChevronRight className="w-4 h-4" />}
                            </Link>
                        ))}
                    </div>
                </div>

                {/* Admin Section */}
                {user?.is_staff && (
                    <div>
                        <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">
                            Administrator
                        </p>
                        <div className="space-y-1">
                            {adminItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group ${isActive(item.href)
                                        ? 'bg-emerald-600/10 text-emerald-400 font-medium border-l-2 border-emerald-500 rounded-l-none'
                                        : 'hover:bg-slate-900 hover:text-white'
                                        }`}
                                >
                                    <div className="flex items-center space-x-3">
                                        <item.icon className={`w-5 h-5 ${isActive(item.href) ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                                        <span>{item.label}</span>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>
                )}
            </nav>

            {/* Bottom Profile Section */}
            <div className="p-4 border-t border-slate-800/50 bg-slate-950/50 backdrop-blur-sm">
                <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/50 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white font-bold ring-2 ring-slate-800">
                        {user?.profile?.avatar_initials || user?.email?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{user?.first_name || 'User'}</p>
                        <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                    </div>
                </div>
                <button
                    onClick={() => logout()}
                    className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-rose-500/10 hover:text-rose-400 transition-colors group"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
