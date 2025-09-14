import React from 'react';
import { TrendingUp, TrendingDown, Brain, BarChart3, RefreshCw } from 'lucide-react';
import { PortfolioAccount, Asset } from '@/types'; // Use PortfolioAccount instead of Account
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  formatDate,
  getAccountIcon,
  validateAssetData,
  validatePortfolioAccountData, // New validation function for PortfolioAccount
  isLoadingValue,
  getPnLColorClass
} from '../lib/utils';

interface AssetTableProps {
  accounts: PortfolioAccount[]; // Updated type
  selectedAccount: string;
  onAnalyze: (symbol: string) => void;
}

interface AccountSectionProps {
  account: PortfolioAccount; // Updated type
  onAnalyze: (symbol: string) => void;
}

interface AssetRowProps {
  asset: Asset;
  onAnalyze: (symbol: string) => void;
}



const AssetTable: React.FC<AssetTableProps> = ({ accounts, selectedAccount, onAnalyze }) => {
  // Validate and filter accounts
  const validAccounts = (accounts || [])
    .map(validatePortfolioAccountData)
    .filter(Boolean) as PortfolioAccount[];

  const filteredAccounts = selectedAccount === 'all'
    ? validAccounts
    : validAccounts.filter(account => account.id.toString() === selectedAccount.toString());

  if (!filteredAccounts.length) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h3 className="text-xl font-bold mb-6">Portfolio Holdings</h3>
        <div className="text-center py-8 text-gray-500">
          <RefreshCw className="mx-auto mb-4 h-12 w-12 animate-spin" />
          <p>Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-xl font-bold mb-6">Portfolio Holdings</h3>

      <div className="space-y-6">
        {filteredAccounts.map((account) => (
          <AccountSection
            key={account.id}
            account={account}
            onAnalyze={onAnalyze}
          />
        ))}
      </div>
    </div>
  );
};

const AccountSection: React.FC<AccountSectionProps> = ({ account, onAnalyze }) => {
  const validAssets = (account.assets || [])
    .map(validateAssetData)
    .filter(Boolean) as Asset[];

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getAccountIcon(account.name)}</span>
          <div>
            <h4 className="font-semibold text-lg">{account.name}</h4>
            <p className="text-sm text-gray-600">
              {formatCurrency(account.balance)} • {validAssets.length} assets
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-gray-900">
            {formatCurrency(account.balance)}
          </div>
          <div className="text-sm text-gray-600 capitalize">
            {account.account_type}
          </div>
        </div>
      </div>

      {validAssets.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-600 border-b">
                <th className="pb-3">Asset</th>
                <th className="pb-3">Shares</th>
                <th className="pb-3">Avg Cost</th>
                <th className="pb-3">Current Price</th>
                <th className="pb-3">Market Value</th>
                <th className="pb-3">P&L</th>
                <th className="pb-3">Day Change</th>
                <th className="pb-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {validAssets.map((asset, index) => (
                <AssetRow
                  key={asset.id || index}
                  asset={asset}
                  onAnalyze={onAnalyze}
                />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-4 text-gray-500">
          <p>No assets in this account</p>
        </div>
      )}
    </div>
  );
};

const AssetRow: React.FC<AssetRowProps> = ({ asset, onAnalyze }) => {
  // Use API-provided calculated values instead of manual calculations
  const shares = asset.shares || 0;
  const avgCost = asset.avg_cost || 0;
  const currentPrice = asset.current_price || 0;
  const marketValue = asset.market_value || asset.value || 0; // Use API-provided market_value
  const unrealizedPnL = asset.unrealized_pnl || asset.pnl || 0; // Use API-provided unrealized_pnl
  const unrealizedPnLPercent = asset.unrealized_pnl_percent || asset.pnl_percent || 0; // Use API-provided percentage
  const dayChange = asset.day_change || 0; // Use API-provided day_change
  const dayChangePercent = asset.day_change_percent || 0; // Use API-provided day_change_percent

  // Check if data is still loading
  const isPriceLoading = currentPrice === 0 || isLoadingValue(currentPrice);
  const isDataLoading = isLoadingValue(avgCost) || isLoadingValue(shares);

  return (
    <tr className="border-b hover:bg-gray-50 transition-colors">
      <td className="py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-sm font-bold text-blue-600">
              {(asset.symbol || 'UN').slice(0, 2)}
            </span>
          </div>
          <div>
            <span className="font-semibold">{asset.symbol || 'UNKNOWN'}</span>
            {asset.name && (
              <div className="text-xs text-gray-500">{asset.name}</div>
            )}
            <div className="text-xs text-gray-500">
              Updated {formatDate(asset.last_updated)}
            </div>
          </div>
        </div>
      </td>

      <td className="py-4 font-medium">
        {isDataLoading ? (
          <div className="animate-pulse bg-gray-200 h-4 w-16 rounded"></div>
        ) : (
          formatNumber(shares)
        )}
      </td>

      <td className="py-4">
        {isDataLoading ? (
          <div className="animate-pulse bg-gray-200 h-4 w-20 rounded"></div>
        ) : (
          formatCurrency(avgCost)
        )}
      </td>

      <td className="py-4 font-semibold">
        {isPriceLoading ? (
          <div className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin text-gray-400" />
            <span className="text-gray-500">Loading...</span>
          </div>
        ) : (
          <span className="text-green-600">{formatCurrency(currentPrice)}</span>
        )}
      </td>

      <td className="py-4 font-bold">
        {isPriceLoading || isDataLoading ? (
          <div className="animate-pulse bg-gray-200 h-4 w-24 rounded"></div>
        ) : (
          formatCurrency(marketValue)
        )}
      </td>

      <td className={`py-4 font-semibold ${getPnLColorClass(unrealizedPnL)}`}>
        {isPriceLoading || isDataLoading ? (
          <div className="animate-pulse bg-gray-200 h-4 w-20 rounded"></div>
        ) : (
          <div className="flex items-center gap-1">
            {unrealizedPnL >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <div>
              <div>{formatCurrency(Math.abs(unrealizedPnL))}</div>
              <div className="text-xs">({formatPercent(Math.abs(unrealizedPnLPercent))})</div>
            </div>
          </div>
        )}
      </td>

      <td className={`py-4 font-medium ${getPnLColorClass(dayChange)}`}>
        {isPriceLoading || isDataLoading ? (
          <div className="animate-pulse bg-gray-200 h-4 w-20 rounded"></div>
        ) : (
          <div className="flex items-center gap-1">
            {dayChange >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <div>
              <div className="text-sm">{formatCurrency(Math.abs(dayChange))}</div>
              <div className="text-xs">({formatPercent(Math.abs(dayChangePercent))})</div>
            </div>
          </div>
        )}
      </td>

      <td className="py-4">
        <div className="flex gap-2">
          <button
            onClick={() => onAnalyze(asset.symbol)}
            disabled={!asset.symbol || asset.symbol === 'UNKNOWN'}
            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
          >
            <Brain size={14} />
            Analyze
          </button>
          <button
            disabled={!asset.symbol || asset.symbol === 'UNKNOWN'}
            className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 disabled:bg-gray-50 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
          >
            <BarChart3 size={14} />
            Chart
          </button>
        </div>
      </td>
    </tr>
  );
};

export default AssetTable;
