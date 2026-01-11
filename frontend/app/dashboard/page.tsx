'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { DomainsGrid } from '@/components/domains/DomainsGrid';
import { DomainDetails } from '@/components/domains/DomainDetails';
import { Modal } from '@/components/ui/Modal';
import { Domain } from '@/shared/types';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import StatCard from '@/components/dashboard/StatCard';
import {
  BookCopy,
  FileText,
  ShieldCheck,
  AlertCircle,
  Zap
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const [showDomainDetails, setShowDomainDetails] = useState(false);
  const [detailsDomainId, setDetailsDomainId] = useState<string | null>(null);

  const handleDomainSelect = (domain: Domain) => {
    setSelectedDomain(domain);
  };

  const handleViewDetails = (domain: Domain) => {
    setDetailsDomainId(domain.id);
    setShowDomainDetails(true);
  };

  const handleCloseDetails = () => {
    setShowDomainDetails(false);
    setDetailsDomainId(null);
  };

  if (!user) return null;

  const planName = user.profile?.subscription_plan?.name || 'Free';
  const remaining = user.usage_summary?.remaining_books ?? 0;

  return (
    <DashboardLayout>
      <div className="space-y-10 animate-fade-in">
        {/* Welcome & Highlights */}
        <section>
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              Welcome back, {user.first_name || 'Author'}! 👋
            </h2>
            <p className="text-slate-500 dark:text-slate-400">
              Here is what is happening with your writing projects today.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              label="Books Created"
              value={user.profile?.total_books_generated || 0}
              icon={BookCopy}
              color="indigo"
              trend={{ value: 12, isPositive: true }}
            />
            <StatCard
              label="Words Written"
              value={(user.profile?.total_words_written || 0).toLocaleString()}
              icon={FileText}
              color="emerald"
            />
            <StatCard
              label="Credits (Remaining)"
              value={remaining}
              icon={Zap}
              color="amber"
            />
            <StatCard
              label="Account Shield"
              value={planName}
              icon={ShieldCheck}
              color="rose"
            />
          </div>
        </section>

        {/* Verification Alert */}
        {!user.email_verified && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-3xl p-6 flex items-start space-x-4 shadow-sm">
            <div className="bg-amber-100 dark:bg-amber-900/40 p-2 rounded-xl">
              <AlertCircle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <h4 className="font-bold text-amber-900 dark:text-amber-300">Email Verification Required</h4>
              <p className="text-sm text-amber-700 dark:text-amber-400/80 mb-3">
                Please verify your email address to unlock unlimited book exports and premium sharing features.
              </p>
              <button className="text-sm font-bold text-amber-900 dark:text-amber-300 hover:underline">
                Resend Verification Email →
              </button>
            </div>
          </div>
        )}

        {/* Domains Explorer */}
        <section className="bg-white dark:bg-slate-800/50 rounded-[2.5rem] p-10 shadow-sm border border-slate-100 dark:border-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">Explore Writing Domains</h3>
              <p className="text-slate-500 dark:text-slate-400">Choose a specialized niche to start your next masterpiece.</p>
            </div>
          </div>

          <DomainsGrid
            onDomainSelect={handleDomainSelect}
            onViewDetails={handleViewDetails}
            selectedDomainId={selectedDomain?.id}
            showOverview={true}
          />
        </section>
      </div>

      {/* Domain Details Modal */}
      <Modal isOpen={showDomainDetails} onClose={handleCloseDetails}>
        {detailsDomainId && (
          <DomainDetails
            domainId={detailsDomainId}
            onClose={handleCloseDetails}
            isModal={true}
          />
        )}
      </Modal>
    </DashboardLayout>
  );
}
