'use client'
import React, { useState } from 'react';
import { Check, X, Star, Shield, Users, BarChart3, TrendingUp, Clock, ArrowRight, Crown } from 'lucide-react';
import LandingNavigation from '@/components/LandingNavigation';
import Link from 'next/link';

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');

  const plans = [
    {
      name: 'Starter',
      icon: TrendingUp,
      description: 'Perfect for individual investors getting started',
      monthlyPrice: 0,
      annualPrice: 0,
      savings: 0,
      color: 'gray',
      popular: false,
      features: [
        { name: 'Up to 2 connected accounts', included: true },
        { name: 'Basic portfolio tracking', included: true },
        { name: 'Market data updates', included: true },
        { name: 'Mobile app access', included: true },
        { name: 'Email support', included: true },
        { name: 'AI analysis', included: false },
        { name: 'Advanced analytics', included: false },
        { name: 'Priority support', included: false },
        { name: 'API access', included: false },
        { name: 'Custom reports', included: false }
      ],
      cta: 'Get Started Free',
      badge: 'Free Forever'
    },
    {
      name: 'Professional',
      icon: BarChart3,
      description: 'Advanced features for serious investors',
      monthlyPrice: 29,
      annualPrice: 24,
      savings: 17,
      color: 'blue',
      popular: true,
      features: [
        { name: 'Up to 10 connected accounts', included: true },
        { name: 'Real-time portfolio tracking', included: true },
        { name: 'AI-powered recommendations', included: true },
        { name: 'Advanced performance analytics', included: true },
        { name: 'Risk assessment tools', included: true },
        { name: 'Priority email support', included: true },
        { name: 'Custom alerts', included: true },
        { name: 'Export capabilities', included: true },
        { name: 'API access', included: false },
        { name: 'White-label options', included: false }
      ],
      cta: 'Start Free Trial',
      badge: 'Most Popular'
    },
    {
      name: 'Enterprise',
      icon: Crown,
      description: 'Complete solution for wealth management firms',
      monthlyPrice: 99,
      annualPrice: 82,
      savings: 20,
      color: 'purple',
      popular: false,
      features: [
        { name: 'Unlimited connected accounts', included: true },
        { name: 'Real-time data & analytics', included: true },
        { name: 'Advanced AI & ML insights', included: true },
        { name: 'Custom risk modeling', included: true },
        { name: 'Team collaboration tools', included: true },
        { name: 'Dedicated account manager', included: true },
        { name: 'Full API access', included: true },
        { name: 'White-label solutions', included: true },
        { name: 'Custom integrations', included: true },
        { name: 'SLA guarantee', included: true }
      ],
      cta: 'Contact Sales',
      badge: 'Best Value'
    }
  ];

  const features = [
    {
      category: 'Core Features',
      items: [
        { name: 'Portfolio Tracking', starter: true, pro: true, enterprise: true },
        { name: 'Real-time Data', starter: false, pro: true, enterprise: true },
        { name: 'Mobile App', starter: true, pro: true, enterprise: true },
        { name: 'Account Connections', starter: '2', pro: '10', enterprise: 'Unlimited' },
        { name: 'Historical Data', starter: '1 year', pro: '5 years', enterprise: 'Unlimited' }
      ]
    },
    {
      category: 'AI & Analytics',
      items: [
        { name: 'Basic Analytics', starter: true, pro: true, enterprise: true },
        { name: 'AI Recommendations', starter: false, pro: true, enterprise: true },
        { name: 'Risk Assessment', starter: false, pro: true, enterprise: true },
        { name: 'Custom Models', starter: false, pro: false, enterprise: true },
        { name: 'Predictive Analytics', starter: false, pro: false, enterprise: true }
      ]
    },
    {
      category: 'Support & Services',
      items: [
        { name: 'Email Support', starter: true, pro: true, enterprise: true },
        { name: 'Priority Support', starter: false, pro: true, enterprise: true },
        { name: 'Phone Support', starter: false, pro: false, enterprise: true },
        { name: 'Dedicated Manager', starter: false, pro: false, enterprise: true },
        { name: 'Training & Onboarding', starter: false, pro: false, enterprise: true }
      ]
    }
  ];

  const faqs = [
    {
      question: 'Can I change plans at any time?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and billing is prorated accordingly.'
    },
    {
      question: 'Is there a free trial available?',
      answer: 'Yes, we offer a 14-day free trial for all paid plans. No credit card required to start your trial.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards, PayPal, and ACH transfers for annual subscriptions. All payments are processed securely.'
    },
    {
      question: 'How secure is my financial data?',
      answer: 'We use bank-grade 256-bit SSL encryption and never store your brokerage login credentials. All data is encrypted at rest and in transit.'
    },
    {
      question: 'Can I cancel my subscription?',
      answer: 'Yes, you can cancel at any time. Your access continues until the end of your current billing period, and we don\'t charge cancellation fees.'
    },
    {
      question: 'Do you offer discounts for annual billing?',
      answer: 'Yes, annual subscribers save 17-20% compared to monthly billing. The savings are automatically applied at checkout.'
    }
  ];

  const getPrice = (plan: typeof plans[0]) => {
    if (plan.monthlyPrice === 0) return 'Free';
    const price = billingCycle === 'monthly' ? plan.monthlyPrice : plan.annualPrice;
    return `$${price}`;
  };

  const getPlanColor = (color: string) => {
    const colors = {
      gray: 'border-gray-200 bg-white',
      blue: 'border-blue-200 bg-blue-50 ring-2 ring-blue-500',
      purple: 'border-purple-200 bg-purple-50'
    };
    return colors[color as keyof typeof colors] || colors.gray;
  };

  const getButtonColor = (color: string) => {
    const colors = {
      gray: 'bg-gray-600 hover:bg-gray-700 text-white',
      blue: 'bg-blue-600 hover:bg-blue-700 text-white',
      purple: 'bg-purple-600 hover:bg-purple-700 text-white'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  const getBadgeColor = (color: string) => {
    const colors = {
      gray: 'bg-gray-100 text-gray-800',
      blue: 'bg-blue-100 text-blue-800',
      purple: 'bg-purple-100 text-purple-800'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <LandingNavigation currentPage="pricing" />

      <div className="page-container pt-20">
        <div className="content-wrapper">
          <div className="text-center page-header">
            <h1 className="page-title">Simple, Transparent Pricing</h1>
            <p className="page-subtitle mt-4">Choose the plan that fits your investment management needs</p>
          </div>

          {/* Billing Toggle */}
          <div className="flex justify-center subsection-spacing">
            <div className="bg-white rounded-lg p-1 border border-gray-200">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === 'monthly'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === 'annual'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Annual
                <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  Save up to 20%
                </span>
              </button>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 section-spacing">
            {plans.map((plan, index) => (
              <div key={index} className={`rounded-lg border p-8 relative ${getPlanColor(plan.color)}`}>
                {plan.badge && (
                  <div className={`absolute -top-3 left-1/2 transform -translate-x-1/2 px-4 py-1 rounded-full text-xs font-medium ${getBadgeColor(plan.color)}`}>
                    {plan.badge}
                  </div>
                )}

                <div className="text-center subsection-spacing">
                  <plan.icon className={`text-${plan.color === 'gray' ? 'gray' : plan.color}-600 mx-auto mb-4`} size={48} />
                  <h3 className="section-title mb-2">{plan.name}</h3>
                  <p className="section-subtitle mb-6">{plan.description}</p>

                  <div className="subsection-spacing">
                    <div className="text-5xl font-bold text-gray-900 mb-2">
                      {getPrice(plan)}
                      {plan.monthlyPrice > 0 && (
                        <span className="text-lg font-normal text-gray-600">
                          /{billingCycle === 'monthly' ? 'mo' : 'mo'}
                        </span>
                      )}
                    </div>
                    {billingCycle === 'annual' && plan.savings > 0 && (
                      <div className="text-sm text-green-600 font-medium">
                        Save {plan.savings}% with annual billing
                      </div>
                    )}
                    {billingCycle === 'annual' && plan.monthlyPrice > 0 && (
                      <div className="card-subtitle">
                        Billed annually (${plan.annualPrice * 12})
                      </div>
                    )}
                  </div>

                  <button className={`w-full py-3 px-6 rounded-lg font-medium transition-colors ${getButtonColor(plan.color)}`}>
                    {plan.cta}
                  </button>
                </div>

                <div className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center gap-3">
                      {feature.included ? (
                        <Check className="text-green-600 flex-shrink-0" size={20} />
                      ) : (
                        <X className="text-gray-400 flex-shrink-0" size={20} />
                      )}
                      <span className={`text-sm ${feature.included ? 'text-gray-700' : 'text-gray-400'}`}>
                        {feature.name}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Feature Comparison Table */}
          <div className="card-large section-spacing">
            <h2 className="section-title subsection-spacing text-center">Detailed Feature Comparison</h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-4 px-4 font-semibold text-gray-900">Features</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-900">Starter</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-900">Professional</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-900">Enterprise</th>
                  </tr>
                </thead>
                <tbody>
                  {features.map((category, categoryIndex) => (
                    <React.Fragment key={categoryIndex}>
                      <tr className="bg-gray-50">
                        <td colSpan={4} className="py-3 px-4 font-semibold text-gray-800 text-sm">
                          {category.category}
                        </td>
                      </tr>
                      {category.items.map((item, itemIndex) => (
                        <tr key={itemIndex} className="border-b border-gray-100">
                          <td className="py-3 px-4 text-gray-700">{item.name}</td>
                          <td className="py-3 px-4 text-center">
                            {typeof item.starter === 'boolean' ? (
                              item.starter ? (
                                <Check className="text-green-600 mx-auto" size={20} />
                              ) : (
                                <X className="text-gray-400 mx-auto" size={20} />
                              )
                            ) : (
                              <span className="text-gray-700">{item.starter}</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {typeof item.pro === 'boolean' ? (
                              item.pro ? (
                                <Check className="text-green-600 mx-auto" size={20} />
                              ) : (
                                <X className="text-gray-400 mx-auto" size={20} />
                              )
                            ) : (
                              <span className="text-gray-700">{item.pro}</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {typeof item.enterprise === 'boolean' ? (
                              item.enterprise ? (
                                <Check className="text-green-600 mx-auto" size={20} />
                              ) : (
                                <X className="text-gray-400 mx-auto" size={20} />
                              )
                            ) : (
                              <span className="text-gray-700">{item.enterprise}</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="card-large section-spacing">
            <h2 className="section-title subsection-spacing text-center">Frequently Asked Questions</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {faqs.map((faq, index) => (
                <div key={index} className="space-y-3">
                  <h3 className="card-title">{faq.question}</h3>
                  <p className="card-subtitle leading-relaxed">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 section-spacing">
            <div className="text-center">
              <Shield className="text-blue-600 mx-auto mb-3" size={32} />
              <h3 className="card-title mb-1">Bank-Grade Security</h3>
              <p className="card-subtitle">256-bit SSL encryption</p>
            </div>
            <div className="text-center">
              <Clock className="text-green-600 mx-auto mb-3" size={32} />
              <h3 className="card-title mb-1">99.9% Uptime</h3>
              <p className="card-subtitle">Reliable service guarantee</p>
            </div>
            <div className="text-center">
              <Users className="text-purple-600 mx-auto mb-3" size={32} />
              <h3 className="card-title mb-1">15,000+ Users</h3>
              <p className="card-subtitle">Trusted by investors</p>
            </div>
            <div className="text-center">
              <Star className="text-yellow-600 mx-auto mb-3" size={32} />
              <h3 className="card-title mb-1">4.8/5 Rating</h3>
              <p className="card-subtitle">Customer satisfaction</p>
            </div>
          </div>

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-8 text-center text-white section-spacing">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-blue-100 subsection-spacing">
              Join thousands of investors who trust FlexPesaAi to manage their wealth intelligently.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium flex items-center gap-2">
                Start Your Free Trial
                <ArrowRight size={20} />
              </button>
              <Link href="/contact">
                <button className="border-2 border-white text-white px-8 py-3 rounded-lg hover:bg-white hover:text-blue-600 transition-colors font-medium">
                  Schedule a Demo
                </button>
              </Link>
            </div>
            <p className="text-blue-200 text-sm mt-4">No credit card required • Cancel anytime</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-xl font-bold">FlexPesaAi</span>
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                Professional investment management powered by artificial intelligence.
                Make smarter decisions with real-time insights and analytics.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
                <li><Link href="/api-docs" className="hover:text-white transition-colors">API</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="/help" className="hover:text-white transition-colors">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact Us</Link></li>
                <li><Link href="/status" className="hover:text-white transition-colors">Status</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2024 FlexPesaAi. All rights reserved. | <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link> | <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></p>
          </div>
        </div>
      </footer>
    </div>
  );
}
