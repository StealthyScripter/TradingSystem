'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Plus, Search, TrendingUp, TrendingDown, BarChart3, Brain, RefreshCw, Eye, Edit2, Trash2, AlertTriangle, Download } from 'lucide-react';
import { portfolioAPI } from '@/lib/api';
import { PortfolioSummary, Asset, AssetCreateRequest } from '@/types';
import { formatCurrency, formatPercent, formatNumber, formatDate, getAccountIcon } from '@/lib/utils';
import Header from '@/components/Header';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

export default function AssetsPage() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [portfolioData, setPortfolioData] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);

  // Filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAccount, setFilterAccount] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState<'symbol' | 'value' | 'pnl' | 'pnl_percent'>('value');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const [formData, setFormData] = useState<AssetCreateRequest>({
    account_id: 0,
    symbol: '',
    shares: 0,
    avg_cost: 0
  });

  const fetchPortfolioData = async () => {
    try {
      setError(null);
      const token = await getToken();
      const result = await portfolioAPI.getPortfolioSummary(token || undefined);
      setPortfolioData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch portfolio data';
      setError(errorMessage);
      console.error('Failed to fetch portfolio data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleAddAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = await getToken();
      await portfolioAPI.addAsset(formData, token || undefined);
      setFormData({ account_id: 0, symbol: '', shares: 0, avg_cost: 0 });
      setShowAddForm(false);
      await fetchPortfolioData();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add asset';
      setError(errorMessage);
      console.error('Failed to add asset:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchPortfolioData();
  };

  const handleAnalyzeAsset = async (symbol: string) => {
    try {
      const token = await getToken();
      const result = await portfolioAPI.getAssetAnalysis(symbol, token || undefined);
      alert(`Analysis for ${symbol}:\n\nRecommendation: ${result.analysis.recommendation}\nRSI: ${result.analysis.technical.rsi}\nSentiment: ${result.analysis.sentiment.signal} (${result.analysis.sentiment.confidence}% confidence)`);
    } catch (err) {
      console.error('Failed to analyze asset:', err);
      alert('Failed to analyze asset. Please try again.');
    }
  };

  // Get all assets from all accounts
  const getAllAssets = (): (Asset & { accountName: string; accountType: string })[] => {
    if (!portfolioData) return [];

    return portfolioData.accounts.flatMap(account =>
      account.assets.map(asset => ({
        ...asset,
        accountName: account.name,
        accountType: account.account_type
      }))
    );
  };

  // Filter and sort assets
  const getFilteredAssets = () => {
    let assets = getAllAssets();

    // Search filter
    if (searchTerm) {
      assets = assets.filter(asset =>
        asset.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (asset.name && asset.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        asset.accountName.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Account filter
    if (filterAccount !== 'all') {
      assets = assets.filter(asset => asset.account_id.toString() === filterAccount);
    }

    // Asset type filter
    if (filterType !== 'all') {
      assets = assets.filter(asset => asset.asset_type === filterType);
    }

    // Sort
    assets.sort((a, b) => {
      let aValue, bValue;
      switch (sortBy) {
        case 'symbol':
          aValue = a.symbol;
          bValue = b.symbol;
          break;
        case 'value':
          aValue = a.value || a.market_value || 0;
          bValue = b.value || b.market_value || 0;
          break;
        case 'pnl':
          aValue = a.pnl || a.unrealized_pnl || 0;
          bValue = b.pnl || b.unrealized_pnl || 0;
          break;
        case 'pnl_percent':
          aValue = a.pnl_percent || a.unrealized_pnl_percent || 0;
          bValue = b.pnl_percent || b.unrealized_pnl_percent || 0;
          break;
        default:
          aValue = 0;
          bValue = 0;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
      return sortOrder === 'asc' ? (aValue as number) - (bValue as number) : (bValue as number) - (aValue as number);
    });

    return assets;
  };

  const calculateAssetTotals = () => {
    const assets = getAllAssets();
    return assets.reduce((totals, asset) => ({
      totalValue: totals.totalValue + (asset.value || asset.market_value || 0),
      totalPnL: totals.totalPnL + (asset.pnl || asset.unrealized_pnl || 0),
      totalAssets: totals.totalAssets + 1,
      winners: totals.winners + ((asset.pnl || asset.unrealized_pnl || 0) > 0 ? 1 : 0)
    }), { totalValue: 0, totalPnL: 0, totalAssets: 0, winners: 0 });
  };

  const getUniqueAssetTypes = () => {
    const assets = getAllAssets();
    return [...new Set(assets.map(asset => asset.asset_type).filter(Boolean))];
  };

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      fetchPortfolioData();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isSignedIn]);

  if (!isLoaded || !isSignedIn) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (loading && !portfolioData) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="xl" className="mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Loading Assets...</h2>
        </div>
      </div>
    );
  }

  const filteredAssets = getFilteredAssets();
  const totals = calculateAssetTotals();
  const assetTypes = getUniqueAssetTypes();

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-start mb-8">
          <Header
            title="Asset Portfolio"
            subtitle="Advanced asset analytics and performance tracking"
          />
          <div className="flex gap-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
            <button className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors">
              <Download size={16} />
              Export
            </button>
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Plus size={16} />
              Add Asset
            </button>
          </div>
        </div>

        {error && (
          <ErrorMessage
            message={error}
            onRetry={() => {
              setError(null);
              fetchPortfolioData();
            }}
          />
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Asset Value</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(totals.totalValue)}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className={`bg-white rounded-lg shadow-lg p-6 border-l-4 ${totals.totalPnL >= 0 ? 'border-green-500' : 'border-red-500'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Unrealized P&L</p>
                <p className={`text-2xl font-bold ${totals.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(totals.totalPnL)}
                </p>
              </div>
              <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${totals.totalPnL >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                {totals.totalPnL >= 0 ?
                  <TrendingUp className="h-6 w-6 text-green-600" /> :
                  <TrendingDown className="h-6 w-6 text-red-600" />
                }
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Holdings</p>
                <p className="text-2xl font-bold text-gray-900">{totals.totalAssets}</p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Win Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {totals.totalAssets > 0 ? Math.round((totals.winners / totals.totalAssets) * 100) : 0}%
                </p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search assets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <select
              value={filterAccount}
              onChange={(e) => setFilterAccount(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Accounts</option>
              {portfolioData?.accounts.map(account => (
                <option key={account.id} value={account.id.toString()}>{account.name}</option>
              ))}
            </select>

            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              {assetTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>

            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="value">Sort by Value</option>
                <option value="symbol">Sort by Symbol</option>
                <option value="pnl">Sort by P&L</option>
                <option value="pnl_percent">Sort by P&L %</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>

        {/* Assets Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Assets ({filteredAssets.length} of {totals.totalAssets})
            </h3>
          </div>

          {filteredAssets.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Cost</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredAssets.map((asset) => (
                    <tr key={`${asset.account_id}-${asset.id}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-sm font-bold text-blue-600">
                              {asset.symbol.slice(0, 2)}
                            </span>
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">{asset.symbol}</div>
                            {asset.name && (
                              <div className="text-sm text-gray-500">{asset.name}</div>
                            )}
                            <div className="text-xs text-gray-400">
                              {formatDate(asset.last_updated)}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getAccountIcon(asset.accountName)}</span>
                          <div>
                            <div className="font-medium text-gray-900">{asset.accountName}</div>
                            <div className="text-sm text-gray-500 capitalize">{asset.accountType}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {formatNumber(asset.shares, 3)}
                      </td>
                      <td className="px-6 py-4 text-gray-900">
                        {formatCurrency(asset.avg_cost)}
                      </td>
                      <td className="px-6 py-4 text-gray-900">
                        <div className="font-medium">{formatCurrency(asset.current_price)}</div>
                        {asset.day_change && (
                          <div className={`text-sm flex items-center gap-1 ${asset.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {asset.day_change >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                            {formatCurrency(Math.abs(asset.day_change))} ({formatPercent(Math.abs(asset.day_change_percent || 0))})
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 font-bold text-gray-900">
                        {formatCurrency(asset.value || asset.market_value)}
                      </td>
                      <td className="px-6 py-4">
                        <div className={`font-semibold ${(asset.pnl || asset.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          <div className="flex items-center gap-1">
                            {(asset.pnl || asset.unrealized_pnl || 0) >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                            {formatCurrency(Math.abs(asset.pnl || asset.unrealized_pnl || 0))}
                          </div>
                          <div className="text-sm">
                            ({formatPercent(Math.abs(asset.pnl_percent || asset.unrealized_pnl_percent || 0))})
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setSelectedAsset(asset)}
                            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Eye size={16} />
                          </button>
                          <button
                            onClick={() => handleAnalyzeAsset(asset.symbol)}
                            className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                            title="AI Analysis"
                          >
                            <Brain size={16} />
                          </button>
                          <button
                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                            title="Edit"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button
                            onClick={() => setShowDeleteConfirm(asset.id)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <BarChart3 className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {searchTerm || filterAccount !== 'all' || filterType !== 'all'
                  ? 'No assets match your filters'
                  : 'No assets found'
                }
              </h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || filterAccount !== 'all' || filterType !== 'all'
                  ? 'Try adjusting your search criteria or filters'
                  : 'Start by adding your first investment asset'
                }
              </p>
              {!(searchTerm || filterAccount !== 'all' || filterType !== 'all') && (
                <button
                  onClick={() => setShowAddForm(true)}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Add Your First Asset
                </button>
              )}
            </div>
          )}
        </div>

        {/* Add Asset Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Asset</h3>

              <form onSubmit={handleAddAsset} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account</label>
                  <select
                    required
                    value={formData.account_id}
                    onChange={(e) => setFormData({...formData, account_id: parseInt(e.target.value)})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={0}>Select Account</option>
                    {portfolioData?.accounts.map(account => (
                      <option key={account.id} value={account.id}>{account.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
                  <input
                    type="text"
                    required
                    value={formData.symbol}
                    onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., AAPL, MSFT, BTC-USD"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Shares</label>
                    <input
                      type="number"
                      step="0.001"
                      required
                      value={formData.shares || ''}
                      onChange={(e) => setFormData({...formData, shares: parseFloat(e.target.value) || 0})}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="10"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Avg Cost</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.avg_cost || ''}
                      onChange={(e) => setFormData({...formData, avg_cost: parseFloat(e.target.value) || 0})}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="150.00"
                    />
                  </div>
                </div>

                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">
                    <strong>Estimated Cost Basis:</strong> {formatCurrency((formData.shares || 0) * (formData.avg_cost || 0))}
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium flex items-center justify-center gap-2"
                  >
                    {loading ? <LoadingSpinner size="sm" /> : 'Add Asset'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddForm(false);
                      setFormData({ account_id: 0, symbol: '', shares: 0, avg_cost: 0 });
                    }}
                    className="flex-1 bg-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-400 font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Asset Details Modal */}
        {selectedAsset && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-blue-600">{selectedAsset.symbol.slice(0, 2)}</span>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{selectedAsset.symbol}</h3>
                    {selectedAsset.name && (
                      <p className="text-gray-600">{selectedAsset.name}</p>
                    )}
                    <p className="text-sm text-gray-500">
                      {selectedAsset.name} • {selectedAsset.sector || 'Unknown Sector'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedAsset(null)}
                  className="text-gray-400 hover:text-gray-600 p-2"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Current Price</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(selectedAsset.current_price)}</p>
                  {selectedAsset.day_change && (
                    <p className={`text-sm flex items-center gap-1 ${selectedAsset.day_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedAsset.day_change >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      {formatCurrency(Math.abs(selectedAsset.day_change))} ({formatPercent(Math.abs(selectedAsset.day_change_percent || 0))})
                    </p>
                  )}
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Market Value</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(selectedAsset.value || selectedAsset.market_value)}</p>
                  <p className="text-sm text-gray-600">{formatNumber(selectedAsset.shares, 3)} shares</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Average Cost</p>
                  <p className="text-xl font-bold text-gray-900">{formatCurrency(selectedAsset.avg_cost)}</p>
                  <p className="text-sm text-gray-600">Cost Basis: {formatCurrency(selectedAsset.cost_basis)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Unrealized P&L</p>
                  <p className={`text-xl font-bold ${(selectedAsset.pnl || selectedAsset.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(selectedAsset.pnl || selectedAsset.unrealized_pnl || 0)}
                  </p>
                  <p className={`text-sm ${(selectedAsset.pnl || selectedAsset.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ({formatPercent(selectedAsset.pnl_percent || selectedAsset.unrealized_pnl_percent || 0)})
                  </p>
                </div>
              </div>

              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">Asset Information</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Asset Type:</span>
                    <span className="ml-2 text-gray-900">{selectedAsset.asset_type || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Industry:</span>
                    <span className="ml-2 text-gray-900">{selectedAsset.industry || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Exchange:</span>
                    <span className="ml-2 text-gray-900">{selectedAsset.exchange || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Currency:</span>
                    <span className="ml-2 text-gray-900">{selectedAsset.currency}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleAnalyzeAsset(selectedAsset.symbol)}
                  className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <Brain size={16} />
                  AI Analysis
                </button>
                <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2">
                  <BarChart3 size={16} />
                  View Chart
                </button>
              </div>

              <div className="mt-4 text-xs text-gray-500">
                Added {formatDate(selectedAsset.created_at)} • Last updated {formatDate(selectedAsset.last_updated)}
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <div className="flex items-center gap-3 mb-4">
                <AlertTriangle className="h-8 w-8 text-red-600" />
                <h3 className="text-lg font-semibold text-gray-900">Delete Asset</h3>
              </div>

              <p className="text-gray-700 mb-6">
                Are you sure you want to delete this asset? This action cannot be undone.
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    // Handle delete logic here
                    setShowDeleteConfirm(null);
                  }}
                  className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 font-medium"
                >
                  Delete Asset
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(null)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
