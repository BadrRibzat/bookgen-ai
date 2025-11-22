import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

type Nullable<T> = T | null | undefined;

/**
 * Merge Tailwind classes with conditional logic support.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Safely parse a JSON string and fall back to null when it fails.
 */
export function safeJsonParse<T>(value: Nullable<string>): T | null {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as T;
  } catch (error) {
    console.warn('Unable to parse JSON value:', error);
    return null;
  }
}

/**
 * Format a Date string into a user friendly representation.
 */
export function formatDate(value: Nullable<string | number | Date>): string {
  if (!value) {
    return '';
  }

  const date = value instanceof Date ? value : new Date(value);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}
