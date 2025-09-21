'use client'
import React from 'react';
import { Shield, Eye, Lock, Database, Users, Mail, Calendar } from 'lucide-react';
import Header from '@/components/Header';

export default function PrivacyPage() {
  const sections = [
    {
      id: 'collection',
      title: 'Information We Collect',
      icon: Database,
      content: [
        {
          subtitle: 'Personal Information',
          items: [
            'Name, email address, and contact information',
            'Account credentials and authentication data',
            'Billing and payment information',
            'Communications and support interactions'
          ]
        },
        {
          subtitle: 'Financial Data',
          items: [
            'Portfolio holdings and investment positions',
            'Account balances and transaction history',
            'Investment preferences and risk tolerance',
            'Third-party brokerage account information (read-only)'
          ]
        },
        {
          subtitle: 'Usage Information',
          items: [
            'Device information and browser type',
            'IP address and location data',
            'Usage patterns and feature interactions',
            'Performance and error data'
          ]
        }
      ]
    },
    {
      id: 'usage',
      title: 'How We Use Your Information',
      icon: Eye,
      content: [
        {
          subtitle: 'Service Provision',
          items: [
            'Provide portfolio analysis and investment insights',
            'Generate AI-powered recommendations and reports',
            'Maintain and sync your account data',
            'Process payments and manage subscriptions'
          ]
        },
        {
          subtitle: 'Communication',
          items: [
            'Send service updates and notifications',
            'Provide customer support and assistance',
            'Share product updates and educational content',
            'Respond to your inquiries and feedback'
          ]
        },
        {
          subtitle: 'Improvement & Security',
          items: [
            'Enhance platform performance and features',
            'Conduct security monitoring and fraud prevention',
            'Analyze usage patterns for product development',
            'Ensure compliance with financial regulations'
          ]
        }
      ]
    },
    {
      id: 'sharing',
      title: 'Information Sharing',
      icon: Users,
      content: [
        {
          subtitle: 'We DO NOT sell your personal data',
          items: [
            'Your financial information is never sold to third parties',
            'We do not share individual portfolio data with advertisers',
            'Account credentials are never shared with anyone',
            'All data sharing is done with your explicit consent'
          ]
        },
        {
          subtitle: 'Limited Sharing Scenarios',
          items: [
            'Service providers who help operate our platform (under strict contracts)',
            'Legal compliance when required by law or court order',
            'Business transfers (with user notification and consent)',
            'Aggregated, anonymized data for research (no personal identification)'
          ]
        }
      ]
    },
    {
      id: 'security',
      title: 'Data Security',
      icon: Lock,
      content: [
        {
          subtitle: 'Technical Safeguards',
          items: [
            'Bank-grade 256-bit SSL encryption for all data transmission',
            'Advanced encryption for data storage and backups',
            'Multi-factor authentication and access controls',
            'Regular security audits and penetration testing'
          ]
        },
        {
          subtitle: 'Operational Security',
          items: [
            'SOC 2 Type II compliance and annual audits',
            'Employee background checks and security training',
            'Principle of least privilege access controls',
            '24/7 security monitoring and incident response'
          ]
        },
        {
          subtitle: 'Data Minimization',
          items: [
            'We only collect data necessary for service operation',
            'Automatic deletion of unnecessary data',
            'Regular data cleanup and archival processes',
            'User-controlled data retention preferences'
          ]
        }
      ]
    },
    {
      id: 'rights',
      title: 'Your Privacy Rights',
      icon: Shield,
      content: [
        {
          subtitle: 'Access & Control',
          items: [
            'View and download all your personal data',
            'Correct or update inaccurate information',
            'Delete your account and associated data',
            'Export your data in portable formats'
          ]
        },
        {
          subtitle: 'Communication Preferences',
          items: [
            'Opt out of marketing communications',
            'Control notification settings and frequency',
            'Choose data sharing preferences',
            'Manage cookie and tracking settings'
          ]
        },
        {
          subtitle: 'Legal Rights (where applicable)',
          items: [
            'Right to data portability under GDPR',
            'Right to be forgotten and data erasure',
            'Right to restrict processing',
            'Right to object to automated decision-making'
          ]
        }
      ]
    }
  ];

  const quickFacts = [
    {
      icon: Lock,
      title: 'Bank-Grade Security',
      description: 'We use the same security standards as major financial institutions'
    },
    {
      icon: Eye,
      title: 'No Data Selling',
      description: 'We never sell or share your personal financial information'
    },
    {
      icon: Shield,
      title: 'User Control',
      description: 'You have full control over your data and privacy settings'
    },
    {
      icon: Database,
      title: 'Minimal Collection',
      description: 'We only collect data necessary to provide our services'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Header
          title="Privacy Policy"
          subtitle="How we protect and handle your personal information"
        />

        {/* Last Updated */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="text-blue-600" size={20} />
            <span className="font-medium text-blue-900">Last Updated: January 15, 2024</span>
          </div>
          <p className="text-blue-700 text-sm">
            We&#39;ll notify you of any significant changes to this policy via email and in-app notifications.
          </p>
        </div>

        {/* Quick Facts */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          {quickFacts.map((fact, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <fact.icon className="text-blue-600 mx-auto mb-3" size={32} />
              <h3 className="font-semibold text-gray-900 mb-2">{fact.title}</h3>
              <p className="text-gray-600 text-sm">{fact.description}</p>
            </div>
          ))}
        </div>

        {/* Introduction */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Commitment to Your Privacy</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 text-lg leading-relaxed mb-4">
              At FlexPesaAi, we understand that your financial information is among your most sensitive data.
              This Privacy Policy explains how we collect, use, protect, and share your information when you
              use our investment portfolio management platform.
            </p>
            <p className="text-gray-600 leading-relaxed mb-4">
              We are committed to transparency about our data practices and giving you control over your
              personal information. This policy covers our website, mobile applications, and all related services.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800 text-sm">
                <strong>Important:</strong> We never sell your personal data or share your individual
                financial information with third parties for marketing purposes.
              </p>
            </div>
          </div>
        </div>

        {/* Main Sections */}
        <div className="space-y-8">
          {sections.map((section, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="flex items-center gap-3 mb-6">
                <section.icon className="text-blue-600" size={28} />
                <h2 className="text-2xl font-bold text-gray-900">{section.title}</h2>
              </div>

              <div className="space-y-6">
                {section.content.map((subsection, subIndex) => (
                  <div key={subIndex}>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">{subsection.subtitle}</h3>
                    <ul className="space-y-2">
                      {subsection.items.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-start gap-3">
                          <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-gray-600">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Cookies & Tracking */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Cookies & Tracking Technologies</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Essential Cookies</h3>
              <p className="text-gray-600 text-sm mb-3">
                Required for basic platform functionality, security, and user authentication.
              </p>
              <ul className="text-gray-600 text-sm space-y-1">
                <li>• Session management</li>
                <li>• Security features</li>
                <li>• User preferences</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Analytics Cookies</h3>
              <p className="text-gray-600 text-sm mb-3">
                Help us understand how users interact with our platform to improve services.
              </p>
              <ul className="text-gray-600 text-sm space-y-1">
                <li>• Usage statistics</li>
                <li>• Performance monitoring</li>
                <li>• Feature optimization</li>
              </ul>
            </div>
          </div>
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-700 text-sm">
              You can control cookie settings in your browser or through our privacy settings.
              Note that disabling essential cookies may affect platform functionality.
            </p>
          </div>
        </div>

        {/* International Users */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">International Users</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 mb-4">
              FlexPesaAi is based in the United States, and your information may be processed
              and stored in the US or other countries where we operate.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">EU/UK Users (GDPR)</h3>
                <ul className="text-gray-600 text-sm space-y-1">
                  <li>• Right to access your data</li>
                  <li>• Right to rectification</li>
                  <li>• Right to erasure</li>
                  <li>• Right to data portability</li>
                  <li>• Right to object to processing</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">California Users (CCPA)</h3>
                <ul className="text-gray-600 text-sm space-y-1">
                  <li>• Right to know about data collection</li>
                  <li>• Right to delete personal information</li>
                  <li>• Right to opt-out of data sales</li>
                  <li>• Right to non-discrimination</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Questions About Privacy?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Privacy Officer</h3>
              <div className="space-y-2 text-gray-700">
                <div className="flex items-center gap-2">
                  <Mail size={16} className="text-blue-600" />
                  <span>privacy@flexpesaai.com</span>
                </div>
                <p className="text-sm text-gray-600">
                  For privacy-related questions, data requests, or concerns about how we handle your information.
                </p>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">General Support</h3>
              <div className="space-y-2 text-gray-700">
                <div className="flex items-center gap-2">
                  <Mail size={16} className="text-blue-600" />
                  <span>support@flexpesaai.com</span>
                </div>
                <p className="text-sm text-gray-600">
                  For general questions about our platform, features, or account management.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-blue-200">
            <p className="text-gray-700 text-sm">
              <strong>Response Time:</strong> We aim to respond to all privacy inquiries within 30 days.
              For urgent matters, please mark your email as &#34;URGENT - Privacy Request.&#34;
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
