'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Lock, Mail, AlertTriangle, ArrowRight } from 'lucide-react';
import { useAuth } from '@/lib/contexts/AuthContext';

export default function AdminLoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();
    const { adminLogin: authContextAdminLogin } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await authContextAdminLogin({ email, password });
            // Redirect happens in AuthContext
        } catch (err: any) {
            console.error('Admin login failed:', err);
            setError(err.message || 'Security clearance denied.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.1),transparent_50%)]"></div>
            <div className="absolute -top-40 -right-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px]"></div>
            <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px]"></div>

            <div className="w-full max-w-md animate-fade-in relative z-10">
                {/* Logo Section */}
                <div className="text-center mb-10">
                    <div className="w-20 h-20 bg-emerald-600 rounded-[2rem] flex items-center justify-center mx-auto shadow-2xl shadow-emerald-500/20 mb-6 group transition-all duration-500 hover:rotate-[360deg]">
                        <ShieldCheck className="text-white w-10 h-10" />
                    </div>
                    <h1 className="text-3xl font-black text-white tracking-tight mb-2 uppercase">BookGen Admin</h1>
                    <p className="text-emerald-500 font-bold text-xs uppercase tracking-[0.3em]">Authorized Personnel Only</p>
                </div>

                {/* Login Card */}
                <div className="bg-slate-900/40 backdrop-blur-3xl border border-emerald-500/20 p-10 rounded-[2.5rem] shadow-2xl relative">
                    {error && (
                        <div className="mb-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-center space-x-3 text-rose-400 animate-shake">
                            <AlertTriangle className="w-5 h-5 shrink-0" />
                            <p className="text-sm font-bold">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-4">Deployment ID (Email)</label>
                            <div className="relative group">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="operative@bookgen.ai"
                                    className="w-full pl-12 pr-4 py-4 bg-slate-950/50 border-2 border-slate-800 rounded-2xl outline-none focus:border-emerald-500 text-white font-bold transition-all placeholder:text-slate-700"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-4">Security Key (Password)</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full pl-12 pr-4 py-4 bg-slate-950/50 border-2 border-slate-800 rounded-2xl outline-none focus:border-emerald-500 text-white font-bold transition-all placeholder:text-slate-700"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-2xl transition-all shadow-xl shadow-emerald-600/20 flex items-center justify-center space-x-2 group ${loading ? 'opacity-70 cursor-not-allowed' : 'active:scale-95'}`}
                        >
                            {loading ? (
                                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    <span>Grant Clearance</span>
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>
                </div>

                <div className="mt-8 text-center">
                    <button
                        onClick={() => router.push('/auth/login')}
                        className="text-slate-500 hover:text-white transition-colors text-xs font-bold uppercase tracking-widest"
                    >
                        Return to Civilian Portal
                    </button>
                </div>
            </div>
        </div>
    );
}
