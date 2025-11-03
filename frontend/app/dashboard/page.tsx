/**
 * Dashboard page with domains integration
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { DomainsGrid } from '@/components/domains/DomainsGrid';
import { DomainDetails } from '@/components/domains/DomainDetails';
import { Modal } from '@/components/ui/Modal';
import { Domain } from '@/shared/types';

export default function DashboardPage() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const [showDomainDetails, setShowDomainDetails] = useState(false);
  const [detailsDomainId, setDetailsDomainId] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [loading, isAuthenticated, router]);

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-3">
              <img 
                src="/logo-icon.svg" 
                alt="BookGen-AI Logo" 
                className="h-8 w-8 text-primary-600"
              />
              <h1 className="text-2xl font-bold text-primary-600">BookGen-AI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">{user.email}</span>
              <Button onClick={logout} variant="outline" size="sm">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Welcome Section */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome, {user.full_name || user.email}! 🎉
          </h2>
          <p className="text-gray-600 mb-6">
            Your AI-powered book generation platform is ready. Choose a domain below to start creating!
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-primary-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-primary-900 mb-2">
                Books Generated
              </h3>
              <p className="text-3xl font-bold text-primary-600">
                {user.profile.total_books_generated}
              </p>
            </div>

            <div className="bg-green-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                Words Written
              </h3>
              <p className="text-3xl font-bold text-green-600">
                {user.profile.total_words_written.toLocaleString()}
              </p>
            </div>

            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                Subscription
              </h3>
              <p className="text-3xl font-bold text-blue-600 capitalize">
                {user.profile.subscription_tier}
              </p>
            </div>
          </div>

          {!user.email_verified && (
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                ⚠️ Please verify your email address to access all features.
              </p>
            </div>
          )}
        </div>

        {/* Domains Section */}
        <div className="bg-white rounded-lg shadow p-8">
          <DomainsGrid 
            onDomainSelect={handleDomainSelect}
            onViewDetails={handleViewDetails}
            selectedDomainId={selectedDomain?.id}
            showOverview={true}
          />
          
          {/* Quick Actions */}
          {selectedDomain && (
            <div className="mt-8 p-6 bg-primary-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{selectedDomain.icon}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-primary-900">
                      Ready to create in {selectedDomain.name}?
                    </h3>
                    <p className="text-primary-700">
                      {selectedDomain.description}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-3">
                  <Button 
                    variant="outline" 
                    onClick={() => handleViewDetails(selectedDomain)}
                  >
                    View Details
                  </Button>
                  <Button>
                    Start Creating Book
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
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
    </div>
  );
}
