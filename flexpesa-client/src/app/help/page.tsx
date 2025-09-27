'use client'
import React, { useState } from 'react';
import { Search, MessageCircle, Book, Shield, Settings, TrendingUp, CreditCard, Users, ChevronRight, Star, Clock, CheckCircle } from 'lucide-react';
import Header from '@/components/Header';

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All Topics', icon: Book },
    { id: 'getting-started', name: 'Getting Started', icon: TrendingUp },
    { id: 'accounts', name: 'Account Management', icon: CreditCard },
    { id: 'security', name: 'Security & Privacy', icon: Shield },
    { id: 'troubleshooting', name: 'Troubleshooting', icon: Settings },
    { id: 'billing', name: 'Billing & Plans', icon: Users }
  ];

  const popularArticles = [
    {
      title: "How to connect your brokerage account",
      category: "getting-started",
      views: 12500,
      rating: 4.8,
      readTime: "3 min"
    },
    {
      title: "Understanding AI portfolio recommendations",
      category: "getting-started",
      views: 8900,
      rating: 4.6,
      readTime: "5 min"
    },
    {
      title: "Setting up two-factor authentication",
      category: "security",
      views: 7200,
      rating: 4.9,
      readTime: "2 min"
    },
    {
      title: "Why my portfolio value differs from my broker",
      category: "troubleshooting",
      views: 6800,
      rating: 4.4,
      readTime: "4 min"
    },
    {
      title: "Upgrading your subscription plan",
      category: "billing",
      views: 5600,
      rating: 4.7,
      readTime: "3 min"
    }
  ];

  const faqData = [
    {
      question: "How secure is my financial data?",
      answer: "We use bank-grade 256-bit SSL encryption and never store your login credentials. All data is encrypted both in transit and at rest.",
      category: "security"
    },
    {
      question: "Which brokerages do you support?",
      answer: "We currently support Wells Fargo, Robinhood, Cash App, TD Ameritrade, Fidelity, Charles Schwab, E*TRADE, and Vanguard.",
      category: "accounts"
    },
    {
      question: "How often is my portfolio data updated?",
      answer: "Portfolio values are updated in real-time during market hours. Outside market hours, data is updated every 15 minutes.",
      category: "getting-started"
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer: "Yes, you can cancel your subscription at any time. Your access will continue until the end of your current billing period.",
      category: "billing"
    },
    {
      question: "What if I can't connect my account?",
      answer: "First, check your credentials. If issues persist, try clearing browser cache or contact support for assistance.",
      category: "troubleshooting"
    }
  ];

  const filteredArticles = selectedCategory === 'all'
    ? popularArticles
    : popularArticles.filter(article => article.category === selectedCategory);

  const filteredFAQs = selectedCategory === 'all'
    ? faqData
    : faqData.filter(faq => faq.category === selectedCategory);

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <Header
          title="Help Center"
          subtitle="Find answers to common questions and get support"
        />

        {/* Search Section */}
        <div className="card-large section-spacing">
          <div className="text-center subsection-spacing">
            <h2 className="section-title mb-2">How can we help you?</h2>
            <p className="section-subtitle">Search our knowledge base or browse by category</p>
          </div>

          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search for help articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="form-input pl-12 text-lg"
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 section-spacing">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 hover:bg-blue-100 cursor-pointer transition-colors">
            <MessageCircle className="text-blue-600 mb-3" size={24} />
            <h3 className="card-title mb-1">Live Chat</h3>
            <p className="card-subtitle">Get instant help from our support team</p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-6 hover:bg-green-100 cursor-pointer transition-colors">
            <Book className="text-green-600 mb-3" size={24} />
            <h3 className="card-title mb-1">Documentation</h3>
            <p className="card-subtitle">Detailed guides and API reference</p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 hover:bg-purple-100 cursor-pointer transition-colors">
            <Users className="text-purple-600 mb-3" size={24} />
            <h3 className="card-title mb-1">Community</h3>
            <p className="card-subtitle">Connect with other users and experts</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Category Sidebar */}
          <div className="lg:col-span-1">
            <div className="card-compact">
              <h3 className="card-title subsection-spacing">Categories</h3>
              <div className="space-y-2">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                      selectedCategory === category.id
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <category.icon size={18} />
                    <span className="text-sm font-medium">{category.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Contact Support */}
            <div className="bg-gray-900 rounded-lg p-4 mt-6 text-white">
              <h3 className="card-title mb-2 text-white">Still need help?</h3>
              <p className="text-gray-300 text-sm mb-4">Our support team is here to help</p>
              <button className="btn-primary w-full">
                Contact Support
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Popular Articles */}
            <div className="card">
              <h2 className="card-title subsection-spacing">Popular Articles</h2>
              <div className="space-y-4">
                {filteredArticles.map((article, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1">{article.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Star className="text-yellow-400 fill-current" size={14} />
                          <span>{article.rating}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock size={14} />
                          <span>{article.readTime}</span>
                        </div>
                        <span>{article.views.toLocaleString()} views</span>
                      </div>
                    </div>
                    <ChevronRight className="text-gray-400" size={20} />
                  </div>
                ))}
              </div>
            </div>

            {/* FAQ Section */}
            <div className="card">
              <h2 className="card-title subsection-spacing">Frequently Asked Questions</h2>
              <div className="space-y-4">
                {filteredFAQs.map((faq, index) => (
                  <div key={index} className="border border-gray-100 rounded-lg">
                    <div className="p-4 cursor-pointer hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-900">{faq.question}</h3>
                        <ChevronRight className="text-gray-400" size={20} />
                      </div>
                      <p className="card-subtitle mt-2">{faq.answer}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Getting Started Checklist */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
              <h2 className="card-title subsection-spacing">Getting Started Checklist</h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="text-green-600" size={20} />
                  <span className="text-gray-700">Create your FlexPesaAi account</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="text-green-600" size={20} />
                  <span className="text-gray-700">Connect your first brokerage account</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                  <span className="text-gray-500">Set up portfolio tracking preferences</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                  <span className="text-gray-500">Enable real-time notifications</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                  <span className="text-gray-500">Explore AI recommendations</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
