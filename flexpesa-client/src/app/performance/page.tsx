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
      <div className="page-container">
        <div className="content-wrapper">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <LoadingSpinner size="xl" className="mx-auto mb-4" />
              <h2 className="section-title">Loading Portfolio Performance...</h2>
              <p className="section-subtitle">Calculating advanced analytics</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <Header
          title="Portfolio Performance"
          subtitle="Advanced analytics and benchmark comparisons"
        >
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </Header>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 section-spacing">
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
              className="btn-danger btn-small"
            >
              Retry
            </button>
          </div>
        )}

        {/* Portfolio Grid */}
        {portfolios.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 section-spacing">
            {portfolios.map((portfolio) => (
              <PortfolioCard
                key={portfolio.id}
                portfolio={portfolio}
                onRefresh={fetchPortfolioData}
              />
            ))}
          </div>
        ) : (
          <div className="card-large text-center section-spacing">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="card-title mb-2">No Portfolios Found</h3>
            <p className="card-subtitle mb-4">Performance data will appear here when portfolios are available</p>
          </div>
        )}

        {/* Summary Stats */}
        {summary && (
          <div className="card section-spacing">
            <h2 className="section-title subsection-spacing">Portfolio Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="metric-card bg-gradient-to-r from-green-50 to-emerald-50">
                <div className="metric-value text-green-600">
                  ${summary.total_value.toLocaleString()}
                </div>
                <div className="metric-label">Total Portfolio Value</div>
              </div>
              <div className="metric-card bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="metric-value text-blue-600">
                  {summary.total_portfolios}
                </div>
                <div className="metric-label">Active Portfolios</div>
              </div>
              <div className="metric-card bg-gradient-to-r from-purple-50 to-pink-50">
                <div className="metric-value text-purple-600">
                  {summary.average_return.toFixed(1)}%
                </div>
                <div className="metric-label">Avg Total Return</div>
              </div>
              <div className="metric-card bg-gradient-to-r from-orange-50 to-red-50">
                <div className="metric-value text-orange-600">
                  {summary.average_sharpe_ratio.toFixed(2)}
                </div>
                <div className="metric-label">Avg Sharpe Ratio</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
