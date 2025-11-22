import type {
  AuthResponse,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  PasswordResetRequest,
  PasswordResetConfirm,
} from '@/shared/types';
import { apiClient, storeTokens, clearTokens, extractErrorMessage } from '@/lib/api/client';

export interface ApiRequestError extends Error {
  status?: number;
  details?: Record<string, string[]>;
}

function buildError(error: unknown): ApiRequestError {
  const message = extractErrorMessage(error);
  const enriched: ApiRequestError = new Error(message);

  if (typeof error === 'object' && error && 'response' in error) {
    const response = (error as any).response;
    enriched.status = response?.status;
    enriched.details = response?.data?.error?.details || response?.data?.details;
  }

  return enriched;
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  try {
    const { data } = await apiClient.post<AuthResponse>('/auth/login/', credentials);
    storeTokens(data.tokens);
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export async function register(payload: RegisterData): Promise<AuthResponse> {
  try {
    const { data } = await apiClient.post<AuthResponse>('/auth/register/', payload);
    storeTokens(data.tokens);
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export async function logout(refreshToken: string | null): Promise<void> {
  try {
    await apiClient.post('/auth/logout/', refreshToken ? { refresh: refreshToken } : {});
  } finally {
    clearTokens();
  }
}

export async function resendVerification(): Promise<{ success: boolean; message: string }> {
  try {
    const { data } = await apiClient.post<{ success: boolean; message: string }>('/auth/resend-verification/');
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export async function verifyEmail(token: string): Promise<{ success: boolean; message?: string; error?: any }> {
  try {
    const { data } = await apiClient.get<{ success: boolean; message?: string; error?: any }>(`/auth/verify-email/${token}/`);
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export async function requestPasswordReset(payload: PasswordResetRequest): Promise<{ success: boolean; message: string }> {
  try {
    const { data } = await apiClient.post<{ success: boolean; message: string }>(
      '/auth/password-reset/',
      payload
    );
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export async function confirmPasswordReset(payload: PasswordResetConfirm): Promise<{ success: boolean; message: string }> {
  try {
    const { data } = await apiClient.post<{ success: boolean; message: string }>(
      '/auth/password-reset-confirm/',
      payload
    );
    return data;
  } catch (error) {
    throw buildError(error);
  }
}

export type { AuthTokens };
