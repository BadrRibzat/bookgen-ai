import type { User, UserAnalytics, Book } from '@/shared/types';
import { apiClient, extractErrorMessage } from '@/lib/api/client';

export interface UpdateUserProfilePayload {
  first_name?: string;
  last_name?: string;
  email?: string;
  theme?: 'light' | 'dark';
  email_notifications?: boolean;
  marketing_emails?: boolean;
}

export interface BooksHistoryResponse {
  success: boolean;
  books: Book[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface AnalyticsResponse {
  success: boolean;
  analytics: UserAnalytics;
}

function buildError(error: unknown): Error {
  return new Error(extractErrorMessage(error));
}

export async function getCurrentUser(): Promise<User> {
  try {
    const { data } = await apiClient.get<{ success: boolean; user: User }>('/users/profile/');
    return data.user;
  } catch (error) {
    throw buildError(error);
  }
}

export async function updateCurrentUser(payload: UpdateUserProfilePayload): Promise<User> {
  try {
    const { data } = await apiClient.patch<{ success: boolean; user: User; message: string }>(
      '/users/profile/',
      payload
    );
    return data.user;
  } catch (error) {
    throw buildError(error);
  }
}

export async function getUserAnalytics(): Promise<UserAnalytics> {
  try {
    const { data } = await apiClient.get<AnalyticsResponse>('/users/analytics/');
    return data.analytics;
  } catch (error) {
    throw buildError(error);
  }
}

export async function getBooksHistory(page = 1): Promise<BooksHistoryResponse> {
  try {
    const { data } = await apiClient.get<BooksHistoryResponse>('/users/books-history/', {
      params: { page },
    });
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export async function getSubscriptionPlans() {
  try {
    const { data } = await apiClient.get<{ success: boolean; plans: any[] }>('/users/plans/');
    return data.plans;
  } catch (error) {
    throw buildError(error);
  }
}

export async function deleteAccount() {
  try {
    const { data } = await apiClient.delete<{ success: boolean; message: string }>('/users/profile/');
    return data;
  } catch (error) {
    throw buildError(error);
  }
}
