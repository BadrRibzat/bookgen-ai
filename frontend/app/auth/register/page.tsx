/**
 * Register page
 */

import { RegisterForm } from '@/components/auth/RegisterForm';
import Navigation from '@/components/Navigation';

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      {/* Navigation */}
      <Navigation />

      {/* Register Form */}
      <div className="flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
        <RegisterForm />
      </div>
    </div>
  );
}
