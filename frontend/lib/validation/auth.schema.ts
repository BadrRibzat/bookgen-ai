import { z } from 'zod';

const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters long')
  .regex(/[A-Z]/, 'Password must include at least one uppercase letter')
  .regex(/[a-z]/, 'Password must include at least one lowercase letter')
  .regex(/[0-9]/, 'Password must include at least one number');

export const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerSchema = z
  .object({
    email: z.string().min(1, 'Email is required').email('Enter a valid email address'),
    first_name: z.string().trim().min(2, 'First name must be at least 2 characters').optional().or(z.literal('').transform(() => undefined)),
    last_name: z.string().trim().min(2, 'Last name must be at least 2 characters').optional().or(z.literal('').transform(() => undefined)),
    password: passwordSchema,
    password_confirm: z.string().min(8, 'Please re-enter your password'),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: 'Passwords do not match',
    path: ['password_confirm'],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;

export const passwordResetRequestSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Enter a valid email address'),
});

export type PasswordResetRequestFormData = z.infer<typeof passwordResetRequestSchema>;

export const passwordResetConfirmSchema = z
  .object({
    token: z.string().min(1, 'Reset token is required'),
    password: passwordSchema,
    password_confirm: z.string().min(8, 'Please re-enter your password'),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: 'Passwords do not match',
    path: ['password_confirm'],
  });

export type PasswordResetConfirmFormData = z.infer<typeof passwordResetConfirmSchema>;
