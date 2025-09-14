'use client'
import Header from "@/components/Header";
import PortfolioCard from "@/components/PortfolioCard";
import { useState, useEffect } from "react";
import { RefreshCw, AlertTriangle } from "lucide-react";
import { portfolioAPI } from "@/lib/api";
import { PortfolioPerformanceSummary, PerformancePortfolio } from "@/types";
import LoadingSpinner from "@/components/LoadingSpinner";

export default function PerformancePage() {
  const [portfolios, setPortfolios] = useState<PerformancePortfolio[]>([]);
  const [summary, setSummary] = useState<PortfolioPerformanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch portfolio performance data
  const fetchPortfolioData = async () => {
    try {
      setError(null);

      // Use the correct API methods that exist in API.ts
      const [performanceResult, summaryResult] = await Promise.all([
        portfolioAPI.getPortfoliosPerformance(),
        portfolioAPI.getPortfolioPerformanceSummary()
      ]);

      setPortfolios(performanceResult);
      setSummary(summaryResult);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch portfolio data';
      setError(errorMessage);
      console.error('Failed to fetch portfolio data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Refresh data
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchPortfolioData();
  };

  // Initial load
  useEffect(() => {
    fetchPortfolioData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Header title="Portfolio Dashboard" subtitle="Real-time portfolio management with AI-powered insights"/>
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <LoadingSpinner size="xl" className="mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-700">Loading Portfolio Performance...</h2>
              <p className="text-gray-500">Calculating advanced analytics</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Header title="Portfolio Performance" subtitle="Advanced analytics and benchmark comparisons"/>

        {/* Page Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div className="flex gap-3">
              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-all duration-200 disabled:opacity-50"
              >
                <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="text-red-600" size={20} />
                <span className="font-medium text-red-800">Error</span>
              </div>
              <p className="text-red-700 text-sm mb-3">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  fetchPortfolioData();
                }}
                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
              >
                Retry
              </button>
            </div>
          )}
        </div>

        {/* Portfolio Grid */}
        {portfolios.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {portfolios.map((portfolio) => (
              <PortfolioCard
                key={portfolio.id}
                portfolio={portfolio}
                onRefresh={fetchPortfolioData}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-12 mb-8 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No Portfolios Found</h3>
            <p className="text-gray-500 mb-4">Performance data will appear here when portfolios are available</p>
          </div>
        )}

        {/* Summary Stats */}
        {summary && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Portfolio Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  ${summary.total_value.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total Portfolio Value</div>
              </div>
              <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {summary.total_portfolios}
                </div>
                <div className="text-sm text-gray-600">Active Portfolios</div>
              </div>
              <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {summary.average_return.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Avg Total Return</div>
              </div>
              <div className="text-center p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {summary.average_sharpe_ratio.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Avg Sharpe Ratio</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
