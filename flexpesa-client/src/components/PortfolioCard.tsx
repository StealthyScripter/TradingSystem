import { TrendingUp, TrendingDown, Activity, Shield, DollarSign, Calendar, MoreVertical, Edit, Trash2, RefreshCw } from "lucide-react";
import { PerformancePortfolio, BenchmarkComparison } from "@/types";
import { portfolioAPI } from "@/lib/api";
import { useState } from "react";
import LoadingSpinner from "./LoadingSpinner";


interface PortfolioCardProps {
  portfolio: PerformancePortfolio;
  onRefresh?: () => void;
}

export default function PortfolioCard({ portfolio, onRefresh }: PortfolioCardProps) {
  const [showActions, setShowActions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getPerformanceColor = (value: number) => {
    if (value > 0) return "text-green-600";
    if (value < 0) return "text-red-600";
    return "text-yellow-600";
  };

  const getPerformanceBackground = (value: number) => {
    if (value > 0) return "from-green-400 to-emerald-500";
    if (value < 0) return "from-red-400 to-rose-500";
    return "from-yellow-400 to-orange-500";
  };

  const getBenchmarkStyle = (performance: number) => {
    if (performance > 0) return "bg-green-100 text-green-800 border border-green-200";
    if (performance < 0) return "bg-red-100 text-red-800 border border-red-200";
    return "bg-yellow-100 text-yellow-800 border border-yellow-200";
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? "+" : "";
    return `${sign}${value.toFixed(1)}%`;
  };

   const handleRecalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await portfolioAPI.recalculatePerformance(portfolio.id);
      if (result.success) {
        onRefresh?.();
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to recalculate performance');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${portfolio.name}"? This action cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await portfolioAPI.deletePortfolio(portfolio.id);
      if (result.success) {
        onRefresh?.();
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to delete portfolio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
      {/* Portfolio Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-900">{portfolio.name}</h3>
            <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-800 text-sm font-medium rounded-full mt-2">
              {portfolio.type}
            </span>
          </div>
          <div className="flex items-start gap-3">
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">
                {formatCurrency(portfolio.total_value)}
              </div>
              <div className="flex items-center text-sm text-gray-500 mt-1">
                <Calendar size={14} className="mr-1" />
                {portfolio.last_updated}
              </div>
            </div>

            {/* Actions Menu */}
            <div className="relative">
              <button
                onClick={() => setShowActions(!showActions)}
                className="p-1 hover:bg-gray-100 rounded-full"
                disabled={loading}
              >
                {loading ? <LoadingSpinner size="sm" /> : <MoreVertical size={16} />}
              </button>

              {showActions && (
                <div className="absolute right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                  <button
                    onClick={() => {
                      handleRecalculate();
                      setShowActions(false);
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <RefreshCw size={14} />
                    Recalculate Performance
                  </button>
                  <button
                    onClick={() => {
                      // TODO: Implement edit functionality
                      setShowActions(false);
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Edit size={14} />
                    Edit Portfolio
                  </button>
                  <button
                    onClick={() => {
                      handleDelete();
                      setShowActions(false);
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 size={14} />
                    Delete Portfolio
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Key Metrics Grid */}
        <div className="p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="mr-2" size={20} />
            Performance Metrics
          </h4>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className={`bg-gradient-to-r ${getPerformanceBackground(portfolio.total_return)} text-white p-4 rounded-lg`}>
              <div className="text-2xl font-bold">{formatPercentage(portfolio.total_return)}</div>
              <div className="text-sm opacity-90">Total Return</div>
            </div>

            <div className={`bg-gradient-to-r ${getPerformanceBackground(portfolio.annualized_return)} text-white p-4 rounded-lg`}>
              <div className="text-2xl font-bold">{formatPercentage(portfolio.annualized_return)}</div>
              <div className="text-sm opacity-90">Annualized Return</div>
            </div>

            <div className="bg-gradient-to-r from-blue-400 to-indigo-500 text-white p-4 rounded-lg">
              <div className="text-2xl font-bold">{portfolio.sharpe_ratio.toFixed(2)}</div>
              <div className="text-sm opacity-90">Sharpe Ratio</div>
            </div>

            <div className="bg-gradient-to-r from-purple-400 to-pink-500 text-white p-4 rounded-lg">
              <div className="text-2xl font-bold">{formatPercentage(portfolio.max_drawdown)}</div>
              <div className="text-sm opacity-90">Max Drawdown</div>
            </div>
          </div>

          {/* Benchmark Comparison */}
          <div className="mb-6">
            <h5 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <Activity className="mr-2" size={18} />
              Benchmark Comparison
            </h5>
            <div className="space-y-2">
              {portfolio.benchmark_comparisons.map((benchmark: BenchmarkComparison, index: number) => (
                <div key={index} className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-700">{benchmark.name}</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getBenchmarkStyle(benchmark.performance)}`}>
                    {benchmark.performance >= 0 ? (
                      <span className="flex items-center">
                        <TrendingUp size={14} className="mr-1" />
                        +{benchmark.performance.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="flex items-center">
                        <TrendingDown size={14} className="mr-1" />
                        {benchmark.performance.toFixed(1)}%
                      </span>
                    )}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Metrics */}
          <div>
            <h5 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <Shield className="mr-2" size={18} />
              Risk Analytics
            </h5>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-indigo-500">
                <div className="font-semibold text-gray-900">{portfolio.risk_metrics.beta.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Beta (vs S&P 500)</div>
              </div>

              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-purple-500">
                <div className="font-semibold text-gray-900">{portfolio.risk_metrics.volatility.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Volatility</div>
              </div>

              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-green-500">
                <div className="font-semibold text-gray-900">+{portfolio.risk_metrics.alpha.toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Jensen&#39;s Alpha</div>
              </div>

              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-orange-500">
                <div className="font-semibold text-gray-900">{portfolio.risk_metrics.expense_ratio.toFixed(2)}%</div>
                <div className="text-sm text-gray-600">Expense Ratio</div>
              </div>

              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-teal-500">
                <div className="font-semibold text-gray-900">{portfolio.risk_metrics.sortino_ratio.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Sortino Ratio</div>
              </div>

              <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-red-500">
                <div className="font-semibold text-gray-900 flex items-center">
                  <DollarSign size={16} className="mr-1" />
                  {portfolio.risk_metrics.value_at_risk.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">VaR (5%, 1 month)</div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
            <button
              onClick={() => {
                // TODO: Navigate to portfolio detail page
                console.log('Navigate to portfolio details for:', portfolio.id);
              }}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg font-medium transition-colors duration-200"
            >
              View Details
            </button>
            <button
              onClick={() => {
                // TODO: Open holdings modal or navigate to holdings page
                console.log('View holdings for:', portfolio.id);
              }}
              className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium transition-colors duration-200"
            >
              View Holdings
            </button>
          </div>
        </div>

        {/* Click outside to close actions menu */}
        {showActions && (
          <div
            className="fixed inset-0 z-0"
            onClick={() => setShowActions(false)}
          />
        )}
      </div>
    );
  }

  // return (
  //   <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
  //     {/* Portfolio Header */}
  //     <div className="p-6 border-b border-gray-100">
  //       <div className="flex justify-between items-start mb-4">
  //         <div>
  //           <h3 className="text-xl font-bold text-gray-900">{portfolio.name}</h3>
  //           <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-800 text-sm font-medium rounded-full mt-2">
  //             {portfolio.type}
  //           </span>
  //         </div>
  //         <div className="text-right">
  //           <div className="text-2xl font-bold text-gray-900">
  //             {formatCurrency(portfolio.totalValue)}
  //           </div>
  //           <div className="flex items-center text-sm text-gray-500 mt-1">
  //             <Calendar size={14} className="mr-1" />
  //             {portfolio.lastUpdated}
  //           </div>
  //         </div>
  //       </div>
  //     </div>

  //     {/* Key Metrics Grid */}
  //     <div className="p-6">
  //       <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
  //         <TrendingUp className="mr-2" size={20} />
  //         Performance Metrics
  //       </h4>

  //       <div className="grid grid-cols-2 gap-4 mb-6">
  //         <div className={`bg-gradient-to-r ${getPerformanceBackground(portfolio.totalReturn)} text-white p-4 rounded-lg`}>
  //           <div className="text-2xl font-bold">{formatPercentage(portfolio.totalReturn)}</div>
  //           <div className="text-sm opacity-90">Total Return (YTD)</div>
  //         </div>

  //         <div className={`bg-gradient-to-r ${getPerformanceBackground(portfolio.annualizedReturn)} text-white p-4 rounded-lg`}>
  //           <div className="text-2xl font-bold">{formatPercentage(portfolio.annualizedReturn)}</div>
  //           <div className="text-sm opacity-90">Annualized Return</div>
  //         </div>

  //         <div className="bg-gradient-to-r from-blue-400 to-indigo-500 text-white p-4 rounded-lg">
  //           <div className="text-2xl font-bold">{portfolio.sharpeRatio.toFixed(2)}</div>
  //           <div className="text-sm opacity-90">Sharpe Ratio</div>
  //         </div>

  //         <div className="bg-gradient-to-r from-purple-400 to-pink-500 text-white p-4 rounded-lg">
  //           <div className="text-2xl font-bold">{formatPercentage(portfolio.maxDrawdown)}</div>
  //           <div className="text-sm opacity-90">Max Drawdown</div>
  //         </div>
  //       </div>

  //       {/* Benchmark Comparison */}
  //       <div className="mb-6">
  //         <h5 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
  //           <Activity className="mr-2" size={18} />
  //           Benchmark Comparison
  //         </h5>
  //         <div className="space-y-2">
  //           {portfolio.benchmarkComparisons.map((benchmark: BenchmarkComparison, index: number) => (
  //             <div key={index} className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
  //               <span className="font-medium text-gray-700">{benchmark.name}</span>
  //               <span className={`px-3 py-1 rounded-full text-sm font-medium ${getBenchmarkStyle(benchmark.performance)}`}>
  //                 {benchmark.performance >= 0 ? (
  //                   <span className="flex items-center">
  //                     <TrendingUp size={14} className="mr-1" />
  //                     +{benchmark.performance.toFixed(1)}%
  //                   </span>
  //                 ) : (
  //                   <span className="flex items-center">
  //                     <TrendingDown size={14} className="mr-1" />
  //                     {benchmark.performance.toFixed(1)}%
  //                   </span>
  //                 )}
  //               </span>
  //             </div>
  //           ))}
  //         </div>
  //       </div>

  //       {/* Risk Metrics */}
  //       <div>
  //         <h5 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
  //           <Shield className="mr-2" size={18} />
  //           Risk Analytics
  //         </h5>
  //         <div className="grid grid-cols-2 gap-3">
  //           <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-indigo-500">
  //             <div className="font-semibold text-gray-900">{portfolio.riskMetrics.beta.toFixed(2)}</div>
  //             <div className="text-sm text-gray-600">Beta (vs S&P 500)</div>
  //           </div>

  //           <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-purple-500">
  //             <div className="font-semibold text-gray-900">{portfolio.riskMetrics.volatility.toFixed(1)}%</div>
  //             <div className="text-sm text-gray-600">Volatility</div>
  //           </div>

  //           <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-green-500">
  //             <div className="font-semibold text-gray-900">+{portfolio.riskMetrics.alpha.toFixed(1)}%</div>
  //             <div className="text-sm text-gray-600">Jensen&#39;s Alpha</div>
  //           </div>

  //           <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-orange-500">
  //             <div className="font-semibold text-gray-900">{portfolio.riskMetrics.expenseRatio.toFixed(2)}%</div>
  //             <div className="text-sm text-gray-600">Expense Ratio</div>
  //           </div>

  //           <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-teal-500">
  //             <div className="font-semibold text-gray-900">{portfolio.riskMetrics.sortinoRatio.toFixed(2)}</div>
  //             <div className="text-sm text-gray-600">Sortino Ratio</div>
  //           </div>

  //           <div className="bg-gray-50 p-3 rounded-lg border-l-4 border-red-500">
  //             <div className="font-semibold text-gray-900 flex items-center">
  //               <DollarSign size={16} className="mr-1" />
  //               {portfolio.riskMetrics.valueAtRisk.toLocaleString()}
  //             </div>
  //             <div className="text-sm text-gray-600">VaR (5%, 1 month)</div>
  //           </div>
  //         </div>
  //       </div>

  //       {/* Action Buttons */}
  //       <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
  //         <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg font-medium transition-colors duration-200">
  //           View Details
  //         </button>
  //         <button className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium transition-colors duration-200">
  //           Edit Portfolio
  //         </button>
  //       </div>
  //     </div>
  //   </div>
  // );

