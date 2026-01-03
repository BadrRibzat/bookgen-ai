import { apiClient } from './client';
import { User, Book } from '@/shared/types';

export const adminGetUsers = async () => {
    const response = await apiClient.get<{ count: number; next: string; previous: string; results: User[] }>('/management-secure/users/');
    return response.data;
};

export const adminGetBooks = async () => {
    const response = await apiClient.get<{ success: boolean; books: Book[] }>('/management-secure/books/');
    return response.data.books;
};

export interface AdminAnalytics {
    users: {
        total: number;
        active: number;
        new_this_month: number;
    };
    books: {
        total_generated: number;
        processing: number;
        failed: number;
    };
    revenue: {
        estimated_monthly: number;
        currency: string;
    };
}

export const adminGetAnalytics = async (): Promise<AdminAnalytics> => {
    const response = await apiClient.get<{ success: boolean; analytics: AdminAnalytics }>('/management-secure/analytics/');
    return response.data.analytics;
};

export const adminUpdateUser = async (userId: string, payload: Partial<User>) => {
    const response = await apiClient.patch<{ success: boolean; user: User }>(`/management-secure/users/${userId}/`, payload);
    return response.data;
};

export const adminDeleteUser = async (userId: string) => {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`/management-secure/users/${userId}/`);
    return response.data;
};
