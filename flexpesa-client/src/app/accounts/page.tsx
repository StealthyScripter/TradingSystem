'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Plus, Building2, TrendingUp, TrendingDown, BarChart3, DollarSign, RefreshCw, Edit2, Trash2, Eye, AlertTriangle } from 'lucide-react';
import { portfolioAPI } from '@/lib/api';
import { PortfolioSummary, AccountCreateRequest, PortfolioAccount, Asset } from '@/types';
import { formatCurrency, formatPercent, formatDate, getAccountIcon } from '@/lib/utils';
import Header from '@/components/Header';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

export default function AccountsPage() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [portfolioData, setPortfolioData] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<PortfolioAccount | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);

  const [formData, setFormData] = useState<AccountCreateRequest>({
    name: '',
    account_type: 'brokerage',
    description: '',
    currency: 'USD'
  });

  const fetchAccounts = React.useCallback(async () => {
    try {
      setError(null);
      const token = await getToken();
      const result = await portfolioAPI.getPortfolioSummary(token || undefined);
      setPortfolioData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch accounts';
      setError(errorMessage);
      console.error('Failed to fetch accounts:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [getToken]);

  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = await getToken();
      await portfolioAPI.createAccount(formData, token || undefined);
      setFormData({ name: '', account_type: 'brokerage', description: '', currency: 'USD' });
      setShowAddForm(false);
      await fetchAccounts();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add account';
      setError(errorMessage);
      console.error('Failed to add account:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAccounts();
  };

  const calculateTotals = () => {
    if (!portfolioData?.accounts) return { totalValue: 0, totalPnL: 0, totalAssets: 0, totalAccounts: 0 };

    return portfolioData.accounts.reduce((totals, account) => ({
      totalValue: totals.totalValue + account.balance,
      totalPnL: totals.totalPnL + (account.pnl || 0),
      totalAssets: totals.totalAssets + (account.assets?.length || 0),
      totalAccounts: totals.totalAccounts + 1
    }), { totalValue: 0, totalPnL: 0, totalAssets: 0, totalAccounts: 0 });
  };

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      fetchAccounts();
    }
  }, [isLoaded, isSignedIn, fetchAccounts]);

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
          <h2 className="text-xl font-semibold text-gray-700">Loading Accounts...</h2>
        </div>
      </div>
    );
  }

  const totals = calculateTotals();
  const accounts = portfolioData?.accounts || [];

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-start mb-8">
          <Header
            title="Account Management"
            subtitle="Manage your investment accounts and track performance"
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
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Plus size={16} />
              Add Account
            </button>
          </div>
        </div>

        {error && (
          <ErrorMessage
            message={error}
            onRetry={() => {
              setError(null);
              fetchAccounts();
            }}
          />
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Value</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(totals.totalValue)}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className={`bg-white rounded-lg shadow-lg p-6 border-l-4 ${totals.totalPnL >= 0 ? 'border-green-500' : 'border-red-500'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total P&L</p>
                <p className={`text-2xl font-bold ${totals.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(totals.totalPnL)}
                </p>
              </div>
              <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${totals.totalPnL >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                {totals.totalPnL >= 0 ?
                  <TrendingUp className={`h-6 w-6 text-green-600`} /> :
                  <TrendingDown className={`h-6 w-6 text-red-600`} />
                }
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Accounts</p>
                <p className="text-2xl font-bold text-gray-900">{totals.totalAccounts}</p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Assets</p>
                <p className="text-2xl font-bold text-gray-900">{totals.totalAssets}</p>
              </div>
              <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Accounts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {accounts.map((account: PortfolioAccount) => (
            <div key={account.id} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">
                    {getAccountIcon(account.name)}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{account.name}</h3>
                    <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full capitalize">
                      {account.account_type}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedAccount(account)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="View Details"
                  >
                    <Eye size={16} />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors" title="Edit">
                    <Edit2 size={16} />
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(account.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Balance</span>
                  <span className="text-lg font-bold text-gray-900">{formatCurrency(account.balance)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cost Basis</span>
                  <span className="text-sm font-medium text-gray-700">{formatCurrency(account.cost_basis || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">P&L</span>
                  <div className="text-right">
                    <div className={`text-sm font-medium ${(account.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(account.pnl || 0)}
                    </div>
                    <div className={`text-xs ${(account.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ({formatPercent(account.pnl_percent || 0)})
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center pt-2 border-t">
                  <span className="text-sm text-gray-600">Assets</span>
                  <span className="text-sm font-medium text-gray-900">{account.assets?.length || 0} holdings</span>
                </div>
              </div>

              {account.description && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">{account.description}</p>
                </div>
              )}

              <div className="text-xs text-gray-500">
                Created {formatDate(account.created_at)}
              </div>
            </div>
          ))}
        </div>

        {accounts.length === 0 && !loading && (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <Building2 className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Accounts Yet</h3>
            <p className="text-gray-600 mb-6">
              Get started by adding your first investment account to track your portfolio.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Add Your First Account
            </button>
          </div>
        )}

        {/* Add Account Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Account</h3>

              <form onSubmit={handleAddAccount} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Name</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Wells Fargo Brokerage"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Type</label>
                  <select
                    value={formData.account_type}
                    onChange={(e) => setFormData({...formData, account_type: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="brokerage">Brokerage</option>
                    <option value="retirement">Retirement (401k/IRA)</option>
                    <option value="crypto">Cryptocurrency</option>
                    <option value="trading">Day Trading</option>
                    <option value="savings">High-Yield Savings</option>
                    <option value="checking">Checking</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
                  <select
                    value={formData.currency}
                    onChange={(e) => setFormData({...formData, currency: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="GBP">GBP - British Pound</option>
                    <option value="CAD">CAD - Canadian Dollar</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                  <textarea
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Brief description of this account..."
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium flex items-center justify-center gap-2"
                  >
                    {loading ? <LoadingSpinner size="sm" /> : 'Add Account'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddForm(false);
                      setFormData({ name: '', account_type: 'brokerage', description: '', currency: 'USD' });
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

        {/* Account Details Modal */}
        {selectedAccount && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">{getAccountIcon(selectedAccount.name)}</div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{selectedAccount.name}</h3>
                    <span className="text-sm text-gray-600 capitalize">{selectedAccount.account_type}</span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedAccount(null)}
                  className="text-gray-400 hover:text-gray-600 p-2"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Current Balance</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(selectedAccount.balance)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Total P&L</p>
                  <p className={`text-2xl font-bold ${(selectedAccount.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(selectedAccount.pnl || 0)}
                  </p>
                  <p className={`text-sm ${(selectedAccount.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ({formatPercent(selectedAccount.pnl_percent || 0)})
                  </p>
                </div>
              </div>

              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">Holdings ({selectedAccount.assets?.length || 0})</h4>
                {selectedAccount.assets && selectedAccount.assets.length > 0 ? (
                  <div className="space-y-2">
                    {selectedAccount.assets.slice(0, 5).map((asset: Asset) => (
                      <div key={asset.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-blue-600">{asset.symbol.slice(0, 2)}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-900">{asset.symbol}</span>
                            <div className="text-xs text-gray-600">{asset.shares} shares</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{formatCurrency(asset.value || asset.market_value)}</div>
                          <div className={`text-xs ${(asset.pnl || asset.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(asset.pnl_percent || asset.unrealized_pnl_percent || 0)}
                          </div>
                        </div>
                      </div>
                    ))}
                    {selectedAccount.assets.length > 5 && (
                      <p className="text-sm text-gray-600 text-center pt-2">
                        And {selectedAccount.assets.length - 5} more assets...
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-600 text-sm">No assets in this account yet.</p>
                )}
              </div>

              {selectedAccount.description && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Description</h4>
                  <p className="text-gray-700 text-sm">{selectedAccount.description}</p>
                </div>
              )}

              <div className="text-xs text-gray-500">
                Created {formatDate(selectedAccount.created_at)} • Last updated {formatDate(selectedAccount.updated_at || selectedAccount.created_at)}
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
                <h3 className="text-lg font-semibold text-gray-900">Delete Account</h3>
              </div>

              <p className="text-gray-700 mb-6">
                Are you sure you want to delete this account? This action cannot be undone and will remove all associated assets.
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    // Handle delete logic here
                    setShowDeleteConfirm(null);
                  }}
                  className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 font-medium"
                >
                  Delete Account
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
