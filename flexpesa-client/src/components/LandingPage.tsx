import React, { useState, useEffect } from 'react';
import { TrendingUp, Shield, Brain, Zap, BarChart3, Users, ArrowRight, Check, Star, Activity, DollarSign, Clock, Globe, ChevronDown } from 'lucide-react';

const LandingPage = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: Activity,
      title: "Real-time Market Data",
      description: "Live price updates and market insights powered by comprehensive data feeds",
      color: "from-blue-500 to-indigo-600"
    },
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Advanced sentiment analysis and intelligent portfolio recommendations",
      color: "from-purple-500 to-pink-600"
    },
    {
      icon: Shield,
      title: "Multi-Account Management",
      description: "Unified view across Wells Fargo, Robinhood, Cash App, and more",
      color: "from-green-500 to-emerald-600"
    },
    {
      icon: BarChart3,
      title: "Performance Analytics",
      description: "Sophisticated metrics including Sharpe ratio, beta, and risk assessment",
      color: "from-orange-500 to-red-600"
    },
    {
      icon: Zap,
      title: "Instant Insights",
      description: "Real-time portfolio health monitoring with intelligent alerts",
      color: "from-cyan-500 to-blue-600"
    },
    {
      icon: Globe,
      title: "Enterprise Security",
      description: "Bank-grade security with multi-factor authentication and encryption",
      color: "from-teal-500 to-green-600"
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Portfolio Manager",
      company: "Firstone Bank",
      content: "The AI analysis capabilities have transformed how I make investment decisions. The platform's insights are consistently accurate and actionable.",
      rating: 5
    },
    {
      name: "Michael Rodriguez",
      role: "Investment Advisor",
      company: "",
      content: "Finally, a platform that aggregates all my client accounts in one place. The real-time data and performance metrics are exceptional.",
      rating: 5
    },
    {
      name: "Jennifer Park",
      role: "Wealth Manager",
      company: "",
      content: "The risk analytics and benchmark comparisons help me provide better advice to my clients. It's like having a research team at my fingertips.",
      rating: 5
    }
  ];

  const stats = [
    { number: "$50B+", label: "Assets Under Management" },
    { number: "15,000+", label: "Active Portfolios" },
    { number: "99.9%", label: "Uptime Reliability" },
    { number: "< 100ms", label: "Data Latency" }
  ];

  const pricingPlans = [
    {
      name: "Professional",
      price: "$29",
      period: "/month",
      description: "Perfect for individual investors and advisors",
      features: [
        "Up to 5 connected accounts",
        "Real-time market data",
        "Basic AI analysis",
        "Performance tracking",
        "Mobile app access",
        "Email support"
      ],
      popular: false
    },
    {
      name: "Enterprise",
      price: "$99",
      period: "/month",
      description: "Advanced features for wealth management firms",
      features: [
        "Unlimited connected accounts",
        "Advanced AI recommendations",
        "Custom risk modeling",
        "White-label options",
        "API access",
        "Dedicated support",
        "Advanced analytics",
        "Team collaboration tools"
      ],
      popular: true
    },
    {
      name: "Institution",
      price: "Custom",
      period: "",
      description: "Tailored solutions for large institutions",
      features: [
        "Custom integrations",
        "Dedicated infrastructure",
        "Compliance reporting",
        "Advanced security",
        "24/7 support",
        "Training & onboarding",
        "Custom AI models",
        "Regulatory compliance"
      ],
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-lg border-b border-gray-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">PortfolioAI</span>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#analytics" className="text-gray-600 hover:text-gray-900 transition-colors">Analytics</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">Pricing</a>
              <a href="#security" className="text-gray-600 hover:text-gray-900 transition-colors">Security</a>
            </div>

            <div className="flex items-center space-x-4">
              <button className="text-gray-600 hover:text-gray-900 transition-colors">
                Sign In
              </button>
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl">
                Start Free Trial
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 bg-gradient-to-br from-gray-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="inline-flex items-center bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
                <Star className="w-4 h-4 mr-2" />
                Trusted by 15,000+ investors worldwide
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                Intelligent Portfolio
                <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> Management</span>
              </h1>

              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Harness the power of AI to optimize your investment strategy. Real-time analytics,
                risk assessment, and intelligent insights all in one sophisticated platform.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center group">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-all duration-200 flex items-center justify-center">
                  Watch Demo
                  <ChevronDown className="ml-2 w-5 h-5" />
                </button>
              </div>

              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <div className="flex items-center">
                  <Check className="w-4 h-4 text-green-500 mr-2" />
                  No credit card required
                </div>
                <div className="flex items-center">
                  <Check className="w-4 h-4 text-green-500 mr-2" />
                  14-day free trial
                </div>
                <div className="flex items-center">
                  <Check className="w-4 h-4 text-green-500 mr-2" />
                  Cancel anytime
                </div>
              </div>
            </div>

            <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              <div className="relative">
                <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">Portfolio Overview</h3>
                      <div className="flex items-center text-green-600">
                        <TrendingUp className="w-4 h-4 mr-1" />
                        <span className="text-sm font-medium">+12.3%</span>
                      </div>
                    </div>
                    <div className="text-3xl font-bold text-gray-900 mb-2">$1,247,891</div>
                    <div className="text-sm text-gray-500">Total Portfolio Value</div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg">
                      <div className="text-lg font-bold text-green-700">+$47,231</div>
                      <div className="text-sm text-green-600">Total Gains</div>
                    </div>
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg">
                      <div className="text-lg font-bold text-blue-700">1.34</div>
                      <div className="text-sm text-blue-600">Sharpe Ratio</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Wells Fargo</span>
                      <span className="text-sm text-gray-900">$456,789</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Robinhood</span>
                      <span className="text-sm text-gray-900">$324,156</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Cash App</span>
                      <span className="text-sm text-gray-900">$287,943</span>
                    </div>
                  </div>
                </div>

                {/* Floating AI insight */}
                <div className="absolute -bottom-4 -right-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-lg shadow-lg">
                  <div className="flex items-center mb-2">
                    <Brain className="w-4 h-4 mr-2" />
                    <span className="text-sm font-medium">AI Insight</span>
                  </div>
                  <div className="text-xs">Consider rebalancing tech exposure</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl lg:text-4xl font-bold text-white mb-2">{stat.number}</div>
                <div className="text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything you need to manage wealth intelligently
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Professional-grade tools and insights that adapt to your investment style and goals
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="group hover:shadow-lg transition-all duration-300 bg-white border border-gray-100 rounded-xl p-8 hover:-translate-y-1">
                <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by investment professionals
            </h2>
            <p className="text-xl text-gray-600">
              See what industry leaders say about our platform
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8 lg:p-12">
            <div className="text-center">
              <div className="flex justify-center mb-4">
                {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                  <Star key={i} className="w-6 h-6 text-yellow-400 fill-current" />
                ))}
              </div>

              <blockquote className="text-xl lg:text-2xl text-gray-900 mb-8 leading-relaxed">
                &#34;{testimonials[currentTestimonial].content}&#34;
              </blockquote>

              <div className="flex items-center justify-center">
                <div className="text-center">
                  <div className="font-semibold text-gray-900">{testimonials[currentTestimonial].name}</div>
                  <div className="text-gray-600">{testimonials[currentTestimonial].role}</div>
                  <div className="text-blue-600 font-medium">{testimonials[currentTestimonial].company}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to transform your investment approach?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of investors who trust PortfolioAI to manage their wealth intelligently.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-4 rounded-lg hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl font-medium">
              Start Your Free Trial
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-lg hover:bg-white hover:text-blue-600 transition-all duration-200 font-medium">
              Schedule a Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">PortfolioAI</span>
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                Professional investment management powered by artificial intelligence.
                Make smarter decisions with real-time insights and analytics.
              </p>
              <div className="flex space-x-4">
                <div className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-colors cursor-pointer">
                  <Users className="w-5 h-5" />
                </div>
                <div className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-colors cursor-pointer">
                  <Globe className="w-5 h-5" />
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Analytics</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2024 PortfolioAI. All rights reserved. | Privacy Policy | Terms of Service</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
