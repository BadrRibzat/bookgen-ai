import { apiClient } from './client';
import { Book, PaginatedResponse } from '@/shared/types';

export const getBookHistory = async (page = 1, perPage = 20) => {
    const response = await apiClient.get<PaginatedResponse<Book>>('/users/books-history/', {
        params: { page, per_page: perPage },
    });
    return response.data;
};

export interface GenerateBookPayload {
    title: string;
    domain_id: string;
    niche_id?: string;
    cover_option?: string;
    target_word_count?: number;
}

export const generateBook = async (payload: GenerateBookPayload) => {
    const response = await apiClient.post<{ success: boolean; book_id: string; message: string }>(
        '/generate/',
        payload
    );
    return response.data;
};

export const getBookDetails = async (bookId: string) => {
    const response = await apiClient.get<{ success: boolean; book: Book }>(`/generation-requests/${bookId}/`);
    return response.data;
};

export const getBookPreview = async (bookId: string) => {
    const response = await apiClient.get<{ 
        generation_request: Book; 
        book_content: any 
    }>(`/books/${bookId}/preview/`);
    return response.data;
};

export const deleteBook = async (bookId: string) => {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`/generation-requests/${bookId}/`);
    return response.data;
};
