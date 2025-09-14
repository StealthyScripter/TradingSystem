'use client'

import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, ScatterChart, Scatter, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle, Brain, Target, Activity, PieChart, BarChart3, Settings, Bell, Search, Filter, Calendar, Download, Play, Pause, RotateCcw, Database, Zap, Shield, Clock, Upload, Eye, EyeOff, RefreshCw, BookOpen, Lightbulb, Users, Briefcase, CreditCard, Building2, Smartphone } from 'lucide-react';
import Header from '@/components/Header';

const ComprehensiveInvestmentPlatform = () => {
  const [activeTab, setActiveTab] = useState('portfolio');
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [realTimeData, setRealTimeData] = useState({});
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState('AAPL');

  // Mock investment accounts data
  const investmentAccounts = {
    wellsFargo: {
      name: 'Wells Fargo Intuitive',
      icon: Building2,
      balance: 45678.90,
      dayChange: 567.23,
      dayChangePercent: 1.26,
      assets: [
        { symbol: 'AAPL', shares: 50, avgCost: 155.30, currentPrice: 175.43, value: 8771.50 },
        { symbol: 'MSFT', shares: 25, avgCost: 285.20, currentPrice: 338.11, value: 8452.75 },
        { symbol: 'SPY', shares: 15, avgCost: 420.50, currentPrice: 445.67, value: 6685.05 },
      ]
    },
    stackWell: {
      name: 'Stack Well',
      icon: Target,
      balance: 23456.78,
      dayChange: -234.56,
      dayChangePercent: -0.99,
      assets: [
        { symbol: 'QQQ', shares: 30, avgCost: 350.25, currentPrice: 375.89, value: 11276.70 },
        { symbol: 'VTI', shares: 40, avgCost: 220.15, currentPrice: 245.33, value: 9813.20 },
        { symbol: 'NVDA', shares: 5, avgCost: 520.80, currentPrice: 875.28, value: 4376.40 },
      ]
    },
    cashApp: {
      name: 'Cash App Investing',
      icon: Smartphone,
      balance: 12345.67,
      dayChange: 123.45,
      dayChangePercent: 1.01,
      assets: [
        { symbol: 'TSLA', shares: 8, avgCost: 180.45, currentPrice: 248.50, value: 1988.00 },
        { symbol: 'AMD', shares: 25, avgCost: 85.60, currentPrice: 142.75, value: 3568.75 },
        { symbol: 'GOOGL', shares: 12, avgCost: 125.30, currentPrice: 139.69, value: 1676.28 },
      ]
    },
    robinhood: {
      name: 'Robinhood',
      icon: CreditCard,
      balance: 8765.43,
      dayChange: 87.65,
      dayChangePercent: 1.01,
      assets: [
        { symbol: 'BTC-USD', shares: 0.5, avgCost: 35000, currentPrice: 42500, value: 21250.00 },
        { symbol: 'ETH-USD', shares: 2.5, avgCost: 2200, currentPrice: 2650, value: 6625.00 },
      ]
    }
  };

  // Calculate total portfolio
  const totalPortfolioValue = Object.values(investmentAccounts).reduce((sum, account) => sum + account.balance, 0);
  const totalDayChange = Object.values(investmentAccounts).reduce((sum, account) => sum + account.dayChange, 0);
  const totalDayChangePercent = (totalDayChange / (totalPortfolioValue - totalDayChange)) * 100;

  // Mock data for charts and analysis
  const mockPerformanceData = [
    { date: '2024-01', portfolio: 85000, sp500: 82000, nasdaq: 83500, wellsFargo: 42000, stackWell: 21000, cashApp: 11000, robinhood: 8000 },
    { date: '2024-02', portfolio: 88000, sp500: 85000, nasdaq: 86000, wellsFargo: 43500, stackWell: 22000, cashApp: 11500, robinhood: 8200 },
    { date: '2024-03', portfolio: 92000, sp500: 87000, nasdaq: 88500, wellsFargo: 44800, stackWell: 22800, cashApp: 12000, robinhood: 8400 },
    { date: '2024-04', portfolio: 95000, sp500: 89000, nasdaq: 91000, wellsFargo: 45200, stackWell: 23200, cashApp: 12200, robinhood: 8600 },
    { date: '2024-05', portfolio: 98000, sp500: 90500, nasdaq: 93000, wellsFargo: 45500, stackWell: 23400, cashApp: 12300, robinhood: 8700 },
    { date: '2024-06', portfolio: 90246, sp500: 92000, nasdaq: 95500, wellsFargo: 45679, stackWell: 23457, cashApp: 12346, robinhood: 8765 },
  ];

  const mockSentimentData = [
    { source: 'Financial News', positive: 65, negative: 20, neutral: 15 },
    { source: 'Social Media', positive: 45, negative: 35, neutral: 20 },
    { source: 'Analyst Reports', positive: 80, negative: 10, neutral: 10 },
    { source: 'SEC Filings', positive: 55, negative: 25, neutral: 20 },
  ];

  const mockAlerts = [
    { id: 1, type: 'risk', message: 'Wells Fargo portfolio volatility exceeded 15% threshold', timestamp: '2 min ago', severity: 'high', account: 'Wells Fargo' },
    { id: 2, type: 'opportunity', message: 'Strong buy signal detected for NVDA in Stack Well account', timestamp: '5 min ago', severity: 'medium', account: 'Stack Well' },
    { id: 3, type: 'model', message: 'Sentiment analysis model drift detected', timestamp: '12 min ago', severity: 'high', account: 'All' },
    { id: 4, type: 'rebalance', message: 'Cash App portfolio rebalancing recommended', timestamp: '18 min ago', severity: 'medium', account: 'Cash App' },
  ];

  // Individual Asset Tracking Component
  const IndividualAssetTracking = () => {
    const getFilteredAccounts = () => {
      if (selectedAccount === 'all') return investmentAccounts;
      return { [selectedAccount]: investmentAccounts[selectedAccount] };
    };

    const filteredAccounts = getFilteredAccounts();

  };

  // Analysis Form Component
  const AnalysisForm = () => {
    const [formData, setFormData] = useState({
      investmentAmount: 10000,
      riskTolerance: 7,
      timeframe: 'medium',
      assets: [selectedAsset],
      account: selectedAccount
    });

    const handleAnalysis = async () => {
      setLoading(true);
      setTimeout(() => {
        setAnalysisData({
         overallScore: 78,
         recommendation: 'BUY',
          confidence: 85,
          expectedReturn: 12.5,
          riskScore: 6.2,
          timeHorizon: '12-18 months',
          alternatives: ['QQQ', 'VTI', 'GOOGL'],
          targetPrice: 185.00,
          aiInsights: [
            'Strong earnings momentum detected',
            'Positive sentiment trend across news sources',
            'Technical breakout pattern confirmed',
            'Institutional buying pressure increasing'
          ]
        });
        setLoading(false);
      }, 2000);
    };

    return (
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Brain className="text-blue-600" size={24} />
          AI Investment Analysis
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2">Investment Amount ($)</label>
            <input
              type="number"
              value={formData.investmentAmount}
              onChange={(e) => setFormData({...formData, investmentAmount: e.target.value})}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Target Account</label>
            <select
              value={formData.account}
              onChange={(e) => setFormData({...formData, account: e.target.value})}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Accounts</option>
              {Object.entries(investmentAccounts).map(([key, account]) => (
                <option key={key} value={key}>{account.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Risk Tolerance (1-10)</label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.riskTolerance}
              onChange={(e) => setFormData({...formData, riskTolerance: e.target.value})}
              className="w-full"
            />
            <div className="text-center text-sm text-gray-600 mt-1">{formData.riskTolerance}/10</div>
          </div>
        </div>

        <button
          onClick={handleAnalysis}
          disabled={loading}
          className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Analyzing...
            </>
          ) : (
            <>
              <Brain size={20} />
              Run AI Analysis
            </>
          )}
        </button>

        {analysisData && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{analysisData.overallScore}/100</div>
                <div className="text-sm text-gray-600">AI Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{analysisData.expectedReturn}%</div>
                <div className="text-sm text-gray-600">Expected Return</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{analysisData.confidence}%</div>
                <div className="text-sm text-gray-600">Confidence</div>
              </div>
            </div>

            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium mb-4 ${
              analysisData.recommendation === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {analysisData.recommendation === 'BUY' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              {analysisData.recommendation} - Target: ${analysisData.targetPrice}
            </div>

            <div>
              <h4 className="font-semibold mb-2">AI Insights:</h4>
              <ul className="space-y-1">
                {analysisData.aiInsights.map((insight, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-center gap-2">
                    <div className="w-1 h-1 bg-blue-600 rounded-full"></div>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Backtesting Dashboard
  const BacktestingDashboard = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Play className="text-blue-600" size={24} />
          Strategy Backtesting
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">+186.2%</div>
            <div className="text-sm text-gray-600">Total Return</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">2.34</div>
            <div className="text-sm text-gray-600">Sharpe Ratio</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-600">-18.5%</div>
            <div className="text-sm text-gray-600">Max Drawdown</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">87.3%</div>
            <div className="text-sm text-gray-600">Win Rate</div>
          </div>
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="portfolio" stroke="#3B82F6" strokeWidth={3} name="AI Strategy" />
              <Line type="monotone" dataKey="sp500" stroke="#10B981" strokeWidth={2} name="S&P 500" />
              <Line type="monotone" dataKey="nasdaq" stroke="#F59E0B" strokeWidth={2} name="NASDAQ" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  // Model Performance Dashboard
  const ModelPerformanceDashboard = () => {
    const mockModelPerformance = [
      { model: 'FinBERT Sentiment', accuracy: 87.3, precision: 89.1, recall: 85.7, f1: 87.4, latency: 45 },
      { model: 'RAG Document Analysis', accuracy: 82.5, precision: 84.2, recall: 80.8, f1: 82.5, latency: 120 },
      { model: 'Price Prediction LSTM', accuracy: 76.8, precision: 78.3, recall: 75.2, f1: 76.7, latency: 25 },
      { model: 'Risk Assessment', accuracy: 91.2, precision: 92.5, recall: 89.8, f1: 91.1, latency: 35 },
    ];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Brain className="text-purple-600" size={24} />
            AI Model Performance
          </h3>

          <div className="space-y-4">
            {mockModelPerformance.map((model, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-lg">{model.model}</h4>
                  <div className={`px-3 py-1 rounded-full text-sm ${
                    model.accuracy >= 85 ? 'bg-green-100 text-green-800' :
                    model.accuracy >= 80 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {model.accuracy >= 85 ? 'Excellent' : model.accuracy >= 80 ? 'Good' : 'Needs Attention'}
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="text-center">
                    <div className="text-xl font-bold text-blue-600">{model.accuracy}%</div>
                    <div className="text-xs text-gray-600">Accuracy</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-green-600">{model.precision}%</div>
                    <div className="text-xs text-gray-600">Precision</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-orange-600">{model.recall}%</div>
                    <div className="text-xs text-gray-600">Recall</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-purple-600">{model.f1}%</div>
                    <div className="text-xs text-gray-600">F1 Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-gray-600">{model.latency}ms</div>
                    <div className="text-xs text-gray-600">Latency</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Alert System Dashboard
  const AlertSystemDashboard = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Bell className="text-red-600" size={24} />
          Intelligent Alert System
        </h3>

        <div className="space-y-3">
          {mockAlerts.map((alert) => (
            <div key={alert.id} className={`border-l-4 p-4 rounded ${
              alert.severity === 'high' ? 'border-red-500 bg-red-50' :
              alert.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
              'border-blue-500 bg-blue-50'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {alert.type === 'risk' && <AlertTriangle className="text-red-600" size={20} />}
                  {alert.type === 'opportunity' && <TrendingUp className="text-green-600" size={20} />}
                  {alert.type === 'model' && <Brain className="text-purple-600" size={20} />}
                  {alert.type === 'rebalance' && <Shield className="text-orange-600" size={20} />}
                  <div>
                    <span className="font-medium">{alert.message}</span>
                    <div className="text-sm text-gray-600">Account: {alert.account}</div>
                  </div>
                </div>
                <div className="text-sm text-gray-600">{alert.timestamp}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Trading Guide Dashboard
  const TradingGuideDashboard = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <BookOpen className="text-indigo-600" size={24} />
          Trading & Market Analysis Guide
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="text-blue-600" size={20} />
                <h4 className="font-semibold">Quick Analysis Tips</h4>
              </div>
              <ul className="text-sm space-y-1 text-gray-700">
                <li>• Check sentiment across multiple sources</li>
                <li>• Compare performance against benchmarks</li>
                <li>• Monitor risk metrics regularly</li>
                <li>• Use AI insights for confirmation</li>
              </ul>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Target className="text-green-600" size={20} />
                <h4 className="font-semibold">Risk Management</h4>
              </div>
              <ul className="text-sm space-y-1 text-gray-700">
                <li>• Diversify across accounts and assets</li>
                <li>• Set stop-loss orders</li>
                <li>• Monitor portfolio correlation</li>
                <li>• Rebalance periodically</li>
              </ul>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="text-purple-600" size={20} />
                <h4 className="font-semibold">AI Features Guide</h4>
              </div>
              <ul className="text-sm space-y-1 text-gray-700">
                <li>• Sentiment analysis from news & social media</li>
                <li>• Automated risk assessment</li>
                <li>• Portfolio optimization suggestions</li>
                <li>• Real-time market anomaly detection</li>
              </ul>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Users className="text-orange-600" size={20} />
                <h4 className="font-semibold">Multi-Account Strategy</h4>
              </div>
              <ul className="text-sm space-y-1 text-gray-700">
                <li>• Use different accounts for different strategies</li>
                <li>• Consider tax implications</li>
                <li>• Monitor aggregate exposure</li>
                <li>• Leverage account-specific features</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Tab Navigation
  const TabNavigation = () => (
    <div className="bg-white rounded-lg shadow-lg p-2 mb-6">
      <div className="flex flex-wrap gap-1">
        {[
          { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
          { id: 'analysis', label: 'AI Analysis', icon: Brain },
          { id: 'backtesting', label: 'Backtesting', icon: Play },
          { id: 'models', label: 'Model Performance', icon: Database },
          { id: 'alerts', label: 'Alert System', icon: Bell },
          { id: 'guide', label: 'Trading Guide', icon: BookOpen },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <tab.icon size={18} />
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <Header title="New" subtitle="Multiple features"/>

        {/* Navigation */}
        <TabNavigation />

        {/* Portfolio Summary - Always Visible */}
        <AnalysisForm />



        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'portfolio' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-bold mb-6">Performance Chart</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mockPerformanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="portfolio" stroke="#3B82F6" strokeWidth={3} name="Total Portfolio" />
                      {selectedAccount === 'all' && (
                        <>
                          <Line type="monotone" dataKey="wellsFargo" stroke="#10B981" strokeWidth={2} name="Wells Fargo" />
                          <Line type="monotone" dataKey="stackWell" stroke="#F59E0B" strokeWidth={2} name="Stack Well" />
                          <Line type="monotone" dataKey="cashApp" stroke="#EF4444" strokeWidth={2} name="Cash App" />
                          <Line type="monotone" dataKey="robinhood" stroke="#8B5CF6" strokeWidth={2} name="Robinhood" />
                        </>
                      )}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-bold mb-6">Sentiment Analysis</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={mockSentimentData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="source" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="positive" fill="#10B981" name="Positive" />
                      <Bar dataKey="negative" fill="#EF4444" name="Negative" />
                      <Bar dataKey="neutral" fill="#6B7280" name="Neutral" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analysis' && <AnalysisForm />}
          {activeTab === 'backtesting' && <BacktestingDashboard />}
          {activeTab === 'models' && <ModelPerformanceDashboard />}
          {activeTab === 'alerts' && <AlertSystemDashboard />}
          {activeTab === 'guide' && <TradingGuideDashboard />}
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveInvestmentPlatform;