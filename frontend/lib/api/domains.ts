import { apiClient } from './client';
import { Domain, Niche, Audience } from '@/shared/types';

export const getDomains = async (): Promise<Domain[]> => {
  const response = await apiClient.get<{ success: boolean; domains: Domain[] }>('/domains/');
  return response.data.domains;
};

export const getDomainsOverview = async (): Promise<(Domain & { nichesCount?: number; audiencesCount?: number })[]> => {
  const response = await apiClient.get<{ success: boolean; domains: any[] }>('/user/domains/');
  return response.data.domains.map(d => ({
    ...d,
    nichesCount: d.niches_count,
    audiencesCount: d.audiences_count
  }));
};

export const getDomainWithData = async (domainId: string): Promise<{ domain: Domain; niches: Niche[]; audiences: Audience[] }> => {
  const response = await apiClient.get<{ success: boolean; domain: Domain; niches: Niche[]; audiences: Audience[] }>(`/domains/${domainId}/details/`);
  return {
    domain: response.data.domain,
    niches: response.data.niches,
    audiences: response.data.audiences
  };
};
