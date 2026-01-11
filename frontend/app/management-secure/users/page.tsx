'use client';

import React, { useState, useEffect } from 'react';
import AdminLayout from '../layout';
import { adminGetUsers, adminUpdateUser } from '@/lib/api/admin';
import { User } from '@/shared/types';
import {
    Search,
    CheckCircle,
    XCircle,
    Shield,
    Trash2,
    Edit,
    UserPlus
} from 'lucide-react';
import { format } from 'date-fns';

const UserManagementPage = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const data = await adminGetUsers();
            setUsers(data.results);
        } catch (err) {
            console.error('Failed to fetch users', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const filteredUsers = users.filter(u =>
        u.email.toLowerCase().includes(search.toLowerCase()) ||
        u.full_name?.toLowerCase().includes(search.toLowerCase())
    );

    const toggleUserActive = async (user: User) => {
        try {
            await adminUpdateUser(user.id, { is_active: !user.is_active });
            setUsers(users.map(u => u.id === user.id ? { ...u, is_active: !u.is_active } : u));
        } catch (err) {
            console.error('Failed to update user', err);
        }
    };

    return (
        <AdminLayout>
            <div className="space-y-10 animate-fade-in">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <h2 className="text-4xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">Active Operatives</h2>
                        <p className="text-slate-500 font-medium italic">"The lifeblood of the platform. Monitor carefully."</p>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
                            <input
                                type="text"
                                placeholder="Search operatives..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-10 pr-4 py-3 bg-white dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500 rounded-2xl outline-none transition-all shadow-sm w-64 font-bold"
                            />
                        </div>
                        <button className="bg-emerald-600 hover:bg-emerald-700 text-white font-black px-6 py-3 rounded-2xl flex items-center space-x-2 shadow-xl shadow-emerald-600/20 active:scale-95 transition-all">
                            <UserPlus className="w-5 h-5" />
                            <span>Enlist Member</span>
                        </button>
                    </div>
                </div>

                {/* User Table */}
                <div className="bg-white dark:bg-slate-900 rounded-[3rem] border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50/50 dark:bg-slate-800/30 border-b border-slate-200 dark:border-slate-800">
                                <th className="px-8 py-6 text-xs font-black text-slate-400 uppercase tracking-widest">Operative</th>
                                <th className="px-8 py-6 text-xs font-black text-slate-400 uppercase tracking-widest">Status</th>
                                <th className="px-8 py-6 text-xs font-black text-slate-400 uppercase tracking-widest">Plan</th>
                                <th className="px-8 py-6 text-xs font-black text-slate-400 uppercase tracking-widest">Joined</th>
                                <th className="px-8 py-6 text-xs font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {loading ? (
                                [1, 2, 3].map(i => (
                                    <tr key={i} className="animate-pulse">
                                        <td colSpan={5} className="px-8 py-10 bg-slate-50/20 dark:bg-slate-800/10"></td>
                                    </tr>
                                ))
                            ) : filteredUsers.map((u) => (
                                <tr key={u.id} className="group hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors">
                                    <td className="px-8 py-6">
                                        <div className="flex items-center space-x-4">
                                            <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 dark:text-slate-400 font-black text-lg border border-slate-200 dark:border-slate-700">
                                                {u.email.charAt(0).toUpperCase()}
                                            </div>
                                            <div>
                                                <p className="font-black text-slate-900 dark:text-white leading-tight">
                                                    {u.full_name || 'Anonymous'}
                                                    {u.is_staff && <Shield className="inline-block w-4 h-4 ml-2 text-emerald-500" />}
                                                </p>
                                                <p className="text-xs font-bold text-slate-500 uppercase tracking-tight">{u.email}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        {u.is_active ? (
                                            <div className="inline-flex items-center space-x-1.5 text-emerald-500 font-black uppercase text-[10px] tracking-widest bg-emerald-500/10 px-3 py-1 rounded-full">
                                                <CheckCircle className="w-3.5 h-3.5" />
                                                <span>Active</span>
                                            </div>
                                        ) : (
                                            <div className="inline-flex items-center space-x-1.5 text-rose-500 font-black uppercase text-[10px] tracking-widest bg-rose-500/10 px-3 py-1 rounded-full">
                                                <XCircle className="w-3.5 h-3.5" />
                                                <span>Suspended</span>
                                            </div>
                                        )}
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className="text-sm font-black text-slate-600 dark:text-slate-300 uppercase tracking-widest">
                                            {u.profile?.subscription_plan?.name || 'Free'}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{u.date_joined ? format(new Date(u.date_joined), 'MMM dd, yyyy') : 'Unknown'}</span>
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Deployment Date</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <div className="flex items-center justify-end space-x-2">
                                            <button
                                                onClick={() => toggleUserActive(u)}
                                                className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 hover:bg-emerald-500 hover:text-white transition-all shadow-sm"
                                            >
                                                <Edit className="w-4 h-4" />
                                            </button>
                                            <button className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm">
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </AdminLayout>
    );
};

export default UserManagementPage;
