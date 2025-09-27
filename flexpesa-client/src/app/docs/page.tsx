'use client'
import React from 'react';
import { BookOpen, Code, Database, Shield, Zap, ArrowRight, ExternalLink, Copy } from 'lucide-react';
import Header from '@/components/Header';

export default function DocsPage() {
  const sections = [
    {
      title: "Getting Started",
      icon: Zap,
      items: [
        { title: "Quick Start Guide", desc: "Get up and running in 5 minutes" },
        { title: "Account Setup", desc: "Connect your brokerage accounts" },
        { title: "First Portfolio", desc: "Create and analyze your first portfolio" },
        { title: "Dashboard Overview", desc: "Navigate the main interface" }
      ]
    },
    {
      title: "API Reference",
      icon: Code,
      items: [
        { title: "Authentication", desc: "Secure API access with tokens" },
        { title: "Portfolio Endpoints", desc: "Manage portfolios and accounts" },
        { title: "Analysis Endpoints", desc: "AI-powered insights and recommendations" },
        { title: "Market Data", desc: "Real-time price feeds and indicators" }
      ]
    },
    {
      title: "Features",
      icon: Database,
      items: [
        { title: "Multi-Account Support", desc: "Wells Fargo, Robinhood, Cash App integration" },
        { title: "AI Analysis", desc: "Sentiment analysis and risk assessment" },
        { title: "Real-time Data", desc: "Live market prices and portfolio updates" },
        { title: "Performance Metrics", desc: "Sharpe ratio, beta, and risk analytics" }
      ]
    },
    {
      title: "Security",
      icon: Shield,
      items: [
        { title: "Data Protection", desc: "Bank-grade encryption and security" },
        { title: "Authentication", desc: "Multi-factor authentication setup" },
        { title: "Privacy Controls", desc: "Manage your data and privacy settings" },
        { title: "Compliance", desc: "SOC 2 Type II and regulatory compliance" }
      ]
    }
  ];

  const codeExample = `// Example: Get Portfolio Summary
const response = await fetch('/api/v1/portfolio/summary', {
  headers: {
    'Authorization': 'Bearer YOUR_API_TOKEN',
    'Content-Type': 'application/json'
  }
});

const portfolio = await response.json();
console.log(\`Total Value: $\${portfolio.summary.total_value}\`);`;

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <Header
          title="Documentation"
          subtitle="Everything you need to know about FlexPesaAi"
        />

        {/* Search Bar */}
        <div className="subsection-spacing">
          <div className="relative max-w-md">
            <input
              type="text"
              placeholder="Search documentation..."
              className="form-input"
            />
            <button className="absolute right-3 top-3 text-gray-400 hover:text-gray-600">
              <ExternalLink size={20} />
            </button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 section-spacing">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="text-blue-600" size={20} />
              <span className="card-title text-blue-900">Quick Start</span>
            </div>
            <p className="card-subtitle text-blue-700">Get started in under 5 minutes</p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Code className="text-green-600" size={20} />
              <span className="card-title text-green-900">API Reference</span>
            </div>
            <p className="card-subtitle text-green-700">Complete API documentation</p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="text-purple-600" size={20} />
              <span className="card-title text-purple-900">Tutorials</span>
            </div>
            <p className="card-subtitle text-purple-700">Step-by-step guides</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Documentation Sections */}
          <div className="lg:col-span-2">
            <div className="space-y-8">
              {sections.map((section, index) => (
                <div key={index} className="card">
                  <div className="flex items-center gap-3 subsection-spacing">
                    <section.icon className="text-blue-600" size={24} />
                    <h2 className="card-title">{section.title}</h2>
                  </div>

                  <div className="space-y-3">
                    {section.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                        <div>
                          <h3 className="font-medium text-gray-900">{item.title}</h3>
                          <p className="card-subtitle">{item.desc}</p>
                        </div>
                        <ArrowRight className="text-gray-400" size={16} />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Code Example */}
            <div className="bg-gray-900 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-medium">Quick Example</h3>
                <button className="text-gray-400 hover:text-white">
                  <Copy size={16} />
                </button>
              </div>
              <pre className="text-green-400 text-sm overflow-x-auto">
                <code>{codeExample}</code>
              </pre>
            </div>

            {/* Popular Articles */}
            <div className="card-compact">
              <h3 className="card-title mb-3">Popular Articles</h3>
              <div className="space-y-2">
                <a href="#" className="block text-blue-600 hover:text-blue-800 text-sm">
                  Setting up multi-account tracking
                </a>
                <a href="#" className="block text-blue-600 hover:text-blue-800 text-sm">
                  Understanding AI recommendations
                </a>
                <a href="#" className="block text-blue-600 hover:text-blue-800 text-sm">
                  Portfolio risk assessment guide
                </a>
                <a href="#" className="block text-blue-600 hover:text-blue-800 text-sm">
                  API authentication best practices
                </a>
              </div>
            </div>

            {/* Support */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="card-title text-blue-900 mb-2">Need Help?</h3>
              <p className="card-subtitle text-blue-700 mb-3">
                Can&#39;t find what you&#39;re looking for?
              </p>
              <button className="btn-primary text-sm">
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
