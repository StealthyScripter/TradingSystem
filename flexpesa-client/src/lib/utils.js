import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// Safely format currency with null/undefined protection
export function formatCurrency(amount, decimals = 2) {
  // Handle null, undefined, NaN, or invalid values
  if (amount === null || amount === undefined || isNaN(amount) || amount === '') {
    return '$0.00';
  }
  
  // Convert string to number if needed
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  
  // Check again after conversion
  if (isNaN(numAmount)) {
    return '$0.00';
  }
  
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(numAmount);
  } catch (error) {
    console.warn('Error formatting currency:', amount, error);
    return '$0.00';
  }
}

// Safely format numbers with null/undefined protection
export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined || isNaN(num) || num === '') {
    return '0.00';
  }
  
  const numValue = typeof num === 'string' ? parseFloat(num) : num;
  
  if (isNaN(numValue)) {
    return '0.00';
  }
  
  try {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(numValue);
  } catch (error) {
    console.warn('Error formatting number:', num, error);
    return '0.00';
  }
}

// Safely format percentage with null/undefined protection
export function formatPercent(num, decimals = 2) {
  if (num === null || num === undefined || isNaN(num) || num === '') {
    return '+0.00%';
  }
  
  const numValue = typeof num === 'string' ? parseFloat(num) : num;
  
  if (isNaN(numValue)) {
    return '+0.00%';
  }
  
  try {
    const sign = numValue >= 0 ? '+' : '';
    return `${sign}${numValue.toFixed(decimals)}%`;
  } catch (error) {
    console.warn('Error formatting percent:', num, error);
    return '+0.00%';
  }
}

// Safely format date with null/undefined protection
export function formatDate(dateString) {
  if (!dateString || dateString === 'Invalid Date') {
    return 'Just now';
  }
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Just now';
    }
    
    // Return relative time if recent, otherwise formatted date
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.warn('Error formatting date:', dateString, error);
    return 'Just now';
  }
}

// Get account icon with fallback
export function getAccountIcon(accountName) {
  if (!accountName || typeof accountName !== 'string') {
    return '💼';
  }
  
  const iconMap = {
    'Wells Fargo Intuitive': '🏦',
    'Wells Fargo': '🏦',
    'Stack Well': '📈',
    'Cash App Investing': '📱',
    'Cash App': '📱',
    'Robinhood': '💳',
    'TD Ameritrade': '🎯',
    'Fidelity': '🛡️',
    'Charles Schwab': '🔷',
    'E*TRADE': '⚡',
    'Vanguard': '🏛️',
    'Coinbase': '₿',
    'Kraken': '🐙',
    'Binance': '🟡',
  };
  
  // Try exact match first
  if (iconMap[accountName]) {
    return iconMap[accountName];
  }
  
  // Try partial match
  const lowerName = accountName.toLowerCase();
  for (const [key, icon] of Object.entries(iconMap)) {
    if (lowerName.includes(key.toLowerCase()) || key.toLowerCase().includes(lowerName)) {
      return icon;
    }
  }
  
  // Default fallback
  return '💼';
}

// Validate and clean asset data
export function validateAssetData(asset) {
  if (!asset || typeof asset !== 'object') {
    return null;
  }
  
  return {
    id: asset.id || 0,
    symbol: asset.symbol || 'UNKNOWN',
    shares: formatNumber(asset.shares || 0),
    avg_cost: asset.avg_cost || 0,
    current_price: asset.current_price || 0,
    value: asset.value || 0,
    last_updated: asset.last_updated || new Date().toISOString(),
    pnl: asset.pnl || 0,
    pnl_percent: asset.pnl_percent || 0,
  };
}

// Validate and clean account data
export function validateAccountData(account) {
  if (!account || typeof account !== 'object') {
    return null;
  }
  
  return {
    id: account.id || 0,
    name: account.name || 'Unknown Account',
    account_type: account.account_type || 'brokerage',
    balance: account.balance || 0,
    assets: Array.isArray(account.assets) 
      ? account.assets.map(validateAssetData).filter(Boolean)
      : [],
    created_at: account.created_at || new Date().toISOString(),
  };
}

// Check if a value is considered "loading" or invalid
export function isLoadingValue(value) {
  return value === null || 
         value === undefined || 
         value === '' || 
         isNaN(value) || 
         value === 'N/A' ||
         value === 'Invalid Date';
}

// Get status color class based on P&L
export function getPnLColorClass(pnl) {
  if (isLoadingValue(pnl) || pnl === 0) {
    return 'text-gray-600';
  }
  return pnl >= 0 ? 'text-green-600' : 'text-red-600';
}
