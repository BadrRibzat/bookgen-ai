'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useRouter } from 'next/navigation';
import type {
  User,
  LoginCredentials,
  RegisterData,
  PasswordResetRequest,
  PasswordResetConfirm,
  UserAnalytics,
} from '@/shared/types';
import {
  login as loginRequest,
  register as registerRequest,
  logout as logoutRequest,
  resendVerification as resendVerificationRequest,
  requestPasswordReset as requestPasswordResetApi,
  confirmPasswordReset as confirmPasswordResetApi,
  type ApiRequestError,
} from '@/lib/api/auth';
import {
  getCurrentUser,
  updateCurrentUser,
  getUserAnalytics,
  type UpdateUserProfilePayload,
} from '@/lib/api/users';
import {
  getAccessToken,
  getRefreshToken,
  clearTokens,
  extractErrorMessage,
} from '@/lib/api/client';

interface AuthError {
  message: string;
  details?: Record<string, string[]>;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: AuthError | null;
  isAuthenticated: boolean;
  analytics: UserAnalytics | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (payload: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateProfile: (payload: UpdateUserProfilePayload) => Promise<User>;
  requestPasswordReset: (payload: PasswordResetRequest) => Promise<void>;
  confirmPasswordReset: (payload: PasswordResetConfirm) => Promise<void>;
  resendVerificationEmail: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<AuthError | null>(null);

  const resetState = useCallback(() => {
    setUser(null);
    setAnalytics(null);
    setError(null);
  }, []);

  const loadUserProfile = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      resetState();
      setLoading(false);
      return;
    }

    try {
      const [profile, analyticsData] = await Promise.all([
        getCurrentUser(),
        getUserAnalytics().catch(() => null),
      ]);

      setUser(profile);
      if (analyticsData) {
        setAnalytics(analyticsData);
      }
    } catch (err) {
      console.error('Failed to load user profile:', err);
      clearTokens();
      resetState();
    } finally {
      setLoading(false);
    }
  }, [resetState]);

  useEffect(() => {
    loadUserProfile();
  }, [loadUserProfile]);

  const handleError = useCallback((err: unknown) => {
    if (!err) {
      setError(null);
      return;
    }

    const message = extractErrorMessage(err);
    const details =
      (typeof err === 'object' && err && 'details' in err && (err as ApiRequestError).details) ||
      undefined;

    setError({ message, details });
  }, []);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      handleError(null);
      try {
        const response = await loginRequest(credentials);
        setUser(response.user);
        setAnalytics(null);
        router.push('/dashboard');
      } catch (err) {
        handleError(err);
        throw err;
      }
    },
    [handleError, router]
  );

  const register = useCallback(
    async (payload: RegisterData) => {
      handleError(null);
      try {
        const response = await registerRequest(payload);
        setUser(response.user);
        setAnalytics(null);
        router.push('/dashboard');
      } catch (err) {
        handleError(err);
        throw err;
      }
    },
    [handleError, router]
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest(getRefreshToken());
    } catch (err) {
      console.warn('Logout request failed:', err);
    } finally {
      clearTokens();
      resetState();
      router.push('/auth/login');
    }
  }, [resetState, router]);

  const refreshProfile = useCallback(async () => {
    try {
      const [profile, analyticsData] = await Promise.all([
        getCurrentUser(),
        getUserAnalytics().catch(() => null),
      ]);

      setUser(profile);
      if (analyticsData) {
        setAnalytics(analyticsData);
      }
    } catch (err) {
      handleError(err);
      throw err;
    }
  }, [handleError]);

  const updateProfile = useCallback(
    async (payload: UpdateUserProfilePayload) => {
      handleError(null);
      try {
        const updatedUser = await updateCurrentUser(payload);
        setUser(updatedUser);
        return updatedUser;
      } catch (err) {
        handleError(err);
        throw err;
      }
    },
    [handleError]
  );

  const requestPasswordReset = useCallback(
    async (payload: PasswordResetRequest) => {
      handleError(null);
      try {
        await requestPasswordResetApi(payload);
      } catch (err) {
        handleError(err);
        throw err;
      }
    },
    [handleError]
  );

  const confirmPasswordReset = useCallback(
    async (payload: PasswordResetConfirm) => {
      handleError(null);
      try {
        await confirmPasswordResetApi(payload);
      } catch (err) {
        handleError(err);
        throw err;
      }
    },
    [handleError]
  );

  const resendVerificationEmail = useCallback(async () => {
    handleError(null);
    try {
      await resendVerificationRequest();
    } catch (err) {
      handleError(err);
      throw err;
    }
  }, [handleError]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      error,
      isAuthenticated: Boolean(user),
      analytics,
      login,
      register,
      logout,
      refreshProfile,
      updateProfile,
      requestPasswordReset,
      confirmPasswordReset,
      resendVerificationEmail,
      clearError: () => setError(null),
    }),
    [
      analytics,
      confirmPasswordReset,
      error,
      loading,
      login,
      logout,
      refreshProfile,
      register,
      requestPasswordReset,
      resendVerificationEmail,
      updateProfile,
      user,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
