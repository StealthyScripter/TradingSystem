'use client'
import React, { useState } from 'react';
import { Code, Key, Database, Shield, Zap, Copy, ExternalLink, ChevronDown, ChevronRight } from 'lucide-react';
import Header from '@/components/Header';

export default function APIDocsPage() {
  const [activeEndpoint, setActiveEndpoint] = useState('auth');
  const [expandedSections, setExpandedSections] = useState<string[]>(['auth']);

  const endpoints = [
    {
      id: 'auth',
      title: 'Authentication',
      icon: Key,
      color: 'blue',
      endpoints: [
        {
          method: 'POST',
          path: '/api/v1/auth/login',
          description: 'Authenticate user and get access token',
          params: ['email', 'password'],
          response: '{ "access_token": "...", "user": {...} }'
        },
        {
          method: 'POST',
          path: '/api/v1/auth/register',
          description: 'Register a new user account',
          params: ['email', 'password', 'first_name', 'last_name'],
          response: '{ "user": {...}, "message": "..." }'
        },
        {
          method: 'GET',
          path: '/api/v1/auth/profile',
          description: 'Get current user profile',
          params: [],
          response: '{ "user_id": "...", "email": "...", ... }'
        }
      ]
    },
    {
      id: 'portfolio',
      title: 'Portfolio',
      icon: Database,
      color: 'green',
      endpoints: [
        {
          method: 'GET',
          path: '/api/v1/portfolio/summary',
          description: 'Get complete portfolio summary with analysis',
          params: [],
          response: '{ "accounts": [...], "summary": {...}, "analysis": {...} }'
        },
        {
          method: 'POST',
          path: '/api/v1/portfolio/update-prices',
          description: 'Update all asset prices from market data',
          params: [],
          response: '{ "updated_assets": 25, "total_assets": 30, ... }'
        }
      ]
    },
    {
      id: 'accounts',
      title: 'Accounts',
      icon: Shield,
      color: 'purple',
      endpoints: [
        {
          method: 'GET',
          path: '/api/v1/accounts',
          description: 'List all user accounts',
          params: [],
          response: '[{ "id": 1, "name": "...", "balance": ... }]'
        },
        {
          method: 'POST',
          path: '/api/v1/accounts',
          description: 'Create a new account',
          params: ['name', 'account_type', 'description?'],
          response: '{ "id": 1, "name": "...", "account_type": "..." }'
        }
      ]
    },
    {
      id: 'assets',
      title: 'Assets',
      icon: Zap,
      color: 'orange',
      endpoints: [
        {
          method: 'POST',
          path: '/api/v1/assets',
          description: 'Add an asset to an account',
          params: ['account_id', 'symbol', 'shares', 'avg_cost'],
          response: '{ "id": 1, "symbol": "...", "shares": ..., ... }'
        }
      ]
    },
    {
      id: 'analysis',
      title: 'AI Analysis',
      icon: Code,
      color: 'red',
      endpoints: [
        {
          method: 'POST',
          path: '/api/v1/analysis/quick',
          description: 'Get quick AI analysis for symbols',
          params: ['symbols[]'],
          response: '{ "analysis": { "AAPL": { "sentiment": "...", ... } } }'
        },
        {
          method: 'POST',
          path: '/api/v1/analysis/asset/{symbol}',
          description: 'Detailed analysis for a specific asset',
          params: [],
          response: '{ "symbol": "...", "analysis": {...}, ... }'
        }
      ]
    }
  ];

  const codeExamples = {
    auth: `// Authentication Example
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'your_password'
  })
});

const data = await response.json();
const token = data.access_token;`,

    portfolio: `// Get Portfolio Summary
const response = await fetch('/api/v1/portfolio/summary', {
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});

const portfolio = await response.json();
console.log(\`Total Value: $\${portfolio.summary.total_value}\`);`,

    accounts: `// Create New Account
const response = await fetch('/api/v1/accounts', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'My Brokerage Account',
    account_type: 'brokerage',
    description: 'Main investment account'
  })
});

const account = await response.json();`,

    assets: `// Add Asset to Account
const response = await fetch('/api/v1/assets', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    account_id: 1,
    symbol: 'AAPL',
    shares: 10,
    avg_cost: 150.00
  })
});

const asset = await response.json();`,

    analysis: `// Get AI Analysis
const response = await fetch('/api/v1/analysis/quick', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symbols: ['AAPL', 'GOOGL', 'MSFT']
  })
});

const analysis = await response.json();
console.log(analysis.analysis.AAPL.recommendation);`
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-50 border-blue-200',
      green: 'text-green-600 bg-green-50 border-green-200',
      purple: 'text-purple-600 bg-purple-50 border-purple-200',
      orange: 'text-orange-600 bg-orange-50 border-orange-200',
      red: 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  const getMethodColor = (method: string) => {
    const colors = {
      GET: 'bg-green-100 text-green-800',
      POST: 'bg-blue-100 text-blue-800',
      PUT: 'bg-yellow-100 text-yellow-800',
      DELETE: 'bg-red-100 text-red-800'
    };
    return colors[method as keyof typeof colors] || colors.GET;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Header
          title="API Documentation"
          subtitle="Complete reference for FlexPesaAi REST API"
        />

        {/* API Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Getting Started</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Base URL</h3>
              <code className="bg-gray-100 px-3 py-2 rounded text-sm font-mono">
                https://api.flexpesaai.com/api/v1
              </code>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Authentication</h3>
              <p className="text-gray-600 text-sm">Bearer token in Authorization header</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Rate Limits</h3>
              <p className="text-gray-600 text-sm">1000 requests per hour</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sticky top-4">
              <h3 className="font-semibold text-gray-900 mb-4">API Endpoints</h3>
              <nav className="space-y-2">
                {endpoints.map((endpoint) => (
                  <div key={endpoint.id}>
                    <button
                      onClick={() => {
                        setActiveEndpoint(endpoint.id);
                        toggleSection(endpoint.id);
                      }}
                      className={`w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors ${
                        activeEndpoint === endpoint.id
                          ? getColorClasses(endpoint.color)
                          : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <endpoint.icon size={18} />
                        <span className="text-sm font-medium">{endpoint.title}</span>
                      </div>
                      {expandedSections.includes(endpoint.id) ?
                        <ChevronDown size={16} /> : <ChevronRight size={16} />
                      }
                    </button>

                    {expandedSections.includes(endpoint.id) && (
                      <div className="ml-4 mt-2 space-y-1">
                        {endpoint.endpoints.map((ep, index) => (
                          <div key={index} className="text-xs text-gray-600 py-1">
                            <span className={`px-2 py-1 rounded font-mono ${getMethodColor(ep.method)}`}>
                              {ep.method}
                            </span>
                            <span className="ml-2">{ep.path.split('/').pop()}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {endpoints.map((section) => (
              activeEndpoint === section.id && (
                <div key={section.id} className="space-y-6">
                  {/* Section Header */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <section.icon className={`text-${section.color}-600`} size={24} />
                      <h2 className="text-2xl font-bold text-gray-900">{section.title}</h2>
                    </div>
                    <p className="text-gray-600">
                      {section.id === 'auth' && 'Manage user authentication and access tokens'}
                      {section.id === 'portfolio' && 'Access portfolio data, summaries, and analysis'}
                      {section.id === 'accounts' && 'Manage investment accounts and balances'}
                      {section.id === 'assets' && 'Add and manage assets within accounts'}
                      {section.id === 'analysis' && 'Get AI-powered analysis and recommendations'}
                    </p>
                  </div>

                  {/* Code Example */}
                  <div className="bg-gray-900 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-white font-semibold">Code Example</h3>
                      <button className="text-gray-400 hover:text-white">
                        <Copy size={16} />
                      </button>
                    </div>
                    <pre className="text-green-400 text-sm overflow-x-auto">
                      <code>{codeExamples[section.id as keyof typeof codeExamples]}</code>
                    </pre>
                  </div>

                  {/* Endpoints */}
                  <div className="space-y-4">
                    {section.endpoints.map((endpoint, index) => (
                      <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <div className="flex items-center gap-3 mb-3">
                          <span className={`px-3 py-1 rounded font-mono text-sm ${getMethodColor(endpoint.method)}`}>
                            {endpoint.method}
                          </span>
                          <code className="text-gray-700 font-mono">{endpoint.path}</code>
                        </div>

                        <p className="text-gray-600 mb-4">{endpoint.description}</p>

                        {endpoint.params.length > 0 && (
                          <div className="mb-4">
                            <h4 className="font-semibold text-gray-900 mb-2">Parameters</h4>
                            <div className="space-y-2">
                              {endpoint.params.map((param, paramIndex) => (
                                <div key={paramIndex} className="flex items-center gap-2">
                                  <code className="bg-gray-100 px-2 py-1 rounded text-sm">
                                    {param}
                                  </code>
                                  {param.includes('?') && (
                                    <span className="text-xs text-gray-500">optional</span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div>
                          <h4 className="font-semibold text-gray-900 mb-2">Response</h4>
                          <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                            <code>{endpoint.response}</code>
                          </pre>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>

        {/* SDK Section */}
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">SDKs & Libraries</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">JavaScript/TypeScript</h3>
              <p className="text-gray-600 text-sm mb-3">Official Node.js SDK</p>
              <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm">
                <ExternalLink size={14} />
                View on GitHub
              </button>
            </div>
            <div className="bg-white rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Python</h3>
              <p className="text-gray-600 text-sm mb-3">Python client library</p>
              <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm">
                <ExternalLink size={14} />
                View on PyPI
              </button>
            </div>
            <div className="bg-white rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Postman Collection</h3>
              <p className="text-gray-600 text-sm mb-3">Complete API collection</p>
              <button className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm">
                <ExternalLink size={14} />
                Import Collection
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
