'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/contexts/AuthContext';
import { getSubscriptionPlans } from '@/lib/api/users';
import Navigation from '@/components/Navigation';
import {
    Check,
    Star,
    Zap,
    Crown,
    Building2,
    ArrowRight,
    Loader2,
    Users,
    BookOpen,
    Shield,
    Globe,
    TrendingUp
} from 'lucide-react';

interface SubscriptionPlan {
    id: number;
    name: string;
    slug: string;
    price: string;
    book_limit_per_month: number;
    features: {
        domains: string[];
        pdf_quality?: string;
        cover_customization?: string;
        social_media_formatting?: boolean;
        branding?: string;
        cover_designs?: string;
        team_collaboration?: number;
        api_access?: string;
        commercial_rights?: boolean;
        analytics?: string;
        account_manager?: boolean;
        ai_model_training?: string;
        security?: string;
        workflow_integration?: string;
        slas?: boolean;
        support: string;
        max_pages?: number;
        commercial_use: boolean;
    };
}

const planIcons = {
    personal: Star,
    creator: Zap,
    professional: Crown,
    entrepreneur: Building2,
    enterprise: Globe,
};

const planColors = {
    personal: 'from-blue-500 to-indigo-600',
    creator: 'from-purple-500 to-pink-600',
    professional: 'from-emerald-500 to-teal-600',
    entrepreneur: 'from-orange-500 to-red-600',
    enterprise: 'from-gray-700 to-gray-900',
};

