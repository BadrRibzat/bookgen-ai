'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { getDomainsOverview, getDomainWithData } from '@/lib/api/domains';
import { generateBook } from '@/lib/api/books';
import { Domain, Niche } from '@/shared/types';
import {
    Wand2,
    ChevronRight,
    ChevronLeft,
    CheckCircle2,
    Loader2,
    Sparkles
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';

const GenerationWizardPage = () => {
    const router = useRouter();
    const { refreshProfile } = useAuth();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [domains, setDomains] = useState<Domain[]>([]);
    const [niches, setNiches] = useState<Niche[]>([]);

    // Form State
    const [title, setTitle] = useState('');
    const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
    const [selectedNiche, setSelectedNiche] = useState<Niche | null>(null);
    const [selectedCover, setSelectedCover] = useState<string>('auto');
    const [status, setStatus] = useState<'idle' | 'generating' | 'success' | 'error'>('idle');
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchDomains = async () => {
            try {
                const data = await getDomainsOverview();
                setDomains(data);
            } catch (err) {
                console.error('Failed to fetch domains', err);
            }
        };
        fetchDomains();
    }, []);

    useEffect(() => {
        if (selectedDomain) {
            const fetchNiches = async () => {
                if (!selectedDomain?.id) {
                    console.warn('Cannot fetch niches: No domain ID selected');
                    return;
                }
                try {
                    const data = await getDomainWithData(selectedDomain.id);
                    setNiches(data.niches);
                } catch (err) {
                    console.error('Failed to fetch niches', err);
                }
            };
            fetchNiches();
        } else {
            setNiches([]);
        }
    }, [selectedDomain]);

    const handleNext = () => setStep(s => s + 1);
    const handleBack = () => setStep(s => s - 1);

    const handleStartGeneration = async () => {
        if (!selectedDomain || !title) return;

        setLoading(true);
        setStatus('generating');
        try {
            const result = await generateBook({
                title,
                domain_id: selectedDomain.id,
                niche_id: selectedNiche?.id,
                cover_option: selectedCover,
                target_word_count: 50000 // Default word count
            });

            if (result.success) {
                setStatus('success');
                await refreshProfile(); // Update usage count
                setTimeout(() => {
                    router.push('/dashboard/history');
                }, 2000);
            }
        } catch (err: any) {
            setStatus('error');
            setError(err.response?.data?.error?.message || 'Failed to start generation');
        } finally {
            setLoading(false);
        }
    };

    const progressPercentage = (step / 4) * 100;

    return (
        <DashboardLayout>
            <div className="max-w-4xl mx-auto py-6">
                {/* Progress Header */}
                <div className="mb-12">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-3xl font-black text-slate-900 dark:text-white flex items-center space-x-3">
                            <div className="p-2 bg-indigo-600 rounded-xl">
                                <Wand2 className="text-white w-6 h-6" />
                            </div>
                            <span>Create New Masterpiece</span>
                        </h2>
                        <div className="text-sm font-bold text-slate-500 uppercase tracking-widest">
                            Step {step} of 4
                        </div>
                    </div>
                    <div className="h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-indigo-600 transition-all duration-500 ease-out shadow-[0_0_15px_rgba(79,70,229,0.5)]"
                            style={{ width: `${progressPercentage}%` }}
                        ></div>
                    </div>
                </div>

                {/* Wizard Steps */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-10 shadow-2xl relative overflow-hidden group">

                    {/* Step 1: Concept & Domain */}
                    {step === 1 && (
                        <div className="space-y-8 animate-slide-up">
                            <div>
                                <label className="block text-sm font-black text-slate-500 uppercase tracking-widest mb-4">
                                    1. Give your book a title
                                </label>
                                <input
                                    type="text"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="e.g. The Future of Quantum Computing"
                                    className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-transparent focus:border-indigo-500 rounded-2xl px-6 py-4 text-xl font-bold text-slate-900 dark:text-white outline-none transition-all placeholder:text-slate-400"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-black text-slate-500 uppercase tracking-widest mb-4">
                                    2. Select your domain
                                </label>
                                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                                    {domains.map((d, idx) => (
                                        <button
                                            key={d.id || `domain-${idx}`}
                                            onClick={() => setSelectedDomain(d)}
                                            className={`p-6 rounded-3xl border-2 transition-all flex flex-col items-center justify-center space-y-3 ${selectedDomain?.id === d.id
                                                ? 'border-indigo-500 bg-indigo-500/10 text-indigo-500 scale-105 shadow-xl shadow-indigo-500/10'
                                                : 'border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:border-slate-300 dark:hover:border-slate-700'
                                                }`}
                                        >
                                            <span className="text-3xl">{d.icon}</span>
                                            <span className="text-xs font-black uppercase text-center">{d.name}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex justify-end pt-6">
                                <button
                                    disabled={!title || !selectedDomain}
                                    onClick={handleNext}
                                    className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-black px-10 py-4 rounded-2xl transition-all shadow-lg shadow-indigo-600/20 active:scale-95 flex items-center space-x-2"
                                >
                                    <span>Continue</span>
                                    <ChevronRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 2: Niche Selection */}
                    {step === 2 && (
                        <div className="space-y-8 animate-slide-up">
                            <div>
                                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2">Refine your vision</h3>
                                <p className="text-slate-500">Selected Domain: <span className="text-indigo-500 font-bold">{selectedDomain?.name}</span></p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {niches.map((n, idx) => (
                                    <button
                                        key={n.id || `niche-${idx}`}
                                        onClick={() => setSelectedNiche(n)}
                                        className={`p-6 rounded-3xl border-2 transition-all text-left flex items-start space-x-4 ${selectedNiche?.id === n.id
                                            ? 'border-indigo-500 bg-indigo-500/10 text-indigo-500'
                                            : 'border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:border-slate-300 dark:hover:border-slate-700'
                                            }`}
                                    >
                                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${selectedNiche?.id === n.id ? 'bg-indigo-500 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}>
                                            <Sparkles className="w-6 h-6" />
                                        </div>
                                        <div className="flex-1">
                                            <span className="block font-bold text-lg mb-1">{n.name}</span>
                                            <span className="block text-sm opacity-70 leading-relaxed">{n.description}</span>
                                        </div>
                                    </button>
                                ))}
                            </div>

                            <div className="flex justify-between pt-6">
                                <button
                                    onClick={handleBack}
                                    className="text-slate-500 font-bold px-6 py-4 rounded-2xl transition-all flex items-center space-x-2"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                    <span>Back</span>
                                </button>
                                <button
                                    onClick={handleNext}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-10 py-4 rounded-2xl transition-all shadow-lg flex items-center space-x-2"
                                >
                                    <span>Choose Cover</span>
                                    <ChevronRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 3: Cover Selection */}
                    {step === 3 && (
                        <div className="space-y-8 animate-slide-up">
                            <div>
                                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2">Choose your cover style</h3>
                                <p className="text-slate-500">Select how you'd like your book cover to be designed.</p>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                <button
                                    onClick={() => setSelectedCover('auto')}
                                    className={`p-8 rounded-3xl border-2 transition-all text-left ${selectedCover === 'auto'
                                        ? 'border-indigo-500 bg-indigo-500/10 text-indigo-500'
                                        : 'border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:border-slate-300 dark:hover:border-slate-700'
                                        }`}
                                >
                                    <div className="flex items-start space-x-4">
                                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${selectedCover === 'auto' ? 'bg-indigo-500 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}>
                                            <Sparkles className="w-8 h-8" />
                                        </div>
                                        <div className="flex-1">
                                            <span className="block font-bold text-xl mb-2">AI-Generated Cover</span>
                                            <span className="block text-sm opacity-80 leading-relaxed">Let our AI create a stunning, professional cover design tailored to your book's content and theme.</span>
                                        </div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => setSelectedCover('template')}
                                    className={`p-8 rounded-3xl border-2 transition-all text-left ${selectedCover === 'template'
                                        ? 'border-indigo-500 bg-indigo-500/10 text-indigo-500'
                                        : 'border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 hover:border-slate-300 dark:hover:border-slate-700'
                                        }`}
                                >
                                    <div className="flex items-start space-x-4">
                                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${selectedCover === 'template' ? 'bg-indigo-500 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}>
                                            <Wand2 className="w-8 h-8" />
                                        </div>
                                        <div className="flex-1">
                                            <span className="block font-bold text-xl mb-2">Template-Based Cover</span>
                                            <span className="block text-sm opacity-80 leading-relaxed">Choose from professionally designed templates and customize them to match your vision.</span>
                                        </div>
                                    </div>
                                </button>
                            </div>

                            <div className="flex justify-between pt-6">
                                <button
                                    onClick={handleBack}
                                    className="text-slate-500 font-bold px-6 py-4 rounded-2xl transition-all flex items-center space-x-2"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                    <span>Back</span>
                                </button>
                                <button
                                    onClick={handleNext}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-10 py-4 rounded-2xl transition-all shadow-lg flex items-center space-x-2"
                                >
                                    <span>Review & Generate</span>
                                    <ChevronRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 4: Review & Generate */}
                    {step === 4 && (
                        <div className="space-y-10 animate-slide-up">
                            <div className="text-center space-y-4">
                                <div className="w-20 h-20 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <Sparkles className="text-indigo-600 w-10 h-10" />
                                </div>
                                <h3 className="text-3xl font-black text-slate-900 dark:text-white">Ready to create magic?</h3>
                                <p className="text-slate-500 max-w-md mx-auto">Review your book details before our AI begins the generation process.</p>
                            </div>

                            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800 divide-y divide-slate-200 dark:divide-slate-800">
                                <div className="py-4 flex justify-between">
                                    <span className="text-slate-500 font-bold uppercase text-xs tracking-widest">Title</span>
                                    <span className="text-slate-900 dark:text-white font-black">{title}</span>
                                </div>
                                <div className="py-4 flex justify-between">
                                    <span className="text-slate-500 font-bold uppercase text-xs tracking-widest">Domain</span>
                                    <span className="text-indigo-500 font-black">{selectedDomain?.name}</span>
                                </div>
                                <div className="py-4 flex justify-between">
                                    <span className="text-slate-500 font-bold uppercase text-xs tracking-widest">Target Niche</span>
                                    <span className="text-slate-900 dark:text-white font-black">{selectedNiche?.name || 'Wide Domain'}</span>
                                </div>
                                <div className="py-4 flex justify-between">
                                    <span className="text-slate-500 font-bold uppercase text-xs tracking-widest">Cover Style</span>
                                    <span className="text-slate-900 dark:text-white font-black">
                                        {selectedCover === 'auto' ? 'AI-Generated' : 'Template-Based'}
                                    </span>
                                </div>
                            </div>

                            {status === 'error' && (
                                <div className="bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/50 rounded-2xl p-4 text-rose-600 dark:text-rose-400 text-center font-bold">
                                    {error}
                                </div>
                            )}

                            <div className="flex justify-between pt-6">
                                <button
                                    disabled={loading}
                                    onClick={handleBack}
                                    className="text-slate-500 font-bold px-6 py-4 rounded-2xl transition-all flex items-center space-x-2"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                    <span>Back</span>
                                </button>
                                <button
                                    disabled={loading}
                                    onClick={handleStartGeneration}
                                    className={`font-black px-12 py-5 rounded-3xl transition-all shadow-2xl flex items-center space-x-3 active:scale-95 ${status === 'success' ? 'bg-emerald-500 text-white' : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                                        }`}
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-6 h-6 animate-spin" />
                                            <span>Transmuting Ideas...</span>
                                        </>
                                    ) : status === 'success' ? (
                                        <>
                                            <CheckCircle2 className="w-6 h-6" />
                                            <span>Success! Redirecting...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-6 h-6" />
                                            <span className="text-xl">Generate Book</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Background decoration */}
                    <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 bg-indigo-500/5 blur-3xl rounded-full"></div>
                    <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-60 h-60 bg-violet-500/5 blur-3xl rounded-full"></div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default GenerationWizardPage;
