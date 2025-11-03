/**
 * Domain details modal/page component
 * Shows detailed information about a domain including niches and audiences
 */

'use client';

import { useEffect, useState } from 'react';
import { Domain, Niche, Audience } from '@/shared/types';
import { getDomainWithData } from '@/lib/api/domains';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { X } from 'lucide-react';

interface DomainDetailsProps {
  domainId: string;
  onClose?: () => void;
  isModal?: boolean;
}

export function DomainDetails({ domainId, onClose, isModal = true }: DomainDetailsProps) {
  const [domain, setDomain] = useState<Domain | null>(null);
  const [niches, setNiches] = useState<Niche[]>([]);
  const [audiences, setAudiences] = useState<Audience[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDomainDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await getDomainWithData(domainId);
      setDomain(data.domain);
      setNiches(data.niches);
      setAudiences(data.audiences);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch domain details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (domainId) {
      fetchDomainDetails();
    }
  }, [domainId]);

  if (loading) {
    return (
      <div className={isModal ? "bg-white rounded-lg shadow-xl p-6 max-w-4xl mx-auto" : "space-y-6"}>
        <div className="flex items-center justify-between mb-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-48 mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-64"></div>
          </div>
          {isModal && onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          )}
        </div>
        
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={isModal ? "bg-white rounded-lg shadow-xl p-6 max-w-4xl mx-auto" : "space-y-6"}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Domain Details</h2>
          {isModal && onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          )}
        </div>
        
        <Alert 
          type="error" 
          message={error}
          title="Failed to load domain details"
        />
        
        <div className="mt-4">
          <Button onClick={fetchDomainDetails} variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (!domain) {
    return null;
  }

  const containerClass = isModal 
    ? "bg-white rounded-lg shadow-xl p-6 max-w-4xl mx-auto max-h-[80vh] overflow-y-auto"
    : "space-y-6";

  return (
    <div className={containerClass}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="text-4xl">{domain.icon}</div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{domain.name}</h2>
            <p className="text-gray-600">{domain.description}</p>
            <div className="flex items-center space-x-2 mt-2">
              <span className={`
                inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                ${domain.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
                }
              `}>
                {domain.is_active ? 'Active' : 'Inactive'}
              </span>
              <div className="flex space-x-1">
                {domain.subscription_tiers.map((tier) => (
                  <span
                    key={tier}
                    className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {tier}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
        {isModal && onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-primary-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-primary-600">{niches.length}</div>
          <div className="text-sm text-primary-700">Available Niches</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-600">{audiences.length}</div>
          <div className="text-sm text-green-700">Target Audiences</div>
        </div>
      </div>

      {/* Niches Section */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          Available Niches ({niches.length})
        </h3>
        {niches.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {niches.map((niche) => (
              <div
                key={niche.id}
                className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
              >
                <h4 className="font-medium text-gray-900">{niche.name}</h4>
                {niche.description && (
                  <p className="text-sm text-gray-600 mt-1">{niche.description}</p>
                )}
                <div className="flex justify-between items-center mt-2">
                  <span className={`
                    inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                    ${niche.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                    }
                  `}>
                    {niche.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(niche.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No niches available for this domain.
          </div>
        )}
      </div>

      {/* Audiences Section */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          Target Audiences ({audiences.length})
        </h3>
        {audiences.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {audiences.map((audience) => (
              <div
                key={audience.id}
                className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
              >
                <h4 className="font-medium text-gray-900">{audience.name}</h4>
                {audience.description && (
                  <p className="text-sm text-gray-600 mt-1">{audience.description}</p>
                )}
                <div className="flex justify-between items-center mt-2">
                  <span className={`
                    inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                    ${audience.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                    }
                  `}>
                    {audience.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(audience.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No audiences available for this domain.
          </div>
        )}
      </div>

      {/* Actions */}
      {isModal && (
        <div className="flex justify-end space-x-3 mt-8 pt-6 border-t">
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
          <Button>
            Start Creating Book
          </Button>
        </div>
      )}
    </div>
  );
}