const SubscriptionsPage = () => {
    const { user } = useAuth();
    const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPlans = async () => {
            try {
                const data = await getSubscriptionPlans();
                setPlans(data);
            } catch (err) {
                console.error('Failed to fetch plans', err);
            } finally {
                setLoading(false);
            }
        };
        fetchPlans();
    }, []);

    const formatPrice = (price: string) => {
        const numPrice = parseFloat(price);
        return numPrice === 0 ? 'Free' : `$${numPrice}`;
    };

    const getPlanIcon = (slug: string) => {
        const IconComponent = planIcons[slug as keyof typeof planIcons] || Star;
        return IconComponent;
    };

    const getPlanColor = (slug: string) => {
        return planColors[slug as keyof typeof planColors] || 'from-blue-500 to-indigo-600';
    };

    const renderFeatureList = (plan: SubscriptionPlan) => {
        const features = plan.features;
        const featureItems = [];

        if (features.domains) {
            featureItems.push(
                <li key="domains" className="flex items-start space-x-3">
                    <Check className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        <strong>Domains:</strong> {Array.isArray(features.domains) ? features.domains.join(', ') : features.domains}
                    </span>
                </li>
            );
        }

        if (plan.book_limit_per_month) {
            const limit = plan.book_limit_per_month === -1 ? 'Unlimited' : plan.book_limit_per_month;
            featureItems.push(
                <li key="books" className="flex items-start space-x-3">
                    <BookOpen className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        <strong>{limit} books</strong> per month
                    </span>
                </li>
            );
        }

        if (features.pdf_quality) {
            featureItems.push(
                <li key="pdf" className="flex items-start space-x-3">
                    <Check className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        <strong>{features.pdf_quality}</strong> PDF quality
                    </span>
                </li>
            );
        }

        if (features.cover_customization || features.cover_designs) {
            const coverText = features.cover_designs || features.cover_customization;
            featureItems.push(
                <li key="covers" className="flex items-start space-x-3">
                    <Check className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        <strong>{coverText}</strong> cover designs
                    </span>
                </li>
            );
        }

        if (features.social_media_formatting) {
            featureItems.push(
                <li key="social" className="flex items-start space-x-3">
                    <Check className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        Social media formatting included
                    </span>
                </li>
            );
        }

        if (features.team_collaboration) {
            featureItems.push(
                <li key="team" className="flex items-start space-x-3">
                    <Users className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        Team collaboration ({features.team_collaboration} seats)
                    </span>
                </li>
            );
        }

        if (features.api_access) {
            featureItems.push(
                <li key="api" className="flex items-start space-x-3">
                    <Shield className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        <strong>{features.api_access}</strong> API access
                    </span>
                </li>
            );
        }

        if (features.commercial_rights) {
            featureItems.push(
                <li key="commercial" className="flex items-start space-x-3">
                    <TrendingUp className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        Full commercial rights
                    </span>
                </li>
            );
        }

        if (features.account_manager) {
            featureItems.push(
                <li key="manager" className="flex items-start space-x-3">
                    <Users className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        Dedicated account manager
                    </span>
                </li>
            );
        }

        if (features.support) {
            featureItems.push(
                <li key="support" className="flex items-start space-x-3">
                    <Check className="text-green-500 w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-600 dark:text-slate-300">
                        <strong>{features.support}</strong> support
                    </span>
                </li>
            );
        }

        return featureItems;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
                <div className="flex flex-col items-center space-y-4">
                    <Loader2 className="w-12 h-12 animate-spin text-indigo-600" />
                    <p className="text-slate-600 dark:text-slate-300 font-medium">Loading subscription plans...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
            {/* Navigation */}
            <Navigation />

            {/* Header */}
            <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="text-center">
                        <h1 className="text-5xl font-black text-slate-900 dark:text-white mb-6 tracking-tight">
                            Choose Your Plan
                        </h1>
                        <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
                            Unlock your creativity with AI-powered book generation. Choose the perfect plan for your needs,
                            from personal projects to enterprise solutions.
                        </p>
                    </div>
                </div>
            </div>

            {/* Plans Grid */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {plans.map((plan) => {
                        const IconComponent = getPlanIcon(plan.slug);
                        const isCurrentPlan = user?.profile?.subscription_plan?.id === plan.id;
                        const gradientClass = getPlanColor(plan.slug);

                        return (
                            <div
                                key={plan.id}
                                className={`relative bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-xl border-2 transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 ${
                                    isCurrentPlan
                                        ? 'border-indigo-500 shadow-indigo-500/20'
                                        : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                                }`}
                            >
                                {isCurrentPlan && (
                                    <div className={`absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r ${gradientClass} text-white px-6 py-2 rounded-full text-sm font-bold shadow-lg`}>
                                        Current Plan
                                    </div>
                                )}

                                <div className="p-8">
                                    {/* Plan Header */}
                                    <div className="text-center mb-8">
                                        <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r ${gradientClass} rounded-2xl mb-4 shadow-lg`}>
                                            <IconComponent className="text-white w-8 h-8" />
                                        </div>
                                        <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2">
                                            {plan.name}
                                        </h3>
                                        <div className="flex items-baseline justify-center space-x-1">
                                            <span className="text-4xl font-black text-slate-900 dark:text-white">
                                                {formatPrice(plan.price)}
                                            </span>
                                            {parseFloat(plan.price) > 0 && (
                                                <span className="text-slate-500 font-medium">/month</span>
                                            )}
                                        </div>
                                    </div>

                                    {/* Features */}
                                    <ul className="space-y-4 mb-8">
                                        {renderFeatureList(plan)}
                                    </ul>

                                    {/* CTA Button */}
                                    <div className="text-center">
                                        {user ? (
                                            isCurrentPlan ? (
                                                <div className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-6 py-3 rounded-2xl font-bold">
                                                    Current Plan
                                                </div>
                                            ) : (
                                                <Link
                                                    href="/dashboard/settings"
                                                    className={`inline-flex items-center space-x-2 bg-gradient-to-r ${gradientClass} text-white px-8 py-4 rounded-2xl font-black transition-all hover:shadow-lg active:scale-95`}
                                                >
                                                    <span>Upgrade Now</span>
                                                    <ArrowRight className="w-5 h-5" />
                                                </Link>
                                            )
                                        ) : (
                                            <Link
                                                href="/auth/register"
                                                className={`inline-flex items-center space-x-2 bg-gradient-to-r ${gradientClass} text-white px-8 py-4 rounded-2xl font-black transition-all hover:shadow-lg active:scale-95`}
                                            >
                                                <span>Get Started</span>
                                                <ArrowRight className="w-5 h-5" />
                                            </Link>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Bottom CTA */}
                <div className="text-center mt-16">
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-[2.5rem] p-12 text-white">
                        <h2 className="text-3xl font-black mb-4">Need a Custom Solution?</h2>
                        <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
                            Our Enterprise plan offers custom AI model training, dedicated support, and tailored workflows
                            for your organization's unique needs.
                        </p>
                        <Link
                            href="/auth/register"
                            className="inline-flex items-center space-x-2 bg-white text-indigo-600 px-8 py-4 rounded-2xl font-black transition-all hover:shadow-lg active:scale-95"
                        >
                            <span>Contact Sales</span>
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SubscriptionsPage;