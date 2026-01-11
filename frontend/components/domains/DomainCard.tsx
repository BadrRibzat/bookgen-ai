/**
 * Domain card component
 * Displays individual domain information with niches and audiences count
 */

import { Domain } from '@/shared/types';
import { Button } from '@/components/ui/Button';

interface DomainCardProps {
  domain: Domain & {
    nichesCount?: number;
    audiencesCount?: number;
  };
  onSelect?: (domain: Domain) => void;
  onViewDetails?: (domain: Domain) => void;
  isSelected?: boolean;
}

export function DomainCard({ 
  domain, 
  onSelect, 
  onViewDetails, 
  isSelected = false 
}: DomainCardProps) {
  return (
    <div 
      className={`
        bg-white rounded-lg border-2 transition-all duration-200 hover:shadow-lg cursor-pointer
        ${isSelected 
          ? 'border-primary-500 bg-primary-50' 
          : 'border-gray-200 hover:border-gray-300'
        }
      `}
      onClick={() => onSelect?.(domain)}
    >
      <div className="p-6">
        {/* Domain Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">{domain.icon}</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {domain.name}
              </h3>
              <p className="text-sm text-gray-600 line-clamp-2">
                {domain.description}
              </p>
            </div>
          </div>
          
          {/* Status indicator */}
          <div className={`
            inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
            ${domain.is_active 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
            }
          `}>
            {domain.is_active ? 'Active' : 'Inactive'}
          </div>
        </div>

        {/* Subscription Tiers */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {domain.subscription_tiers?.map((tier) => (
              <span
                key={tier}
                className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tier}
              </span>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {domain.nichesCount ?? '—'}
            </div>
            <div className="text-xs text-gray-500">Niches</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {domain.audiencesCount ?? '—'}
            </div>
            <div className="text-xs text-gray-500">Audiences</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <Button
            variant={isSelected ? "primary" : "outline"}
            size="sm"
            className="flex-1"
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(domain);
            }}
          >
            {isSelected ? 'Selected' : 'Select'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails?.(domain);
            }}
          >
            Details
          </Button>
        </div>
      </div>
    </div>
  );
}