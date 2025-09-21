'use client'
import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, XCircle, Clock, TrendingUp, Server, Database, Globe, Zap, Shield, RefreshCw, Calendar, Activity } from 'lucide-react';
import Header from '@/components/Header';

export default function StatusPage() {
  const [lastUpdated, setLastUpdated] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const updateTime = () => {
      setLastUpdated(new Date().toLocaleTimeString());
    };

    updateTime();

    if (autoRefresh) {
      const interval = setInterval(updateTime, 30000); // Update every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const overallStatus = {
    status: 'operational',
    message: 'All systems operational',
    lastIncident: '12 days ago',
    uptime: '99.98%'
  };

  const services = [
    {
      name: 'Portfolio API',
      description: 'Core portfolio management and data retrieval',
      status: 'operational',
      uptime: '99.99%',
      responseTime: '145ms',
      icon: Database
    },
    {
      name: 'Authentication Service',
      description: 'User login and access management',
      status: 'operational',
      uptime: '99.97%',
      responseTime: '89ms',
      icon: Shield
    },
    {
      name: 'Market Data Feed',
      description: 'Real-time market prices and financial data',
      status: 'operational',
      uptime: '99.95%',
      responseTime: '234ms',
      icon: TrendingUp
    },
    {
      name: 'AI Analysis Engine',
      description: 'Machine learning recommendations and insights',
      status: 'degraded',
      uptime: '99.89%',
      responseTime: '1.2s',
      icon: Zap
    },
    {
      name: 'Web Application',
      description: 'Frontend dashboard and user interface',
      status: 'operational',
      uptime: '99.98%',
      responseTime: '567ms',
      icon: Globe
    },
    {
      name: 'Mobile API',
      description: 'Mobile application backend services',
      status: 'operational',
      uptime: '99.96%',
      responseTime: '198ms',
      icon: Server
    },
    {
      name: 'Notification Service',
      description: 'Email, SMS, and push notifications',
      status: 'operational',
      uptime: '99.94%',
      responseTime: '89ms',
      icon: Activity
    },
    {
      name: 'File Storage',
      description: 'Document storage and backup systems',
      status: 'operational',
      uptime: '99.99%',
      responseTime: '156ms',
      icon: Database
    }
  ];

  const incidents = [
    {
      title: 'Intermittent AI Analysis Delays',
      status: 'investigating',
      severity: 'minor',
      startTime: '2024-01-15 14:30 UTC',
      description: 'Some users may experience slower than normal response times for AI portfolio analysis.',
      updates: [
        {
          time: '15:45 UTC',
          message: 'We have identified the issue with our ML processing pipeline and are working on a fix.',
          status: 'investigating'
        },
        {
          time: '14:30 UTC',
          message: 'We are investigating reports of slower AI analysis response times.',
          status: 'investigating'
        }
      ]
    }
  ];

  const pastIncidents = [
    {
      title: 'Market Data Feed Interruption',
      date: '2024-01-03',
      duration: '23 minutes',
      severity: 'major',
      resolved: true,
      summary: 'Temporary interruption in real-time market data due to upstream provider issues. Service was restored within 23 minutes.'
    },
    {
      title: 'Authentication Service Maintenance',
      date: '2023-12-28',
      duration: '45 minutes',
      severity: 'minor',
      resolved: true,
      summary: 'Scheduled maintenance on authentication infrastructure. Some users experienced brief login delays.'
    },
    {
      title: 'Database Performance Optimization',
      date: '2023-12-15',
      duration: '2 hours',
      severity: 'minor',
      resolved: true,
      summary: 'Database optimization performed during low-traffic hours. Portfolio loading times were temporarily slower.'
    }
  ];

  const metrics = [
    {
      title: 'Average Response Time',
      value: '247ms',
      change: '+12ms',
      trend: 'up',
      period: 'Last 24 hours'
    },
    {
      title: 'Success Rate',
      value: '99.97%',
      change: '+0.02%',
      trend: 'up',
      period: 'Last 24 hours'
    },
    {
      title: 'Active Users',
      value: '14,583',
      change: '+247',
      trend: 'up',
      period: 'Currently online'
    },
    {
      title: 'API Requests',
      value: '2.3M',
      change: '+15.2%',
      trend: 'up',
      period: 'Last 24 hours'
    }
  ];

  const uptimeData = [
    { date: '2024-01-14', uptime: 100 },
    { date: '2024-01-13', uptime: 99.98 },
    { date: '2024-01-12', uptime: 100 },
    { date: '2024-01-11', uptime: 100 },
    { date: '2024-01-10', uptime: 99.95 },
    { date: '2024-01-09', uptime: 100 },
    { date: '2024-01-08', uptime: 100 },
    { date: '2024-01-07', uptime: 99.97 },
    { date: '2024-01-06', uptime: 100 },
    { date: '2024-01-05', uptime: 100 },
    { date: '2024-01-04', uptime: 100 },
    { date: '2024-01-03', uptime: 98.94 },
    { date: '2024-01-02', uptime: 100 },
    { date: '2024-01-01', uptime: 100 }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'degraded':
        return <AlertTriangle className="text-yellow-600" size={20} />;
      case 'down':
        return <XCircle className="text-red-600" size={20} />;
      default:
        return <Clock className="text-gray-600" size={20} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'down':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'major':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'minor':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'maintenance':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getUptimeColor = (uptime: number) => {
    if (uptime >= 99.95) return 'bg-green-500';
    if (uptime >= 99.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <Header
          title="System Status"
          subtitle="Real-time status of FlexPesaAi services and infrastructure"
        />

        {/* Status Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              {getStatusIcon(overallStatus.status)}
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{overallStatus.message}</h2>
                <p className="text-gray-600">Last incident: {overallStatus.lastIncident}</p>
              </div>
            </div>

            <div className="text-right">
              <div className="text-3xl font-bold text-green-600">{overallStatus.uptime}</div>
              <div className="text-sm text-gray-600">30-day uptime</div>
            </div>
          </div>

          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <RefreshCw size={16} className={autoRefresh ? 'animate-spin' : ''} />
              <span>Last updated: {lastUpdated}</span>
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className="text-blue-600 hover:text-blue-800 ml-2"
              >
                {autoRefresh ? 'Disable' : 'Enable'} auto-refresh
              </button>
            </div>
            <div>All times in UTC</div>
          </div>
        </div>

        {/* Current Incidents */}
        {incidents.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Current Incidents</h2>

            {incidents.map((incident, index) => (
              <div key={index} className="border border-yellow-200 rounded-lg p-6 bg-yellow-50">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">{incident.title}</h3>
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-600">Started: {incident.startTime}</span>
                    </div>
                    <p className="text-gray-700">{incident.description}</p>
                  </div>
                  <AlertTriangle className="text-yellow-600" size={24} />
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">Updates:</h4>
                  {incident.updates.map((update, updateIndex) => (
                    <div key={updateIndex} className="flex gap-3 p-3 bg-white rounded border">
                      <div className="text-sm text-gray-600 font-medium">{update.time}</div>
                      <div className="text-sm text-gray-700">{update.message}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Service Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Service Status</h2>

          <div className="space-y-4">
            {services.map((service, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-4">
                  <service.icon className="text-gray-600" size={24} />
                  <div>
                    <h3 className="font-medium text-gray-900">{service.name}</h3>
                    <p className="text-sm text-gray-600">{service.description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{service.uptime}</div>
                    <div className="text-xs text-gray-600">30-day uptime</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{service.responseTime}</div>
                    <div className="text-xs text-gray-600">Avg response</div>
                  </div>
                  <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-medium ${getStatusColor(service.status)}`}>
                    {getStatusIcon(service.status)}
                    <span className="capitalize">{service.status}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-900">{metric.title}</h3>
                <TrendingUp className={`${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`} size={20} />
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-1">{metric.value}</div>
              <div className="flex items-center gap-2 text-sm">
                <span className={`${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.change}
                </span>
                <span className="text-gray-600">{metric.period}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Uptime History */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">14-Day Uptime History</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
              <span>14 days ago</span>
              <span>Today</span>
            </div>

            <div className="flex gap-1">
              {uptimeData.map((day, index) => (
                <div
                  key={index}
                  className={`flex-1 h-10 rounded ${getUptimeColor(day.uptime)} relative group cursor-pointer`}
                  title={`${day.date}: ${day.uptime}% uptime`}
                >
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    {day.date}: {day.uptime}%
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-6 text-sm text-gray-600 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>100% uptime</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                <span>99.5-99.95% uptime</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>&lt;99.5% uptime</span>
              </div>
            </div>
          </div>
        </div>

        {/* Past Incidents */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Incidents</h2>

          <div className="space-y-4">
            {pastIncidents.map((incident, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">{incident.title}</h3>
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                        {incident.severity.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-600">{incident.date}</span>
                      <span className="text-sm text-gray-600">Duration: {incident.duration}</span>
                    </div>
                    <p className="text-gray-700 text-sm">{incident.summary}</p>
                  </div>
                  <CheckCircle className="text-green-600" size={20} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Subscribe to Updates */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Stay Updated</h2>
            <p className="text-gray-600 mb-6">
              Subscribe to receive notifications about service status updates and planned maintenance.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                Subscribe
              </button>
            </div>

            <div className="flex items-center justify-center gap-6 mt-6 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <Calendar size={16} />
                <span>Maintenance alerts</span>
              </div>
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} />
                <span>Incident updates</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle size={16} />
                <span>Resolution notices</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
