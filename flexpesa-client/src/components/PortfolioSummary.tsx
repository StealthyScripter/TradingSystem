import React from 'react';
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { PortfolioData } from '@/types';
import { formatCurrency, formatPercent } from '../lib/utils';

interface PortfolioSummaryProps {
  portfolioData: PortfolioData;
  lastUpdated: string;
  onRefresh: () => void;
  isRefreshing: boolean;
}

const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ 
  portfolioData, 
  lastUpdated, 
  onRefresh, 
  isRefreshing 
}) => {
  if (!portfolioData) return null;

  const { accounts, total_value, analysis } = portfolioData;
  
  // Calculate day change (mock for now - can be enhanced)
  const totalDayChange = total_value * 0.012; // Mock 1.2% daily change
  const totalDayChangePercent = 1.2;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Portfolio Overview</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
            <span>Updated {lastUpdated}</span>
          </div>
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
            {isRefreshing ? 'Updating...' : 'Refresh Prices'}
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Total Portfolio Value */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg">
          <div className="text-3xl font-bold">{formatCurrency(total_value, 0)}</div>
          <div className="text-sm opacity-90 mt-1">Total Portfolio Value</div>
        </div>
        
        {/* Day Change */}
        <div className={`bg-gradient-to-r ${totalDayChange >= 0 ? 'from-green-500 to-green-600' : 'from-red-500 to-red-600'} text-white p-6 rounded-lg`}>
          <div className="text-3xl font-bold flex items-center gap-2">
            {totalDayChange >= 0 ? <TrendingUp size={28} /> : <TrendingDown size={28} />}
            {formatCurrency(Math.abs(totalDayChange), 0)}
          </div>
          <div className="text-sm opacity-90 mt-1">Today&#39;s Change</div>
        </div>
        
        {/* Day Change Percentage */}
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg">
          <div className="text-3xl font-bold">{formatPercent(totalDayChangePercent)}</div>
          <div className="text-sm opacity-90 mt-1">Day Change %</div>
        </div>
        
        {/* Active Accounts */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-lg">
          <div className="text-3xl font-bold">{accounts.length}</div>
          <div className="text-sm opacity-90 mt-1">Active Accounts</div>
        </div>
      </div>

      {/* AI Analysis Insights */}
      {analysis && (
        <div className="mt-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800">AI Portfolio Analysis</h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              analysis.recommendation === 'HOLD' ? 'bg-blue-100 text-blue-800' :
              analysis.recommendation === 'DIVERSIFY' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {analysis.recommendation}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{analysis.diversity_score.toFixed(1)}</div>
              <div className="text-xs text-gray-600">Diversity Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{analysis.risk_score.toFixed(1)}</div>
              <div className="text-xs text-gray-600">Risk Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{(analysis.confidence * 100).toFixed(0)}%</div>
              <div className="text-xs text-gray-600">Confidence</div>
            </div>
          </div>
          <div className="text-sm text-gray-700">
            <strong>Insights:</strong> {analysis.insights.join(' • ')}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioSummary;
