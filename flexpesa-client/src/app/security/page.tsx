'use client'
import React from 'react';
import { Shield, Lock, Eye, Server, Users, CheckCircle, AlertTriangle, Globe, FileText, Zap } from 'lucide-react';
import LandingNavigation from '@/components/LandingNavigation';

export default function SecurityPage() {
  const securityMeasures = [
    {
      title: 'Data Encryption',
      icon: Lock,
      description: 'End-to-end encryption for all data transmission and storage',
      details: [
        'AES-256 encryption for data at rest',
        'TLS 1.3 for data in transit',
        'End-to-end encryption for sensitive data',
        'Hardware security modules (HSMs) for key management'
      ],
      status: 'Active',
      color: 'green'
    },
    {
      title: 'Access Controls',
      icon: Users,
      description: 'Multi-layered authentication and authorization systems',
      details: [
        'Multi-factor authentication (MFA) required',
        'Role-based access control (RBAC)',
        'Principle of least privilege',
        'Regular access reviews and audits'
      ],
      status: 'Active',
      color: 'green'
    },
    {
      title: 'Infrastructure Security',
      icon: Server,
      description: 'Secure cloud infrastructure with continuous monitoring',
      details: [
        'AWS/Azure enterprise-grade infrastructure',
        'Network segmentation and firewalls',
        'Intrusion detection and prevention',
        'Regular vulnerability assessments'
      ],
      status: 'Active',
      color: 'green'
    },
    {
      title: 'Privacy Protection',
      icon: Eye,
      description: 'Comprehensive privacy controls and data minimization',
      details: [
        'Data minimization principles',
        'Privacy by design architecture',
        'User-controlled data sharing',
        'Regular privacy impact assessments'
      ],
      status: 'Active',
      color: 'green'
    }
  ];

  const certifications = [
    {
      name: 'SOC 2 Type II',
      description: 'Independent audit of security controls and processes',
      icon: Shield,
      status: 'Certified',
      validUntil: 'December 2024'
    },
    {
      name: 'ISO 27001',
      description: 'International standard for information security management',
      icon: Globe,
      status: 'Certified',
      validUntil: 'March 2025'
    },
    {
      name: 'PCI DSS Level 1',
      description: 'Payment card industry data security standard compliance',
      icon: Lock,
      status: 'Compliant',
      validUntil: 'Ongoing'
    },
    {
      name: 'GDPR Compliant',
      description: 'European Union General Data Protection Regulation',
      icon: FileText,
      status: 'Compliant',
      validUntil: 'Ongoing'
    }
  ];

  const securityPractices = [
    {
      category: 'Development Security',
      practices: [
        'Secure software development lifecycle (SSDLC)',
        'Code review and static analysis',
        'Dependency scanning and management',
        'Penetration testing by third parties',
        'Bug bounty program'
      ]
    },
    {
      category: 'Operational Security',
      practices: [
        '24/7 security operations center (SOC)',
        'Incident response procedures',
        'Regular security training for employees',
        'Background checks for all personnel',
        'Vendor risk management program'
      ]
    },
    {
      category: 'Data Protection',
      practices: [
        'Data classification and handling procedures',
        'Regular data backups and recovery testing',
        'Data retention and disposal policies',
        'Cross-border data transfer safeguards',
        'User consent and preference management'
      ]
    }
  ];

  const threatProtection = [
    {
      threat: 'Unauthorized Access',
      protection: 'Multi-factor authentication, session management, and access logging',
      status: 'Protected'
    },
    {
      threat: 'Data Breaches',
      protection: 'Encryption, network segmentation, and continuous monitoring',
      status: 'Protected'
    },
    {
      threat: 'Malware & Viruses',
      protection: 'Endpoint protection, email filtering, and behavioral analysis',
      status: 'Protected'
    },
    {
      threat: 'DDoS Attacks',
      protection: 'Content delivery network and traffic analysis',
      status: 'Protected'
    },
    {
      threat: 'Social Engineering',
      protection: 'Employee training and verification procedures',
      status: 'Protected'
    },
    {
      threat: 'Insider Threats',
      protection: 'Access controls, activity monitoring, and regular audits',
      status: 'Protected'
    }
  ];

  const incidentResponse = [
    {
      phase: 'Detection',
      description: 'Automated monitoring systems and threat intelligence',
      timeframe: '< 5 minutes'
    },
    {
      phase: 'Analysis',
      description: 'Security team investigation and impact assessment',
      timeframe: '< 30 minutes'
    },
    {
      phase: 'Containment',
      description: 'Isolate affected systems and prevent spread',
      timeframe: '< 1 hour'
    },
    {
      phase: 'Recovery',
      description: 'Restore services and implement additional safeguards',
      timeframe: '< 4 hours'
    },
    {
      phase: 'Lessons Learned',
      description: 'Post-incident review and security improvements',
      timeframe: '< 48 hours'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <LandingNavigation currentPage="security" />

      <div className="page-container pt-20">
        <div className="content-wrapper">
          <div className="text-center page-header">
            <h1 className="page-title">Security & Trust</h1>
            <p className="page-subtitle mt-4">Bank-grade security protecting your financial data</p>
          </div>

          {/* Security Overview */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-8 text-white section-spacing">
            <div className="text-center subsection-spacing">
              <Shield className="mx-auto mb-4" size={64} />
              <h2 className="text-3xl font-bold mb-4">Your Security is Our Priority</h2>
              <p className="text-xl text-blue-100 max-w-3xl mx-auto">
                We employ the same security standards as major financial institutions to protect your
                sensitive financial data and ensure your privacy.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold">256-bit</div>
                <div className="text-blue-200">SSL Encryption</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">SOC 2</div>
                <div className="text-blue-200">Type II Certified</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">24/7</div>
                <div className="text-blue-200">Security Monitoring</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">99.9%</div>
                <div className="text-blue-200">Uptime SLA</div>
              </div>
            </div>
          </div>

          {/* Security Measures */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 section-spacing">
            {securityMeasures.map((measure, index) => (
              <div key={index} className="card">
                <div className="flex items-center gap-3 subsection-spacing">
                  <measure.icon className={`text-${measure.color}-600`} size={32} />
                  <div>
                    <h3 className="card-title">{measure.title}</h3>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium bg-${measure.color}-100 text-${measure.color}-800`}>
                      {measure.status}
                    </span>
                  </div>
                </div>

                <p className="card-subtitle subsection-spacing">{measure.description}</p>

                <ul className="space-y-2">
                  {measure.details.map((detail, detailIndex) => (
                    <li key={detailIndex} className="flex items-center gap-2">
                      <CheckCircle className="text-green-600 flex-shrink-0" size={16} />
                      <span className="text-gray-700 text-sm">{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Certifications */}
          <div className="card-large section-spacing">
            <h2 className="section-title subsection-spacing text-center">Security Certifications & Compliance</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {certifications.map((cert, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6 text-center hover:shadow-md transition-shadow">
                  <cert.icon className="text-blue-600 mx-auto mb-4" size={48} />
                  <h3 className="card-title mb-2">{cert.name}</h3>
                  <p className="card-subtitle mb-3">{cert.description}</p>
                  <div className="space-y-1">
                    <div className="flex items-center justify-center gap-2">
                      <CheckCircle className="text-green-600" size={16} />
                      <span className="text-green-700 text-sm font-medium">{cert.status}</span>
                    </div>
                    <div className="text-gray-500 text-xs">Valid until {cert.validUntil}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Security Practices */}
          <div className="card-large section-spacing">
            <h2 className="section-title subsection-spacing">Security Practices & Procedures</h2>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {securityPractices.map((category, index) => (
                <div key={index}>
                  <h3 className="card-title subsection-spacing">{category.category}</h3>
                  <ul className="space-y-3">
                    {category.practices.map((practice, practiceIndex) => (
                      <li key={practiceIndex} className="flex items-start gap-3">
                        <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={16} />
                        <span className="text-gray-700 text-sm">{practice}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Threat Protection */}
          <div className="card-large section-spacing">
            <h2 className="section-title subsection-spacing">Threat Protection Matrix</h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-4 px-4 font-semibold text-gray-900">Threat Type</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-900">Protection Measures</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-900">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {threatProtection.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100">
                      <td className="py-4 px-4 font-medium text-gray-900">{item.threat}</td>
                      <td className="py-4 px-4 text-gray-700">{item.protection}</td>
                      <td className="py-4 px-4 text-center">
                        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-green-100 text-green-800 text-sm font-medium">
                          <CheckCircle size={14} />
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Incident Response */}
          <div className="card-large section-spacing">
            <h2 className="section-title subsection-spacing">Incident Response Process</h2>

            <div className="relative">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                {incidentResponse.map((phase, index) => (
                  <div key={index} className="relative">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                      <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                        {index + 1}
                      </div>
                      <h3 className="card-title mb-2">{phase.phase}</h3>
                      <p className="card-subtitle mb-3">{phase.description}</p>
                      <div className="text-blue-600 font-medium text-sm">{phase.timeframe}</div>
                    </div>

                    {index < incidentResponse.length - 1 && (
                      <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                        <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                          <Zap className="text-white" size={12} />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Responsible Disclosure */}
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 border border-blue-200 rounded-lg p-8 section-spacing">
            <h2 className="section-title subsection-spacing">Responsible Disclosure & Bug Bounty</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="card-title subsection-spacing">Report Security Issues</h3>
                <p className="card-subtitle subsection-spacing">
                  We welcome security researchers to help us maintain the highest security standards.
                  If you discover a security vulnerability, please report it responsibly.
                </p>
                <ul className="space-y-2 text-gray-700 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="text-green-600" size={16} />
                    <span>Email: security@flexpesaai.com</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="text-green-600" size={16} />
                    <span>PGP key available for encrypted communication</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="text-green-600" size={16} />
                    <span>Response within 24 hours</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="card-title subsection-spacing">Bug Bounty Program</h3>
                <p className="card-subtitle subsection-spacing">
                  We offer rewards for valid security vulnerabilities discovered in our systems.
                </p>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg border">
                    <span className="text-gray-700 font-medium">Critical</span>
                    <span className="text-green-600 font-bold">$5,000 - $10,000</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg border">
                    <span className="text-gray-700 font-medium">High</span>
                    <span className="text-green-600 font-bold">$1,000 - $5,000</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg border">
                    <span className="text-gray-700 font-medium">Medium</span>
                    <span className="text-green-600 font-bold">$250 - $1,000</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg border">
                    <span className="text-gray-700 font-medium">Low</span>
                    <span className="text-green-600 font-bold">$50 - $250</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Security Contact */}
          <div className="bg-gray-900 text-white rounded-lg p-8 section-spacing">
            <h2 className="text-2xl font-bold mb-6">Security Contact Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">General Security Inquiries</h3>
                <div className="space-y-2">
                  <p>Email: security@flexpesaai.com</p>
                  <p>Phone: +1 (555) 123-4567 ext. 911</p>
                  <p>Response Time: Within 24 hours</p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Emergency Security Incidents</h3>
                <div className="space-y-2">
                  <p>Email: emergency@flexpesaai.com</p>
                  <p>Phone: +1 (555) 911-HELP (4357)</p>
                  <p>Response Time: Within 1 hour (24/7)</p>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-gray-700">
              <p className="text-gray-300 text-sm">
                For non-security related issues, please use our regular support channels at support@flexpesaai.com
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
