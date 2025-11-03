/**
 * Domains grid component
 * Displays all available domains in a responsive grid
 */

'use client';

import { useEffect, useState } from 'react';
import { Domain } from '@/shared/types';
import { getDomains, getDomainsOverview } from '@/lib/api/domains';
import { DomainCard } from './DomainCard';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';

interface DomainsGridProps {
  onDomainSelect?: (domain: Domain) => void;
  onViewDetails?: (domain: Domain) => void;
  selectedDomainId?: string;
  showOverview?: boolean;
}

export function DomainsGrid({ 
  onDomainSelect, 
  onViewDetails,
  selectedDomainId,
  showOverview = true 
}: DomainsGridProps) {
  const [domains, setDomains] = useState<(Domain & { nichesCount?: number; audiencesCount?: number })[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);

  const fetchDomains = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (showOverview) {
        // Fetch domains with counts
        const domainsWithCounts = await getDomainsOverview();
        setDomains(domainsWithCounts);
      } else {
        // Just fetch domains list
        const domainsList = await getDomains();
        setDomains(domainsList);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch domains');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, [showOverview]);

  const handleDomainSelect = (domain: Domain) => {
    setSelectedDomain(domain);
    onDomainSelect?.(domain);
  };

  const handleViewDetails = (domain: Domain) => {
    // Callback to parent component to handle modal opening
    onViewDetails?.(domain);
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Available Domains</h2>
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
        </div>
        
        {/* Loading skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg border-2 border-gray-200 p-6">
              <div className="animate-pulse">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-gray-300 rounded"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-300 rounded w-24"></div>
                    <div className="h-3 bg-gray-300 rounded w-32"></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-300 rounded w-full"></div>
                  <div className="h-3 bg-gray-300 rounded w-3/4"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Available Domains</h2>
          <Button onClick={fetchDomains} size="sm" variant="outline">
            Retry
          </Button>
        </div>
        
        <Alert 
          type="error" 
          message={error}
          title="Failed to load domains"
        />
        <div className="mt-4">
          <Button onClick={fetchDomains} size="sm" variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (domains.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-6xl mb-4">📚</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Domains Available</h3>
        <p className="text-gray-600">
          No domains are available for your subscription tier.
        </p>
        <Button onClick={fetchDomains} className="mt-4" variant="outline">
          Refresh
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Available Domains</h2>
          <p className="text-gray-600">
            Choose from {domains.length} domain{domains.length !== 1 ? 's' : ''} available for your subscription
          </p>
        </div>
        <Button onClick={fetchDomains} size="sm" variant="outline">
          Refresh
        </Button>
      </div>

      {/* Selected domain info */}
      {selectedDomain && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">{selectedDomain.icon}</div>
            <div>
              <h3 className="font-medium text-primary-900">
                Selected: {selectedDomain.name}
              </h3>
              <p className="text-sm text-primary-700">
                {selectedDomain.description}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Domains grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {domains.map((domain) => (
          <DomainCard
            key={domain.id}
            domain={domain}
            onSelect={handleDomainSelect}
            onViewDetails={handleViewDetails}
            isSelected={selectedDomainId === domain.id || selectedDomain?.id === domain.id}
          />
        ))}
      </div>

      {/* Summary */}
      {showOverview && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Domain Summary</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{domains.length}</div>
              <div className="text-sm text-gray-600">Total Domains</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {domains.reduce((sum, d) => sum + (d.nichesCount || 0), 0)}
              </div>
              <div className="text-sm text-gray-600">Total Niches</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {domains.reduce((sum, d) => sum + (d.audiencesCount || 0), 0)}
              </div>
              <div className="text-sm text-gray-600">Total Audiences</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}