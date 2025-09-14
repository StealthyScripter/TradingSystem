'use client';

import React, { useState, useEffect } from 'react';
import { portfolioAPI } from '../lib/api';
import PortfolioSummary from '../components/PortfolioSummary';
import { Account, Asset, PortfolioSummary as PortfolioSummaryType, AccountCreateRequest, AssetCreateRequest, PortfolioAccount } from '@/types';
import AccountFilter from '../components/AccountFilter';
import AssetTable from '../components/AssetTable';
import QuickActions from '../components/QuickActions';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Header from '@/components/Header';

export default function Dashboard() {
  const [portfolioData, setPortfolioData] = useState<PortfolioSummaryType | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch portfolio data
  const fetchPortfolioData = async () => {
    try {
      setError(null);
      const result = await portfolioAPI.getPortfolioSummary();

      const mappedAccounts: PortfolioAccount[] = result.accounts.map((acc: Account) => ({
        ...acc,
        clerk_user_id: acc.clerk_user_id ?? '',
        is_active: acc.is_active ?? true,
        updated_at: acc.updated_at ?? new Date().toISOString(),
        portfolio_id: acc.id,
      }));

      setPortfolioData({ ...result, accounts: mappedAccounts });
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error: Unable to connect to backend';
      setError(errorMessage);
      console.error('Failed to fetch portfolio data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Refresh prices
  const handleRefreshPrices = async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    try {
      const result = await portfolioAPI.updatePrices();
      console.log(`Updated ${result.updated_assets} of ${result.total_assets} assets`);
      await fetchPortfolioData();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update prices';
      setError(errorMessage);
      console.error('Failed to update prices:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Add new account
  const handleAddAccount = async (accountData: AccountCreateRequest) => {
    try {
      const result = await portfolioAPI.createAccount(accountData);
      console.log('Account created:', result);
      await fetchPortfolioData();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add account';
      setError(errorMessage);
      console.error('Failed to add account:', err);
    }
  };

  // Add new asset
  const handleAddAsset = async (assetData: AssetCreateRequest) => {
    try {
      const result = await portfolioAPI.addAsset(assetData);
      console.log('Asset added:', result);
      await fetchPortfolioData();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add asset';
      setError(errorMessage);
      console.error('Failed to add asset:', err);
    }
  };

  // Run AI analysis
  const handleAnalyze = async (symbol: string) => {
    try {
      const result = await portfolioAPI.getQuickAnalysis([symbol]);
      alert(`AI Analysis for ${symbol}: ${JSON.stringify(result.analysis[symbol], null, 2)}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get analysis';
      setError(errorMessage);
      console.error('Failed to get analysis:', err);
    }
  };

  // Run general AI analysis
  const handleRunAnalysis = async () => {
    if (!portfolioData?.accounts) return;

    const allSymbols = portfolioData.accounts
      .flatMap((account: Account) => account.assets.map((asset: Asset) => asset.symbol))
      .slice(0, 5);

    if (allSymbols.length > 0) {
      await handleAnalyze(allSymbols[0]);
    }
  };

  // Initial load
  useEffect(() => {
    fetchPortfolioData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="xl" className="mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Loading Portfolio...</h2>
          <p className="text-gray-500">Fetching your investment data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <Header title="Portfolio Dashboard" subtitle="Real-time portfolio management with AI-powered insights"/>

        {/* Error Message */}
        {error && (
          <ErrorMessage
            message={error}
            onRetry={() => {
              setError(null);
              fetchPortfolioData();
            }}
          />
        )}

        {/* Portfolio Summary - Pass the complete PortfolioSummary object */}
        {portfolioData && (
          <PortfolioSummary
            portfolioData={portfolioData} // Pass entire API response, not transformed object
            lastUpdated={lastUpdated}
            onRefresh={handleRefreshPrices}
            isRefreshing={isRefreshing}
          />
        )}

        {/* Account Filter */}
        {portfolioData?.accounts && (
          <AccountFilter
            accounts={portfolioData.accounts}
            selectedAccount={selectedAccount}
            onAccountSelect={setSelectedAccount}
          />
        )}

        {/* Quick Actions */}
        {portfolioData?.accounts && (
          <QuickActions
            accounts={portfolioData.accounts}
            onAddAccount={handleAddAccount}
            onAddAsset={handleAddAsset}
            onRunAnalysis={handleRunAnalysis}
          />
        )}

        {/* Asset Table */}
        {portfolioData?.accounts && (
          <AssetTable
            accounts={portfolioData.accounts}
            selectedAccount={selectedAccount}
            onAnalyze={handleAnalyze}
          />
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>Built with Next.js + FastAPI • Real-time market data via yfinance</p>
          <p className="mt-1">Portfolio value updates every 30 seconds</p>
        </div>
      </div>
    </div>
  );
}
