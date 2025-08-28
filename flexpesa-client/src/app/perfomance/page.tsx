'use client'
import Header from "@/components/Header";
import PortfolioCard from "@/components/PortfolioCard";
import { useState, useEffect } from "react";
import { Plus, RefreshCw, AlertTriangle } from "lucide-react";
import { portfolioAPI } from "@/lib/api";
import { PortfolioCreate, HoldingCreate, PortfolioPerformanceSummary, PerformancePortfolio } from "@/types";
import LoadingSpinner  from "@/components/LoadingSpinner";

export default function PerformancePage() {
  const [portfolios, setPortfolios] = useState<PerformancePortfolio[]>([]);
  const [summary, setSummary] = useState<PortfolioPerformanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [creating, setCreating] = useState(false);

  // Form state for creating new portfolios
  const [portfolioForm, setPortfolioForm] = useState({
    name: '',
    type: 'Growth',
    initial_investment: '',
    expense_ratio: '0.5'
  });

  const [holdings, setHoldings] = useState<HoldingCreate[]>([
    { symbol: '', quantity: 0, purchase_price: 0, purchase_date: new Date().toISOString().split('T')[0] }
  ]);

  // Fetch portfolio performance data
  const fetchPortfolioData = async () => {
    try {
      setError(null);

      const [performanceResult, summaryResult] = await Promise.all([
        portfolioAPI.getAllPortfolioPerformance(),
        portfolioAPI.getPortfolioPerformanceSummary()
      ]);

      if (performanceResult.success) {
        setPortfolios(performanceResult.data);
      } else {
        setError(performanceResult.error);
      }

      if (summaryResult.success) {
        setSummary(summaryResult.data);
      }

    } catch (err) {
      setError('Failed to fetch portfolio data');
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

  // Handle adding a new portfolio
  const handleAddPortfolio = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError(null);

    try {
      const portfolioData: PortfolioCreate = {
        name: portfolioForm.name,
        type: portfolioForm.type,
        initial_investment: parseFloat(portfolioForm.initial_investment),
        expense_ratio: parseFloat(portfolioForm.expense_ratio),
        holdings: holdings.filter(h => h.symbol && h.quantity > 0 && h.purchase_price > 0)
      };

      const result = await portfolioAPI.createPortfolioWithPerformance(portfolioData);

      if (result.success) {
        // Refresh the portfolio list
        await fetchPortfolioData();

        // Reset form
        setPortfolioForm({
          name: '',
          type: 'Growth',
          initial_investment: '',
          expense_ratio: '0.5'
        });
        setHoldings([
          { symbol: '', quantity: 0, purchase_price: 0, purchase_date: new Date().toISOString().split('T')[0] }
        ]);
        setShowAddForm(false);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to create portfolio');
    } finally {
      setCreating(false);
    }
  };

  // Add holding to form
  const addHolding = () => {
    setHoldings([...holdings, {
      symbol: '',
      quantity: 0,
      purchase_price: 0,
      purchase_date: new Date().toISOString().split('T')[0]
    }]);
  };

  // Remove holding from form
  const removeHolding = (index: number) => {
    if (holdings.length > 1) {
      setHoldings(holdings.filter((_, i) => i !== index));
    }
  };

  // Update holding in form
  const updateHolding = (index: number, field: keyof HoldingCreate, value: string | number) => {
    const updated = [...holdings];
    updated[index] = { ...updated[index], [field]: value };
    setHoldings(updated);
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

              {/* Add Portfolio Button */}
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <Plus size={20} />
                Add Portfolio
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

        {/* Add Portfolio Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h3 className="text-xl font-bold mb-4">Create New Portfolio</h3>
            <form onSubmit={handleAddPortfolio} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Portfolio Name</label>
                  <input
                    type="text"
                    required
                    value={portfolioForm.name}
                    onChange={(e) => setPortfolioForm({...portfolioForm, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="My Growth Portfolio"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  <select
                    value={portfolioForm.type}
                    onChange={(e) => setPortfolioForm({...portfolioForm, type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Growth">Growth</option>
                    <option value="Value">Value</option>
                    <option value="Balanced">Balanced</option>
                    <option value="Conservative">Conservative</option>
                    <option value="Aggressive">Aggressive</option>
                    <option value="Income">Income</option>
                    <option value="Index">Index</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Initial Investment</label>
                  <input
                    type="number"
                    required
                    min="0"
                    step="0.01"
                    value={portfolioForm.initial_investment}
                    onChange={(e) => setPortfolioForm({...portfolioForm, initial_investment: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="10000.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Expense Ratio (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="5"
                    step="0.01"
                    value={portfolioForm.expense_ratio}
                    onChange={(e) => setPortfolioForm({...portfolioForm, expense_ratio: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="0.50"
                  />
                </div>
              </div>

              {/* Holdings */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold">Initial Holdings</h4>
                  <button
                    type="button"
                    onClick={addHolding}
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus size={16} />
                    Add Holding
                  </button>
                </div>

                <div className="space-y-3">
                  {holdings.map((holding, index) => (
                    <div key={index} className="grid grid-cols-1 md:grid-cols-5 gap-3 p-3 bg-gray-50 rounded-lg">
                      <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">Symbol</label>
                        <input
                          type="text"
                          value={holding.symbol}
                          onChange={(e) => updateHolding(index, 'symbol', e.target.value.toUpperCase())}
                          className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                          placeholder="AAPL"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">Quantity</label>
                        <input
                          type="number"
                          min="0"
                          step="0.001"
                          value={holding.quantity || ''}
                          onChange={(e) => updateHolding(index, 'quantity', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                          placeholder="100"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">Purchase Price</label>
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          value={holding.purchase_price || ''}
                          onChange={(e) => updateHolding(index, 'purchase_price', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                          placeholder="150.00"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-600 mb-1">Purchase Date</label>
                        <input
                          type="date"
                          value={holding.purchase_date}
                          onChange={(e) => updateHolding(index, 'purchase_date', e.target.value)}
                          className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                        />
                      </div>
                      <div className="flex items-end">
                        {holdings.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeHolding(index)}
                            className="text-red-600 hover:text-red-700 px-2 py-1"
                          >
                            Remove
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Form Actions */}
              <div className="flex gap-3 pt-4 border-t">
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
                >
                  {creating && <LoadingSpinner size="sm" />}
                  {creating ? 'Creating...' : 'Create Portfolio'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

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
            <p className="text-gray-500 mb-4">Create your first portfolio to start tracking performance metrics</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
            >
              Create Portfolio
            </button>
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
