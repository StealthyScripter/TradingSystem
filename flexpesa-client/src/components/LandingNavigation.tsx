import React from 'react';
import { SignInButton, SignUpButton } from '@clerk/nextjs';
import { Logo } from './Logo';
import Link from 'next/link';

interface LandingNavigationProps {
  currentPage?: string;
}

const LandingNavigation: React.FC<LandingNavigationProps> = ({ currentPage }) => {
  const navItems = [
    { href: '/#features', label: 'Features' },
    { href: '/#analytics', label: 'Analytics' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/security', label: 'Security' }
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-lg border-b border-gray-100 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-2">
            <Logo />
            <span className="text-xl font-bold text-gray-900">FlexPesaAi</span>
          </Link>

          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-link ${currentPage === item.label.toLowerCase() ? 'nav-link-active' : ''}`}
              >
                {item.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center space-x-4">
            <SignInButton mode="modal">
              <button className="nav-link">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl font-medium">
                Start Free Trial
              </button>
            </SignUpButton>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default LandingNavigation;
