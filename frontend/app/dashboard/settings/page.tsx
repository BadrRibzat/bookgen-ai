'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { useAuth } from '@/lib/contexts/AuthContext';
import { updateCurrentUser, getSubscriptionPlans, deleteAccount, changePassword } from '@/lib/api/users';
import UsageMeter from '@/components/dashboard/UsageMeter';
import {
    User,
    CreditCard,
    ShieldAlert,
    Shield,
    Check,
    Loader2,
    Trash2,
    Mail,
    Zap
} from 'lucide-react';
import { Alert } from '@/components/ui/Alert';

const SettingsPage = () => {
    const { user, refreshProfile, logout } = useAuth();
    const [plans, setPlans] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    // Form State
    const [formData, setFormData] = useState({
        first_name: user?.first_name || '',
        last_name: user?.last_name || '',
        email: user?.email || '',
    });

    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        new_password_confirm: '',
    });

    useEffect(() => {
        const fetchPlans = async () => {
            try {
                const data = await getSubscriptionPlans();
                setPlans(data);
            } catch (err) {
                console.error('Failed to fetch plans', err);
            }
        };
        fetchPlans();
    }, []);

    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');
        try {
            await updateCurrentUser(formData);
            await refreshProfile();
            setSuccess('Profile updated successfully!');
        } catch (err: any) {
            setError(err.message || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (window.confirm('WARNING: This will permanently deactivate your account. Are you sure?')) {
            try {
                await deleteAccount();
                alert('Account deleted. You will be logged out.');
                logout();
            } catch (err: any) {
                setError(err.message || 'Failed to delete account');
            }
        }
    };

    const handleChangePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');
        
        if (passwordData.new_password !== passwordData.new_password_confirm) {
            setError('New passwords do not match');
            setLoading(false);
            return;
        }

        try {
            await changePassword(passwordData);
            setSuccess('Password changed successfully!');
            setPasswordData({
                current_password: '',
                new_password: '',
                new_password_confirm: '',
            });
        } catch (err: any) {
            setError(err.message || 'Failed to change password');
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;

    return (
        <DashboardLayout>
            <div className="max-w-5xl mx-auto space-y-10 animate-fade-in">
                <div>
                    <h2 className="text-4xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">Settings</h2>
                    <p className="text-slate-500 font-medium">Manage your profile, preferences, and subscription.</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    {/* Left Column: Forms */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Profile Section */}
                        <section className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 shadow-sm border border-slate-100 dark:border-slate-800">
                            <div className="flex items-center space-x-3 mb-8">
                                <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl">
                                    <User className="text-indigo-600 w-5 h-5" />
                                </div>
                                <h3 className="text-xl font-black text-slate-800 dark:text-white">Personal Information</h3>
                            </div>

                            <form onSubmit={handleUpdateProfile} className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest pl-1">First Name</label>
                                        <input
                                            type="text"
                                            value={formData.first_name}
                                            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                            className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-indigo-500 rounded-2xl px-5 py-3 font-bold text-slate-900 dark:text-white outline-none transition-all"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest pl-1">Last Name</label>
                                        <input
                                            type="text"
                                            value={formData.last_name}
                                            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                            className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-indigo-500 rounded-2xl px-5 py-3 font-bold text-slate-900 dark:text-white outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-black text-slate-500 uppercase tracking-widest pl-1">Email Address</label>
                                    <div className="relative">
                                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                        <input
                                            type="email"
                                            value={formData.email}
                                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                            className="w-full pl-12 pr-5 py-3 bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-indigo-500 rounded-2xl font-bold text-slate-900 dark:text-white outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                {success && <Alert type="success" message={success} />}
                                {error && <Alert type="error" message={error} />}

                                <div className="pt-4">
                                    <button
                                        disabled={loading}
                                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-8 py-3.5 rounded-2xl transition-all shadow-lg flex items-center space-x-2 active:scale-95 disabled:opacity-50"
                                    >
                                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                                        <span>Save Changes</span>
                                    </button>
                                </div>
                            </form>
                        </section>

                        {/* Password Section */}
                        <section className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 shadow-sm border border-slate-100 dark:border-slate-800">
                            <div className="flex items-center space-x-3 mb-8">
                                <div className="p-2 bg-amber-50 dark:bg-amber-900/30 rounded-xl">
                                    <Shield className="text-amber-600 w-5 h-5" />
                                </div>
                                <h3 className="text-xl font-black text-slate-800 dark:text-white">Change Password</h3>
                            </div>

                            <form onSubmit={handleChangePassword} className="space-y-6">
                                <div className="space-y-2">
                                    <label className="text-xs font-black text-slate-500 uppercase tracking-widest pl-1">Current Password</label>
                                    <input
                                        type="password"
                                        value={passwordData.current_password}
                                        onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                                        className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-amber-500 rounded-2xl px-5 py-3 font-bold text-slate-900 dark:text-white outline-none transition-all"
                                        required
                                    />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest pl-1">New Password</label>
                                        <input
                                            type="password"
                                            value={passwordData.new_password}
                                            onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                                            className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-amber-500 rounded-2xl px-5 py-3 font-bold text-slate-900 dark:text-white outline-none transition-all"
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-black text-slate-500 uppercase tracking-widest pl-1">Confirm New Password</label>
                                        <input
                                            type="password"
                                            value={passwordData.new_password_confirm}
                                            onChange={(e) => setPasswordData({ ...passwordData, new_password_confirm: e.target.value })}
                                            className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-amber-500 rounded-2xl px-5 py-3 font-bold text-slate-900 dark:text-white outline-none transition-all"
                                            required
                                        />
                                    </div>
                                </div>

                                {success && <Alert type="success" message={success} />}
                                {error && <Alert type="error" message={error} />}

                                <div className="pt-4">
                                    <button
                                        disabled={loading}
                                        className="bg-amber-600 hover:bg-amber-700 text-white font-black px-8 py-3.5 rounded-2xl transition-all shadow-lg flex items-center space-x-2 active:scale-95 disabled:opacity-50"
                                    >
                                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                                        <span>Change Password</span>
                                    </button>
                                </div>
                            </form>
                        </section>

                        {/* Danger Zone */}
                        <section className="bg-rose-50/50 dark:bg-rose-950/10 rounded-[2.5rem] p-8 border border-rose-100 dark:border-rose-900/30">
                            <div className="flex items-center space-x-3 mb-6">
                                <div className="p-2 bg-rose-100 dark:bg-rose-900/40 rounded-xl">
                                    <ShieldAlert className="text-rose-600 w-5 h-5" />
                                </div>
                                <h3 className="text-xl font-black text-rose-900 dark:text-rose-300">Danger Zone</h3>
                            </div>
                            <p className="text-sm text-rose-700 dark:text-rose-400/80 mb-6 font-medium">
                                Once you delete your account, there is no going back. Please be certain.
                            </p>
                            <button
                                onClick={handleDeleteAccount}
                                className="bg-rose-600 hover:bg-rose-700 text-white font-black px-8 py-4 rounded-2xl transition-all flex items-center space-x-2 shadow-xl shadow-rose-600/20 active:scale-95"
                            >
                                <Trash2 className="w-5 h-5" />
                                <span>Delete Account Permanently</span>
                            </button>
                        </section>
                    </div>

                    {/* Right Column: Subscription & Usage */}
                    <div className="space-y-8">
                        <section className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 shadow-sm border border-slate-100 dark:border-slate-800">
                            <div className="flex items-center space-x-3 mb-8">
                                <div className="p-2 bg-amber-50 dark:bg-amber-900/30 rounded-xl">
                                    <CreditCard className="text-amber-600 w-5 h-5" />
                                </div>
                                <h3 className="text-xl font-black text-slate-800 dark:text-white">Active Plan</h3>
                            </div>

                            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-3xl p-6 border border-slate-100 dark:border-slate-800 mb-8 relative overflow-hidden group">
                                <div className="relative z-10">
                                    <span className="text-xs font-black text-indigo-500 uppercase tracking-widest mb-1 block">Your tier</span>
                                    <h4 className="text-3xl font-black text-slate-900 dark:text-white capitalize">
                                        {user.is_staff ? 'Admin (Unlimited)' : (user.profile?.subscription_plan?.name || 'No Plan')}
                                    </h4>
                                    <p className="text-sm font-bold text-slate-400 mt-1">
                                        {user.is_staff ? 'Full access' : 'Billed monthly'}
                                    </p>
                                </div>
                                <Zap className="absolute -right-4 -bottom-4 w-24 h-24 text-indigo-500/10 group-hover:scale-110 transition-transform" />
                            </div>

                            <UsageMeter
                                label="Monthly Book Credits"
                                current={user.profile?.current_month_book_count || 0}
                                total={user.is_staff ? -1 : (user.profile?.subscription_plan?.book_limit_per_month || 1)}
                            />

                            {!user.is_staff && (
                                <div className="mt-8 pt-8 border-t border-slate-100 dark:border-slate-800">
                                    <h5 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Available Upgrades</h5>
                                    <div className="space-y-3">
                                        {plans && plans.length > 0 && plans.filter(p => p.id !== user.profile?.subscription_plan?.id).map(p => (
                                            <button
                                                key={p.id}
                                                className="w-full flex items-center justify-between p-4 rounded-2xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors group"
                                            >
                                                <div className="text-left">
                                                    <p className="font-black text-slate-800 dark:text-white uppercase text-xs">{p.name}</p>
                                                    <p className="text-xs text-slate-400 font-bold">{p.book_limit_per_month} books / mo</p>
                                                </div>
                                                <div className="text-indigo-600 font-black text-sm group-hover:scale-110 transition-transform">
                                                    Upgrade →
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </section>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default SettingsPage;
