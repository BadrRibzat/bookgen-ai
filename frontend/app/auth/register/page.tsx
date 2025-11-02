/**
 * Register page
 */

import { RegisterForm } from '@/components/auth/RegisterForm';

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50 px-4 sm:px-6 lg:px-8">
      <RegisterForm />
    </div>
  );
}
