import React from 'react';
import { TrendingUp, TrendingDown, Brain, BarChart3 } from 'lucide-react';
import { formatCurrency, formatNumber, formatPercent, getAccountIcon } from '../lib/utils';

const AssetTable = ({ accounts, selectedAccount, onAnalyze }) => {
  const filteredAccounts = selectedAccount === 'all' 
    ? accounts 
    : accounts.filter(account => account.id === selectedAccount);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-xl font-bold mb-6">Portfolio Holdings</h3>
      
      <div className="space-y-6">
        {filteredAccounts.map((account) => (
          <div key={account.id} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getAccountIcon(account.name)}</span>
                <div>
                  <h4 className="font-semibold text-lg">{account.name}</h4>
                  <p className="text-sm text-gray-600">
                    {formatCurrency(account.balance)} • {account.assets.length} assets
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">
                  {formatCurrency(account.balance)}
                </div>
                <div className="text-sm text-gray-600">
                  {account.account_type}
                </div>
              </div>
            </div>
            
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
                    <th className="pb-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {account.assets.map((asset, index) => {
                    const currentValue = asset.shares * asset.current_price;
                    const totalCost = asset.shares * asset.avg_cost;
                    const pnl = currentValue - totalCost;
                    const pnlPercent = totalCost > 0 ? ((currentValue - totalCost) / totalCost) * 100 : 0;
                    
                    return (
                      <tr key={index} className="border-b hover:bg-gray-50 transition-colors">
                        <td className="py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-bold text-blue-600">
                                {asset.symbol.slice(0, 2)}
                              </span>
                            </div>
                            <div>
                              <span className="font-semibold">{asset.symbol}</span>
                              <div className="text-xs text-gray-500">
                                Updated {new Date(asset.last_updated).toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 font-medium">{formatNumber(asset.shares)}</td>
                        <td className="py-4">{formatCurrency(asset.avg_cost)}</td>
                        <td className="py-4 font-semibold">
                          {asset.current_price > 0 ? formatCurrency(asset.current_price) : 'N/A'}
                        </td>
                        <td className="py-4 font-bold">{formatCurrency(currentValue)}</td>
                        <td className={`py-4 font-semibold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          <div className="flex items-center gap-1">
                            {pnl >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                            {formatCurrency(Math.abs(pnl))}
                          </div>
                          <div className="text-xs">({formatPercent(pnlPercent)})</div>
                        </td>
                        <td className="py-4">
                          <div className="flex gap-2">
                            <button 
                              onClick={() => onAnalyze(asset.symbol)}
                              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 flex items-center gap-1"
                            >
                              <Brain size={14} />
                              Analyze
                            </button>
                            <button className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 flex items-center gap-1">
                              <BarChart3 size={14} />
                              Chart
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AssetTable;
