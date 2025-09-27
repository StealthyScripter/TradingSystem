import React from 'react';
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { PortfolioSummary } from '@/types';
import { formatCurrency, formatPercent } from '../lib/utils';

interface PortfolioSummaryProps {
  portfolioData: PortfolioSummary;
  lastUpdated: string;
  onRefresh: () => void;
  isRefreshing: boolean;
}

const PortfolioSummaryComponent: React.FC<PortfolioSummaryProps> = ({
  portfolioData,
  lastUpdated,
  onRefresh,
  isRefreshing
}) => {
  if (!portfolioData) return null;

  const { accounts, summary, analysis } = portfolioData;

  const totalValue = summary.total_value;
  const totalAssets = summary.total_assets;
  const totalAccounts = summary.total_accounts;
  const totalPnL = summary.total_pnl;
  const totalPnLPercent = summary.total_pnl_percent;

  const totalDayChange = totalPnL * 0.1;
  const totalDayChangePercent = totalPnLPercent * 0.1;

  return (
    <div className="card">
      <div className="flex items-center justify-between subsection-spacing">
        <h2 className="section-title">Portfolio Overview</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
            <span>Updated {lastUpdated}</span>
          </div>
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
            {isRefreshing ? 'Updating...' : 'Refresh Prices'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Total Portfolio Value */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg">
          <div className="metric-value text-white">{formatCurrency(totalValue, 0)}</div>
          <div className="text-sm opacity-90 mt-1">Total Portfolio Value</div>
        </div>

        {/* Total P&L */}
        <div className={`bg-gradient-to-r ${totalPnL >= 0 ? 'from-green-500 to-green-600' : 'from-red-500 to-red-600'} text-white p-6 rounded-lg`}>
          <div className="metric-value text-white flex items-center gap-2">
            {totalPnL >= 0 ? <TrendingUp size={28} /> : <TrendingDown size={28} />}
            {formatCurrency(Math.abs(totalPnL), 0)}
          </div>
          <div className="text-sm opacity-90 mt-1">Total P&L ({formatPercent(totalPnLPercent)})</div>
        </div>

        {/* Active Accounts */}
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg">
          <div className="metric-value text-white">{totalAccounts}</div>
          <div className="text-sm opacity-90 mt-1">Active Accounts</div>
        </div>

        {/* Total Assets */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-lg">
          <div className="metric-value text-white">{totalAssets}</div>
          <div className="text-sm opacity-90 mt-1">Total Assets</div>
        </div>
      </div>

      {/* AI Analysis Insights */}
      {analysis && (
        <div className="mt-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="card-title">AI Portfolio Analysis</h3>
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
              <div className="card-subtitle">Diversity Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{analysis.risk_score.toFixed(1)}</div>
              <div className="card-subtitle">Risk Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{(analysis.confidence * 100).toFixed(0)}%</div>
              <div className="card-subtitle">Confidence</div>
            </div>
          </div>
          <div className="card-subtitle">
            <strong>Insights:</strong> {analysis.insights.join(' • ')}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioSummaryComponent;
