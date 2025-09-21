'use client'
import React from 'react';
import { FileText, Shield, AlertTriangle, Users, CreditCard, Scale, Calendar, Mail } from 'lucide-react';
import Header from '@/components/Header';

export default function TermsPage() {
  const sections = [
    {
      id: 'acceptance',
      title: 'Acceptance of Terms',
      icon: FileText,
      content: `By accessing or using FlexPesaAi's services, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing our services. These terms constitute a legally binding agreement between you and FlexPesaAi, Inc.`
    },
    {
      id: 'services',
      title: 'Description of Services',
      icon: Users,
      content: `FlexPesaAi provides a portfolio management and analysis platform that integrates with various brokerage accounts to offer investment insights, AI-powered recommendations, and portfolio tracking. Our services include but are not limited to:`,
      list: [
        'Real-time portfolio tracking and analysis',
        'AI-powered investment recommendations and insights',
        'Integration with supported brokerage platforms',
        'Performance analytics and reporting',
        'Risk assessment and portfolio optimization tools',
        'Market data and financial information aggregation'
      ]
    },
    {
      id: 'accounts',
      title: 'User Accounts and Registration',
      icon: Shield,
      content: `To use our services, you must create an account and provide accurate, complete information. You are responsible for:`,
      list: [
        'Maintaining the confidentiality of your account credentials',
        'All activities that occur under your account',
        'Notifying us immediately of any unauthorized use',
        'Providing accurate and up-to-date information',
        'Complying with all applicable laws and regulations'
      ]
    },
    {
      id: 'financial',
      title: 'Financial Disclaimers',
      icon: AlertTriangle,
      content: `IMPORTANT: FlexPesaAi is NOT a registered investment advisor, broker-dealer, or financial advisor. Our services are for informational purposes only.`,
      list: [
        'All investment recommendations are for educational purposes only',
        'We do not provide personalized investment advice',
        'Past performance does not guarantee future results',
        'All investments carry risk of loss',
        'You should consult with qualified financial professionals before making investment decisions',
        'We are not responsible for investment losses resulting from use of our platform'
      ]
    },
    {
      id: 'data',
      title: 'Data Usage and Third-Party Integrations',
      icon: Users,
      content: `By using our services, you authorize us to:`,
      list: [
        'Access read-only data from your connected brokerage accounts',
        'Aggregate and analyze your portfolio information',
        'Provide insights based on your investment data',
        'Store your data securely in accordance with our Privacy Policy',
        'Use anonymized, aggregated data for service improvement'
      ],
      note: 'We NEVER have access to your brokerage login credentials or the ability to execute trades on your behalf.'
    },
    {
      id: 'payments',
      title: 'Payments and Subscriptions',
      icon: CreditCard,
      content: `Subscription fees are charged in advance and are non-refundable except as required by law. By subscribing, you agree to:`,
      list: [
        'Pay all applicable fees and taxes',
        'Automatic renewal of subscriptions unless cancelled',
        'Price changes with 30 days notice',
        'Cancellation at any time with access continuing until period end',
        'No refunds for partial months of service'
      ]
    },
    {
      id: 'prohibited',
      title: 'Prohibited Uses',
      icon: Scale,
      content: `You may not use our services to:`,
      list: [
        'Violate any laws or regulations',
        'Infringe on intellectual property rights',
        'Transmit malicious code or attempt to breach security',
        'Share your account access with others',
        'Use automated systems to access our services without permission',
        'Reverse engineer or attempt to extract our algorithms',
        'Use our services for unauthorized commercial purposes'
      ]
    }
  ];

  const legalNotices = [
    {
      title: 'Limitation of Liability',
      content: 'IN NO EVENT SHALL FlexPesaAi BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, OR USE, ARISING OUT OF OR RELATED TO YOUR USE OF OUR SERVICES.'
    },
    {
      title: 'Indemnification',
      content: 'You agree to indemnify and hold harmless FlexPesaAi and its officers, directors, employees, and agents from any claims, damages, or expenses arising from your use of our services or violation of these terms.'
    },
    {
      title: 'Governing Law',
      content: 'These terms are governed by the laws of the State of California, without regard to conflict of law principles. Any disputes will be resolved in the courts of San Francisco County, California.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Header
          title="Terms of Service"
          subtitle="Legal terms and conditions for using FlexPesaAi"
        />

        {/* Last Updated */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="text-blue-600" size={20} />
            <span className="font-medium text-blue-900">Effective Date: January 15, 2024</span>
          </div>
          <p className="text-blue-700 text-sm">
            These terms were last updated on January 15, 2024. We&#39;ll notify users of material changes via email and in-app notifications.
          </p>
        </div>

        {/* Important Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-yellow-600 mt-1" size={24} />
            <div>
              <h3 className="font-semibold text-yellow-900 mb-2">Important Financial Disclaimer</h3>
              <p className="text-yellow-800 text-sm leading-relaxed">
                FlexPesaAi is not a registered investment advisor. All information provided is for educational
                purposes only and should not be considered as personalized investment advice. Please consult
                with qualified financial professionals before making investment decisions.
              </p>
            </div>
          </div>
        </div>

        {/* Introduction */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Agreement Overview</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 text-lg leading-relaxed mb-4">
              Welcome to FlexPesaAi. These Terms of Service (&#34;Terms&#34;) govern your access to and use of our
              portfolio management platform, including our website, mobile applications, and related services
              (collectively, the &#34;Services&#34;).
            </p>
            <p className="text-gray-600 leading-relaxed">
              By creating an account or using our Services, you agree to these Terms. Please read them carefully.
              If you don&#39;t agree to these Terms, you may not use our Services.
            </p>
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

              <div className="prose prose-gray max-w-none">
                <p className="text-gray-600 leading-relaxed mb-4">{section.content}</p>

                {section.list && (
                  <ul className="space-y-2 mb-4">
                    {section.list.map((item, itemIndex) => (
                      <li key={itemIndex} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-gray-600">{item}</span>
                      </li>
                    ))}
                  </ul>
                )}

                {section.note && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 text-sm font-medium">{section.note}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Intellectual Property */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Intellectual Property Rights</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 leading-relaxed mb-4">
              The Services and their original content, features, and functionality are and will remain the
              exclusive property of FlexPesaAi, Inc. and its licensors. The Services are protected by
              copyright, trademark, and other laws.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Our Rights</h3>
                <ul className="text-gray-600 text-sm space-y-1">
                  <li>• All proprietary algorithms and AI models</li>
                  <li>• Software, design, and user interface</li>
                  <li>• Trademarks, logos, and brand elements</li>
                  <li>• Aggregated and anonymized data insights</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Rights</h3>
                <ul className="text-gray-600 text-sm space-y-1">
                  <li>• Your personal financial data</li>
                  <li>• Content you create using our platform</li>
                  <li>• Right to export your data</li>
                  <li>• Limited license to use our Services</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Privacy and Data */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Privacy and Data Protection</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 leading-relaxed mb-4">
              Your privacy is important to us. Our collection and use of personal information in connection
              with the Services is described in our Privacy Policy, which is incorporated by reference into these Terms.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">Key Privacy Commitments</h3>
              <ul className="text-blue-800 text-sm space-y-2">
                <li className="flex items-start gap-2">
                  <Shield size={16} className="mt-0.5 flex-shrink-0" />
                  <span>Bank-grade security for all financial data</span>
                </li>
                <li className="flex items-start gap-2">
                  <Shield size={16} className="mt-0.5 flex-shrink-0" />
                  <span>No selling of personal information to third parties</span>
                </li>
                <li className="flex items-start gap-2">
                  <Shield size={16} className="mt-0.5 flex-shrink-0" />
                  <span>User control over data sharing and retention</span>
                </li>
                <li className="flex items-start gap-2">
                  <Shield size={16} className="mt-0.5 flex-shrink-0" />
                  <span>Compliance with GDPR, CCPA, and other privacy laws</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Legal Notices */}
        <div className="bg-gray-900 text-white rounded-lg p-8 mt-8">
          <h2 className="text-2xl font-bold mb-6">Legal Disclaimers</h2>
          <div className="space-y-6">
            {legalNotices.map((notice, index) => (
              <div key={index}>
                <h3 className="text-lg font-semibold mb-3">{notice.title}</h3>
                <p className="text-gray-300 text-sm leading-relaxed">{notice.content}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Modifications and Termination */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Modifications and Termination</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Changes to Terms</h3>
              <p className="text-gray-600 text-sm mb-3">
                We may modify these Terms at any time. We&#39;ll provide notice of material changes through:
              </p>
              <ul className="text-gray-600 text-sm space-y-1">
                <li>• Email notifications to registered users</li>
                <li>• In-app notifications and banners</li>
                <li>• Updates to this page with effective dates</li>
                <li>• At least 30 days notice for material changes</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Account Termination</h3>
              <p className="text-gray-600 text-sm mb-3">
                Either party may terminate this agreement at any time:
              </p>
              <ul className="text-gray-600 text-sm space-y-1">
                <li>• You can cancel your account in settings</li>
                <li>• We may suspend accounts for violations</li>
                <li>• Data export available before termination</li>
                <li>• No refunds for prepaid subscription periods</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-8 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Questions About These Terms?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Legal Department</h3>
              <div className="space-y-2 text-gray-700">
                <div className="flex items-center gap-2">
                  <Mail size={16} className="text-blue-600" />
                  <span>legal@flexpesaai.com</span>
                </div>
                <p className="text-sm text-gray-600">
                  For questions about these terms, legal compliance, or contractual matters.
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
                  For general questions about our platform, features, or how to use our services.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-blue-200">
            <p className="text-gray-700 text-sm">
              <strong>Address:</strong> FlexPesaAi, Inc., 123 Market Street, Suite 500, San Francisco, CA 94105
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
