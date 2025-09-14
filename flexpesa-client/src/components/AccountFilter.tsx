import React from 'react';
import { PortfolioAccount } from '@/types'; // Use PortfolioAccount instead of Account
import { getAccountIcon } from '../lib/utils';

interface AccountFilterProps {
  accounts: PortfolioAccount[]; // Updated type
  selectedAccount: string;
  onAccountSelect: (accountId: string) => void;
}

const AccountFilter: React.FC<AccountFilterProps> = ({ accounts, selectedAccount, onAccountSelect }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onAccountSelect('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selectedAccount === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Accounts
        </button>
        {accounts.map((account) => (
          <button
            key={account.id}
            onClick={() => onAccountSelect(account.id.toString())}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              selectedAccount === account.id.toString()
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <span>{getAccountIcon(account.name)}</span>
            {account.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default AccountFilter;
