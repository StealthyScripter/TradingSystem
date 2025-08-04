import React, { useState } from 'react';
import { Plus, DollarSign, Brain, TrendingUp } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const QuickActions = ({ onAddAccount, onAddAsset, onRunAnalysis, accounts }) => {
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [showAddAsset, setShowAddAsset] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const [accountForm, setAccountForm] = useState({
    name: '',
    account_type: 'brokerage'
  });

  const [assetForm, setAssetForm] = useState({
    account_id: '',
    symbol: '',
    shares: '',
    avg_cost: ''
  });

  const handleAddAccount = async (e) => {
    e.preventDefault();
    setLoading(true);
    await onAddAccount(accountForm);
    setAccountForm({ name: '', account_type: 'brokerage' });
    setShowAddAccount(false);
    setLoading(false);
  };

  const handleAddAsset = async (e) => {
    e.preventDefault();
    setLoading(true);
    await onAddAsset({
      ...assetForm,
      account_id: parseInt(assetForm.account_id),
      shares: parseFloat(assetForm.shares),
      avg_cost: parseFloat(assetForm.avg_cost)
    });
    setAssetForm({ account_id: '', symbol: '', shares: '', avg_cost: '' });
    setShowAddAsset(false);
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Add Account */}
        <button
          onClick={() => setShowAddAccount(!showAddAccount)}
          className="flex items-center gap-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <Plus size={20} className="text-blue-600" />
          <span className="font-medium">Add Account</span>
        </button>

        {/* Add Asset */}
        <button
          onClick={() => setShowAddAsset(!showAddAsset)}
          className="flex items-center gap-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
        >
          <DollarSign size={20} className="text-green-600" />
          <span className="font-medium">Add Asset</span>
        </button>

        {/* Run Analysis */}
        <button
          onClick={onRunAnalysis}
          className="flex items-center gap-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors"
        >
          <Brain size={20} className="text-purple-600" />
          <span className="font-medium">AI Analysis</span>
        </button>

        {/* Portfolio Stats */}
        <div className="flex items-center gap-2 p-4 bg-gray-50 rounded-lg">
          <TrendingUp size={20} className="text-orange-600" />
          <div>
            <div className="font-medium text-sm">Portfolio Health</div>
            <div className="text-xs text-gray-600">Excellent</div>
          </div>
        </div>
      </div>

      {/* Add Account Form */}
      {showAddAccount && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold mb-3">Add New Account</h4>
          <form onSubmit={handleAddAccount} className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Account Name</label>
              <input
                type="text"
                required
                value={accountForm.name}
                onChange={(e) => setAccountForm({...accountForm, name: e.target.value})}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., TD Ameritrade"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Account Type</label>
              <select
                value={accountForm.account_type}
                onChange={(e) => setAccountForm({...accountForm, account_type: e.target.value})}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
              >
                <option value="brokerage">Brokerage</option>
                <option value="retirement">Retirement</option>
                <option value="crypto">Crypto</option>
                <option value="trading">Trading</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Add Account'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddAccount(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Add Asset Form */}
      {showAddAsset && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <h4 className="font-semibold mb-3">Add New Asset</h4>
          <form onSubmit={handleAddAsset} className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Account</label>
              <select
                required
                value={assetForm.account_id}
                onChange={(e) => setAssetForm({...assetForm, account_id: e.target.value})}
                className="w-full p-2 border rounded focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select Account</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>{account.name}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium mb-1">Symbol</label>
                <input
                  type="text"
                  required
                  value={assetForm.symbol}
                  onChange={(e) => setAssetForm({...assetForm, symbol: e.target.value.toUpperCase()})}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-green-500"
                  placeholder="AAPL"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Shares</label>
                <input
                  type="number"
                  step="0.001"
                  required
                  value={assetForm.shares}
                  onChange={(e) => setAssetForm({...assetForm, shares: e.target.value})}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-green-500"
                  placeholder="10"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Avg Cost</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={assetForm.avg_cost}
                  onChange={(e) => setAssetForm({...assetForm, avg_cost: e.target.value})}
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-green-500"
                  placeholder="150.00"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Add Asset'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddAsset(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default QuickActions;

