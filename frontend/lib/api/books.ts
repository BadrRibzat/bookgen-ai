import { apiClient } from './client';
import { Book, PaginatedResponse } from '@/shared/types';

export const getBookHistory = async (page = 1, perPage = 20) => {
    const response = await apiClient.get<PaginatedResponse<Book>>('/books/history/', {
        params: { page, per_page: perPage },
    });
    return response.data;
};

export interface GenerateBookPayload {
    title: string;
    domain_id: string;
    niche_id?: string;
}

export const generateBook = async (payload: GenerateBookPayload) => {
    const response = await apiClient.post<{ success: boolean; book_id: string; message: string }>(
        '/books/generate/',
        payload
    );
    return response.data;
};

export const getBookDetails = async (bookId: string) => {
    const response = await apiClient.get<{ success: boolean; book: Book }>(`/books/${bookId}/`);
    return response.data;
};

export const deleteBook = async (bookId: string) => {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`/books/${bookId}/`);
    return response.data;
};
