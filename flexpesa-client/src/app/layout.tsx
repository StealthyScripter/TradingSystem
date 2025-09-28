import type { Metadata } from "next";
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs'
import { Geist, Geist_Mono } from 'next/font/google'
import "./globals.css";
import HamburgerMenu from "@/components/HamburgerMenu";
import { Logo } from "@/components/Logo";

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: "Investment Portfolio Dashboard",
  description: "Real-time portfolio management with AI-powered insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
          {/* Navigation Header */}
          <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                {/* Logo */}
                <div className="flex items-center">
                  <h1 className="flex items-center gap-2 text-xl font-bold text-gray-900">
                    <Logo /> Portfolio Dashboard
                  </h1>
                </div>

                {/* Auth Controls */}
                <div className="flex items-center space-x-4">
                  <SignedOut>
                    <div className="flex items-center space-x-2">
                      <SignInButton mode="modal">
                        <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                          Sign In
                        </button>
                      </SignInButton>
                      <SignUpButton mode="modal">
                        <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors">
                          Sign Up
                        </button>
                      </SignUpButton>
                    </div>
                  </SignedOut>

                  <SignedIn>
                    <div className="flex items-center space-x-3">
                      <span className="text-sm text-gray-600">Welcome back!</span>
                      <UserButton
                        afterSignOutUrl="/"
                        appearance={{
                          elements: {
                            avatarBox: "w-8 h-8",
                          }
                        }}
                      />
                      <HamburgerMenu />
                    </div>
                  </SignedIn>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main>
            {children}
          </main>
        </body>
      </html>
    </ClerkProvider>
  );
}
