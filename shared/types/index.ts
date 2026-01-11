// Shared TypeScript type definitions for BookGen-AI

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email_verified?: boolean;
  is_staff?: boolean;
  is_active?: boolean;
  date_joined?: string;
  profile?: UserProfile;
  subscription_plan?: SubscriptionPlan;
  usage_summary?: {
    remaining_books: number;
    total_books_this_month: number;
    monthly_limit: number;
  };
}

export interface UserProfile {
  user: User;
  subscription_plan?: SubscriptionPlan;
  current_month_book_count: number;
  total_books_generated: number;
  total_words_written: number;
  total_edit_actions: number;
  total_time_spent_minutes: number;
  avatar_seed?: string;
  avatar_initials?: string;
  theme: 'light' | 'dark';
  email_notifications: boolean;
  marketing_emails: boolean;
}

export interface SubscriptionPlan {
  id: string | number;
  name: string;
  slug: string;
  price: number;
  billing_cycle: 'monthly' | 'quarterly' | 'annual' | 'forever';
  duration_days: number;
  book_limit_per_month: number;
  features: Record<string, any>;
  is_active: boolean;
}

export interface Domain {
  id: string;
  name: string;
  display_name: string;
  description: string;
  icon: string;
  color: string;
  trending_score: number;
  is_active: boolean;
  subscription_tiers?: string[];
  niches_count?: number;
  audiences_count?: number;
}

export interface Niche {
  id: string;
  name: string;
  description: string;
  domain_id: string;
  is_active?: boolean;
  created_at?: string;
}

export interface Audience {
  id: string;
  name: string;
  description: string;
  domain_id: string;
  is_active?: boolean;
  created_at?: string;
}

export interface Book {
  id: string;
  title: string;
  domain_id: string;
  niche_id?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  pdf_url?: string;
  cover_url?: string;
  word_count?: number;
  tokens_used?: number;
  is_previewed?: boolean;
  is_downloaded?: boolean;
  downloaded_at?: string;
  error_message?: string;
}

export interface BookGenerationRequest {
  id: string;
  title: string;
  domain: Domain;
  niche?: Niche;
  custom_prompt?: string;
  target_word_count: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  pdf_url?: string;
  cover_url?: string;
  tokens_used?: number;
  error_message?: string;
  can_download: boolean;
  is_expired: boolean;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
  };
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  tokens: AuthTokens;
  message?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  password: string;
}

export interface AuthUser extends User {
  tokens: AuthTokens;
}

// Analytics types
export interface UserAnalytics {
  total_books_generated: number;
  total_words_written: number;
  total_edit_actions: number;
  total_time_spent_minutes: number;
  last_active_at: string;
}

// API Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}