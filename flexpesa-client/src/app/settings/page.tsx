'use client'
import React, { useState } from 'react';
import {
  User, Shield, Bell, Database, Palette, Globe, Key, Trash2, Save, Eye, EyeOff, Download, RefreshCw
} from 'lucide-react';

import Header from '@/components/Header';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [profileData, setProfileData] = useState({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    timezone: 'America/New_York',
    language: 'en'
  });

  const [securityData, setSecurityData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    twoFactorEnabled: true,
    sessionTimeout: '30'
  });

  const [notificationData, setNotificationData] = useState({
    emailAlerts: true,
    pushNotifications: true,
    portfolioUpdates: true,
    marketNews: false,
    weeklyReports: true
  });

  const [privacyData, setPrivacyData] = useState({
    dataSharing: false,
    analytics: true,
    marketing: false,
    thirdParty: false
  });

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Database },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'advanced', label: 'Advanced', icon: Globe }
  ];

  const handleSave = async (section: string) => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      alert(`${section} settings saved successfully!`);
    }, 1000);
  };

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="card-title subsection-spacing">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="form-label">First Name</label>
            <input
              type="text"
              value={profileData.firstName}
              onChange={(e) => setProfileData({...profileData, firstName: e.target.value})}
              className="form-input"
            />
          </div>
          <div>
            <label className="form-label">Last Name</label>
            <input
              type="text"
              value={profileData.lastName}
              onChange={(e) => setProfileData({...profileData, lastName: e.target.value})}
              className="form-input"
            />
          </div>
          <div>
            <label className="form-label">Email Address</label>
            <input
              type="email"
              value={profileData.email}
              onChange={(e) => setProfileData({...profileData, email: e.target.value})}
              className="form-input"
            />
          </div>
          <div>
            <label className="form-label">Phone Number</label>
            <input
              type="tel"
              value={profileData.phone}
              onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
              className="form-input"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="card-title subsection-spacing">Preferences</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="form-label">Timezone</label>
            <select
              value={profileData.timezone}
              onChange={(e) => setProfileData({...profileData, timezone: e.target.value})}
              className="form-input"
            >
              <option value="America/New_York">Eastern Time (ET)</option>
              <option value="America/Chicago">Central Time (CT)</option>
              <option value="America/Denver">Mountain Time (MT)</option>
              <option value="America/Los_Angeles">Pacific Time (PT)</option>
            </select>
          </div>
          <div>
            <label className="form-label">Language</label>
            <select
              value={profileData.language}
              onChange={(e) => setProfileData({...profileData, language: e.target.value})}
              className="form-input"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
        </div>
      </div>

      <button
        onClick={() => handleSave('Profile')}
        disabled={isLoading}
        className="btn-primary flex items-center gap-2"
      >
        <Save size={16} />
        {isLoading ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="card-title subsection-spacing">Change Password</h3>
        <div className="space-y-4">
          <div>
            <label className="form-label">Current Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={securityData.currentPassword}
                onChange={(e) => setSecurityData({...securityData, currentPassword: e.target.value})}
                className="form-input pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div>
            <label className="form-label">New Password</label>
            <input
              type="password"
              value={securityData.newPassword}
              onChange={(e) => setSecurityData({...securityData, newPassword: e.target.value})}
              className="form-input"
            />
          </div>
          <div>
            <label className="form-label">Confirm New Password</label>
            <input
              type="password"
              value={securityData.confirmPassword}
              onChange={(e) => setSecurityData({...securityData, confirmPassword: e.target.value})}
              className="form-input"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="card-title subsection-spacing">Two-Factor Authentication</h3>
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <div className="font-medium text-gray-900">Enable 2FA</div>
            <div className="card-subtitle">Add an extra layer of security to your account</div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={securityData.twoFactorEnabled}
              onChange={(e) => setSecurityData({...securityData, twoFactorEnabled: e.target.checked})}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>

      <div>
        <h3 className="card-title subsection-spacing">Session Settings</h3>
        <div>
          <label className="form-label">Session Timeout (minutes)</label>
          <select
            value={securityData.sessionTimeout}
            onChange={(e) => setSecurityData({...securityData, sessionTimeout: e.target.value})}
            className="form-input"
          >
            <option value="15">15 minutes</option>
            <option value="30">30 minutes</option>
            <option value="60">1 hour</option>
            <option value="120">2 hours</option>
            <option value="0">Never</option>
          </select>
        </div>
      </div>

      <button
        onClick={() => handleSave('Security')}
        disabled={isLoading}
        className="btn-primary flex items-center gap-2"
      >
        <Shield size={16} />
        {isLoading ? 'Saving...' : 'Update Security Settings'}
      </button>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="card-title subsection-spacing">Email Notifications</h3>
        <div className="space-y-4">
          {[
            { key: 'emailAlerts', label: 'Portfolio Alerts', desc: 'Get notified about important portfolio changes' },
            { key: 'portfolioUpdates', label: 'Portfolio Updates', desc: 'Daily portfolio performance summaries' },
            { key: 'marketNews', label: 'Market News', desc: 'Relevant market news and insights' },
            { key: 'weeklyReports', label: 'Weekly Reports', desc: 'Comprehensive weekly portfolio reports' }
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">{item.label}</div>
                <div className="card-subtitle">{item.desc}</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationData[item.key as keyof typeof notificationData]}
                  onChange={(e) => setNotificationData({...notificationData, [item.key]: e.target.checked})}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="card-title subsection-spacing">Push Notifications</h3>
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <div className="font-medium text-gray-900">Mobile Push Notifications</div>
            <div className="card-subtitle">Receive notifications on your mobile device</div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={notificationData.pushNotifications}
              onChange={(e) => setNotificationData({...notificationData, pushNotifications: e.target.checked})}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>

      <button
        onClick={() => handleSave('Notifications')}
        disabled={isLoading}
        className="btn-primary flex items-center gap-2"
      >
        <Bell size={16} />
        {isLoading ? 'Saving...' : 'Save Notification Settings'}
      </button>
    </div>
  );

  const renderPrivacySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="card-title subsection-spacing">Data Privacy</h3>
        <div className="space-y-4">
          {[
            { key: 'dataSharing', label: 'Data Sharing', desc: 'Allow sharing anonymized data for research' },
            { key: 'analytics', label: 'Analytics', desc: 'Help improve our service with usage analytics' },
            { key: 'marketing', label: 'Marketing Communications', desc: 'Receive promotional emails and offers' },
            { key: 'thirdParty', label: 'Third-party Integrations', desc: 'Allow third-party service integrations' }
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">{item.label}</div>
                <div className="card-subtitle">{item.desc}</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacyData[item.key as keyof typeof privacyData]}
                  onChange={(e) => setPrivacyData({...privacyData, [item.key]: e.target.checked})}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="font-semibold text-yellow-900 mb-2">Data Export & Deletion</h4>
        <p className="card-subtitle text-yellow-700 mb-4">
          You have the right to export or delete your personal data at any time.
        </p>
        <div className="flex gap-3">
          <button className="btn-secondary btn-small">Export My Data</button>
          <button className="btn-danger btn-small flex items-center gap-2">
            <Trash2 size={14} />
            Delete Account
          </button>
        </div>
      </div>

      <button
        onClick={() => handleSave('Privacy')}
        disabled={isLoading}
        className="btn-primary flex items-center gap-2"
      >
        <Database size={16} />
        {isLoading ? 'Saving...' : 'Save Privacy Settings'}
      </button>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="card-title subsection-spacing">Theme Preferences</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500">
            <div className="w-full h-20 bg-white border rounded mb-3"></div>
            <div className="font-medium text-center">Light</div>
          </div>
          <div className="border border-blue-500 rounded-lg p-4 cursor-pointer bg-blue-50">
            <div className="w-full h-20 bg-gray-800 rounded mb-3"></div>
            <div className="font-medium text-center text-blue-700">Dark</div>
          </div>
          <div className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500">
            <div className="w-full h-20 bg-gradient-to-br from-white to-gray-800 rounded mb-3"></div>
            <div className="font-medium text-center">Auto</div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="card-title subsection-spacing">Display Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="form-label">Currency Display</label>
            <select className="form-input">
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="CAD">CAD (C$)</option>
            </select>
          </div>
          <div>
            <label className="form-label">Number Format</label>
            <select className="form-input">
              <option value="US">1,234.56 (US)</option>
              <option value="EU">1.234,56 (EU)</option>
              <option value="IN">1,23,456.78 (Indian)</option>
            </select>
          </div>
        </div>
      </div>

      <button
        onClick={() => handleSave('Appearance')}
        disabled={isLoading}
        className="btn-primary flex items-center gap-2"
      >
        <Palette size={16} />
        {isLoading ? 'Saving...' : 'Save Appearance Settings'}
      </button>
    </div>
  );

  const renderAdvancedSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="card-title subsection-spacing">API Access</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="font-medium text-gray-900">API Key</div>
              <div className="card-subtitle">Use this key to access the FlexPesaAi API</div>
            </div>
            <button className="btn-secondary btn-small flex items-center gap-2">
              <Key size={14} />
              Generate New Key
            </button>
          </div>
          <div className="font-mono text-sm bg-white p-3 rounded border">
            sk-fp-1234567890abcdef...
          </div>
        </div>
      </div>

      <div>
        <h3 className="card-title subsection-spacing">Data Management</h3>
        <div className="space-y-3">
          <button className="btn-secondary flex items-center gap-2">
            <Database size={16} />
            Clear Cache
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download size={16} />
            Export Portfolio Data
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <RefreshCw size={16} />
            Sync All Accounts
          </button>
        </div>
      </div>

      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h4 className="font-semibold text-red-900 mb-2">Danger Zone</h4>
        <p className="card-subtitle text-red-700 mb-4">
          These actions cannot be undone. Please be careful.
        </p>
        <div className="space-y-2">
          <button className="btn-danger btn-small flex items-center gap-2">
            <Trash2 size={14} />
            Delete All Portfolio Data
          </button>
          <button className="btn-danger btn-small flex items-center gap-2">
            <Trash2 size={14} />
            Delete Account Permanently
          </button>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return renderProfileSettings();
      case 'security':
        return renderSecuritySettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'privacy':
        return renderPrivacySettings();
      case 'appearance':
        return renderAppearanceSettings();
      case 'advanced':
        return renderAdvancedSettings();
      default:
        return renderProfileSettings();
    }
  };

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <Header
          title="Settings"
          subtitle="Manage your account preferences and configuration"
        />

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Settings Navigation */}
          <div className="lg:col-span-1">
            <div className="card-compact">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <tab.icon size={18} />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-3">
            <div className="card-large">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
