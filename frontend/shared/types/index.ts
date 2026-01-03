/**
 * Shared TypeScript types for BookGen-AI
 * Used across backend and frontend
 */

// ============================================
// User Types
// ============================================

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_staff: boolean;
  email_verified: boolean;
  is_active: boolean;
  date_joined: string;
  profile: UserProfile;
  usage_summary?: UsageSummary;
}

export interface SubscriptionPlan {
  id: number;
  name: string;
  slug: string;
  price: string;
  book_limit_per_month: number;
  features: Record<string, any>;
}

export interface UsageSummary {
  plan_name: string;
  book_limit: number;
  current_usage: number;
  remaining_books: number;
  usage_reset_date: string;
}

export interface UserProfile {
  avatar_seed: string;
  avatar_initials: string;
  subscription_plan: SubscriptionPlan | null;
  subscription_status: string;
  total_books_generated: number;
  total_words_written: number;
  total_edit_actions: number;
  total_time_spent_minutes: number;
  current_month_book_count: number;
  usage_reset_date: string;
  last_active_at: string;
  features_used: Record<string, number>;
  theme: 'light' | 'dark';
  email_notifications: boolean;
  marketing_emails: boolean;
}

export interface UserAnalytics {
  total_books: number;
  total_words: number;
  total_edits: number;
  total_time_minutes: number;
  recent_activity: AnalyticsEvent[];
  feature_usage: Record<string, number>;
}

export interface AnalyticsEvent {
  event_type: string;
  metadata: Record<string, any>;
  duration_seconds: number | null;
  created_at: string;
}

// ============================================
// Authentication Types
// ============================================

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  first_name?: string;
  last_name?: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user: User;
  tokens: AuthTokens;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  password: string;
  password_confirm: string;
}

// ============================================
// API Response Types
// ============================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: ApiError;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  success: boolean;
  results: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// ============================================
// Domain, Niche & Audience Types
// ============================================

export interface Domain {
  id: string;
  name: string;
  description: string;
  icon: string;
  is_active: boolean;
  subscription_tiers: string[];
  created_at: string;
  updated_at: string;
}

export interface Niche {
  id: string;
  name: string;
  description: string;
  domain_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Audience {
  id: string;
  name: string;
  description: string;
  domain_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DomainsResponse {
  success: boolean;
  domains: Domain[];
}

export interface DomainNichesResponse {
  success: boolean;
  niches: Niche[];
  domain: Domain;
}

export interface DomainAudiencesResponse {
  success: boolean;
  audiences: Audience[];
  domain: Domain;
}

// ============================================
// Book Types (Placeholder for future)
// ============================================

export interface Book {
  id: string;
  title: string;
  domain_id: string;
  niche_id?: string;
  summary?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error?: string;
}

// ============================================
// Form Types
// ============================================

export interface FormError {
  field: string;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: FormError[];
}
