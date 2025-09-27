'use client'
import React, { useState } from 'react';
import { Mail, Phone, MapPin, Clock, MessageCircle, Send, CheckCircle, AlertCircle, Users, BookOpen, Zap } from 'lucide-react';
import Header from '@/components/Header';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: 'general',
    message: '',
    priority: 'normal'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    setTimeout(() => {
      setSubmitStatus('success');
      setIsSubmitting(false);
      setFormData({ name: '', email: '', subject: 'general', message: '', priority: 'normal' });
    }, 2000);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const contactMethods = [
    {
      icon: MessageCircle,
      title: 'Live Chat',
      description: 'Get instant help from our support team',
      details: 'Available 24/7',
      action: 'Start Chat',
      color: 'blue'
    },
    {
      icon: Mail,
      title: 'Email Support',
      description: 'Send us a detailed message',
      details: 'support@flexpesaai.com',
      action: 'Send Email',
      color: 'green'
    },
    {
      icon: Phone,
      title: 'Phone Support',
      description: 'Speak directly with our team',
      details: '+1 (555) 123-4567',
      action: 'Call Now',
      color: 'purple'
    }
  ];

  const supportOptions = [
    {
      icon: Users,
      title: 'Account & Billing',
      description: 'Questions about your subscription, billing, or account settings',
      responseTime: '< 2 hours'
    },
    {
      icon: Zap,
      title: 'Technical Support',
      description: 'Issues with app functionality, integrations, or performance',
      responseTime: '< 1 hour'
    },
    {
      icon: BookOpen,
      title: 'General Inquiries',
      description: 'Product questions, feature requests, or general information',
      responseTime: '< 4 hours'
    }
  ];

  const offices = [
    {
      city: 'San Francisco',
      address: '123 Market Street, Suite 500',
      zipCode: 'San Francisco, CA 94105',
      phone: '+1 (555) 123-4567',
      type: 'Headquarters'
    },
    {
      city: 'New York',
      address: '456 Broadway, Floor 12',
      zipCode: 'New York, NY 10013',
      phone: '+1 (555) 234-5678',
      type: 'East Coast Office'
    },
    {
      city: 'Austin',
      address: '789 Congress Ave, Suite 200',
      zipCode: 'Austin, TX 78701',
      phone: '+1 (555) 345-6789',
      type: 'Operations Center'
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-50 border-blue-200 hover:bg-blue-100',
      green: 'text-green-600 bg-green-50 border-green-200 hover:bg-green-100',
      purple: 'text-purple-600 bg-purple-50 border-purple-200 hover:bg-purple-100'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <Header
          title="Contact Us"
          subtitle="Get in touch with our team - we're here to help"
        />

        {/* Contact Methods */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 section-spacing">
          {contactMethods.map((method, index) => (
            <div key={index} className={`border rounded-lg p-6 cursor-pointer transition-all duration-200 ${getColorClasses(method.color)}`}>
              <method.icon className={`text-${method.color}-600 mb-4`} size={32} />
              <h3 className="card-title mb-2">{method.title}</h3>
              <p className="card-subtitle mb-3">{method.description}</p>
              <div className="text-sm font-medium text-gray-700 mb-4">{method.details}</div>
              <button className={`w-full bg-${method.color}-600 text-white py-2 px-4 rounded-lg hover:bg-${method.color}-700 transition-colors text-sm font-medium`}>
                {method.action}
              </button>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <div className="card-large">
            <h2 className="section-title subsection-spacing">Send us a Message</h2>

            {submitStatus === 'success' && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 subsection-spacing">
                <div className="flex items-center gap-2">
                  <CheckCircle className="text-green-600" size={20} />
                  <span className="font-medium text-green-900">Message sent successfully!</span>
                </div>
                <p className="text-green-700 text-sm mt-1">We&#39;ll get back to you within 24 hours.</p>
              </div>
            )}

            {submitStatus === 'error' && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 subsection-spacing">
                <div className="flex items-center gap-2">
                  <AlertCircle className="text-red-600" size={20} />
                  <span className="font-medium text-red-900">Failed to send message</span>
                </div>
                <p className="text-red-700 text-sm mt-1">Please try again or contact us directly.</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Name *</label>
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Your full name"
                  />
                </div>

                <div>
                  <label className="form-label">Email *</label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="your@email.com"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">Subject</label>
                  <select
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="general">General Inquiry</option>
                    <option value="technical">Technical Support</option>
                    <option value="billing">Billing & Account</option>
                    <option value="feature">Feature Request</option>
                    <option value="partnership">Partnership</option>
                  </select>
                </div>

                <div>
                  <label className="form-label">Priority</label>
                  <select
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="form-label">Message *</label>
                <textarea
                  name="message"
                  required
                  rows={6}
                  value={formData.message}
                  onChange={handleInputChange}
                  className="form-input resize-none"
                  placeholder="Tell us how we can help you..."
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-primary w-full btn-large flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <Send size={20} />
                    Send Message
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Support Info & Offices */}
          <div className="space-y-8">
            {/* Support Categories */}
            <div className="card">
              <h3 className="card-title subsection-spacing">How We Can Help</h3>
              <div className="space-y-4">
                {supportOptions.map((option, index) => (
                  <div key={index} className="flex gap-4 p-4 border border-gray-100 rounded-lg">
                    <option.icon className="text-blue-600 mt-1" size={24} />
                    <div>
                      <h4 className="card-title mb-1">{option.title}</h4>
                      <p className="card-subtitle mb-2">{option.description}</p>
                      <div className="flex items-center gap-2">
                        <Clock size={14} className="text-gray-400" />
                        <span className="text-xs text-gray-500">Response time: {option.responseTime}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Office Locations */}
            <div className="card">
              <h3 className="card-title subsection-spacing">Our Offices</h3>
              <div className="space-y-6">
                {offices.map((office, index) => (
                  <div key={index} className="border-b border-gray-100 last:border-b-0 pb-4 last:pb-0">
                    <div className="flex items-start gap-3">
                      <MapPin className="text-gray-400 mt-1" size={20} />
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="card-title">{office.city}</h4>
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            {office.type}
                          </span>
                        </div>
                        <p className="card-subtitle">{office.address}</p>
                        <p className="card-subtitle">{office.zipCode}</p>
                        <p className="card-subtitle">{office.phone}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Business Hours */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
              <h3 className="card-title text-gray-900 mb-4">Business Hours</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Monday - Friday</span>
                  <span className="font-medium text-gray-900">9:00 AM - 6:00 PM PST</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Saturday</span>
                  <span className="font-medium text-gray-900">10:00 AM - 4:00 PM PST</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Sunday</span>
                  <span className="font-medium text-gray-900">Closed</span>
                </div>
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <div className="flex items-center gap-2 text-blue-700">
                    <MessageCircle size={16} />
                    <span className="text-sm font-medium">Live Chat available 24/7</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
