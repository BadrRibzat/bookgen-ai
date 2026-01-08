/**
 * Home page - Landing page
 */

import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-3">
              <img 
                src="/logo-icon.svg" 
                alt="BookGen-AI Logo" 
                className="h-8 w-8 text-primary-600"
              />
              <span className="text-2xl font-bold text-primary-600">
                BookGen-AI
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/subscriptions">
                <Button variant="ghost">Pricing</Button>
              </Link>
              <Link href="/auth/login">
                <Button variant="ghost">Sign in</Button>
              </Link>
              <Link href="/auth/register">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Transform Your Ideas Into
            <span className="text-primary-600"> Professional Books</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Harness the power of AI to generate high-quality, professionally formatted books
            in minutes. From concept to publication, we've got you covered.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/auth/register">
              <Button size="lg">Start Writing for Free</Button>
            </Link>
            <Link href="#features">
              <Button variant="outline" size="lg">
                Learn More
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div id="features" className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              AI-Powered Generation
            </h3>
            <p className="text-gray-600">
              Advanced AI technology creates engaging, coherent content tailored to your
              specifications.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Professional Formatting
            </h3>
            <p className="text-gray-600">
              Export publication-ready PDFs with professional typography and layout.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Lightning Fast</h3>
            <p className="text-gray-600">
              Generate complete books in minutes, not months. Focus on your ideas, not
              formatting.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-32 bg-primary-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Writing?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of authors creating amazing content with BookGen-AI
          </p>
          <Link href="/auth/register">
            <Button size="lg" variant="secondary">
              Create Your Free Account
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <p className="text-gray-400">
              © 2024 BookGen-AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
