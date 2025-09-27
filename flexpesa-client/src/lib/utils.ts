import { clsx, ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Asset, Account, PortfolioAccount } from '@/types'; // Add PortfolioAccount import

interface RawAssetData {
  id?: number;
  account_id?: number;
  symbol?: string;
  name?: string;
  shares?: number | string;
  avg_cost?: number | string;
  current_price?: number | string;
  market_value?: number | string;  // API returns market_value
  value?: number | string;         // Fallback for backward compatibility
  cost_basis?: number | string;
  unrealized_pnl?: number | string;  // API returns unrealized_pnl
  pnl?: number | string;             // Fallback for backward compatibility
  unrealized_pnl_percent?: number | string;  // API returns unrealized_pnl_percent
  pnl_percent?: number | string;             // Fallback for backward compatibility
  day_change?: number | string;
  day_change_percent?: number | string;
  asset_type?: string;
  sector?: string;
  industry?: string;
  currency?: string;
  exchange?: string;
  is_active?: boolean;
  created_at?: string;
  last_updated?: string;
  price_updated_at?: string;
  [key: string]: unknown;
}

interface RawAccountData {
  id?: number;
  clerk_user_id?: string;
  name?: string;
  account_type?: string;
  description?: string;
  balance?: number | string;
  cost_basis?: number | string;
  pnl?: number | string;
  pnl_percent?: number | string;
  currency?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  assets?: RawAssetData[];
  [key: string]: unknown;
}

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(
  amount: number | string | null | undefined,
  decimals: number = 2
): string {
  if (amount === null || amount === undefined || amount === '' || isNaN(Number(amount))) {
    return '$0.00';
  }

  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;

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

export function formatNumber(
  num: number | string | null | undefined,
  decimals: number = 2
): string {
  if (num === null || num === undefined || num === '' || isNaN(Number(num))) {
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

export function formatPercent(
  num: number | string | null | undefined,
  decimals: number = 2
): string {
  if (num === null || num === undefined || num === '' || isNaN(Number(num))) {
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

export function formatDate(dateString: string | null | undefined): string {
  if (!dateString || dateString === 'Invalid Date') {
    return 'Just now';
  }

  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Just now';
    }

    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

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

export function getAccountIcon(accountName: string | null | undefined): string {
  if (!accountName || typeof accountName !== 'string') {
    return '💼';
  }

  const iconMap: Record<string, string> = {
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

function safeNumber(value: unknown): number {
  if (value == null) return 0; // handles null + undefined

  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    if (isNaN(parsed)) {
      console.warn('Invalid numeric value encountered:', value);
      return 0;
    }
    return parsed;
  }

  console.warn('Unexpected value type for number conversion:', typeof value, value);
  return 0;
}


function safeString(value: unknown): string {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return '';
  return String(value);
}

function safeBoolean(value: unknown): boolean {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'string') return value.toLowerCase() === 'true';
  return Boolean(value);
}

// Updated to match actual API response structure
export function validateAssetData(asset: unknown): Asset | null {
  if (!asset || typeof asset !== 'object' || asset === null) {
    return null;
  }

  const rawAsset = asset as RawAssetData;

  return {
    id: safeNumber(rawAsset.id),
    account_id: safeNumber(rawAsset.account_id),
    symbol: safeString(rawAsset.symbol) || 'UNKNOWN',
    name: safeString(rawAsset.name),
    shares: safeNumber(rawAsset.shares),
    avg_cost: safeNumber(rawAsset.avg_cost),
    current_price: safeNumber(rawAsset.current_price),
    // Use API property names with fallbacks
    value: safeNumber(rawAsset.market_value) || safeNumber(rawAsset.value), // market_value is primary
    cost_basis: safeNumber(rawAsset.cost_basis),
    pnl: safeNumber(rawAsset.unrealized_pnl) || safeNumber(rawAsset.pnl), // unrealized_pnl is primary
    pnl_percent: safeNumber(rawAsset.unrealized_pnl_percent) || safeNumber(rawAsset.pnl_percent), // unrealized_pnl_percent is primary
    day_change: safeNumber(rawAsset.day_change),
    day_change_percent: safeNumber(rawAsset.day_change_percent),
    asset_type: safeString(rawAsset.asset_type),
    sector: safeString(rawAsset.sector),
    industry: safeString(rawAsset.industry),
    currency: safeString(rawAsset.currency) || 'USD',
    exchange: safeString(rawAsset.exchange),
    is_active: safeBoolean(rawAsset.is_active),
    created_at: safeString(rawAsset.created_at) || new Date().toISOString(),
    last_updated: safeString(rawAsset.last_updated) || new Date().toISOString(),
    price_updated_at: safeString(rawAsset.price_updated_at) || new Date().toISOString(),

    // Additional computed properties for backward compatibility
    market_value: safeNumber(rawAsset.market_value) || safeNumber(rawAsset.value),
    unrealized_pnl: safeNumber(rawAsset.unrealized_pnl) || safeNumber(rawAsset.pnl),
    unrealized_pnl_percent: safeNumber(rawAsset.unrealized_pnl_percent) || safeNumber(rawAsset.pnl_percent),
  };
}

// Updated to match actual API response structure
export function validateAccountData(account: unknown): Account | null {
  if (!account || typeof account !== 'object' || account === null) {
    return null;
  }

  const rawAccount = account as RawAccountData;

  return {
    id: safeNumber(rawAccount.id),
    clerk_user_id: safeString(rawAccount.clerk_user_id),
    name: safeString(rawAccount.name) || 'Unknown Account',
    account_type: safeString(rawAccount.account_type) || 'brokerage',
    description: safeString(rawAccount.description),
    balance: safeNumber(rawAccount.balance),
    cost_basis: safeNumber(rawAccount.cost_basis),
    pnl: safeNumber(rawAccount.pnl),
    pnl_percent: safeNumber(rawAccount.pnl_percent),
    currency: safeString(rawAccount.currency) || 'USD',
    is_active: safeBoolean(rawAccount.is_active),
    created_at: safeString(rawAccount.created_at) || new Date().toISOString(),
    updated_at: safeString(rawAccount.updated_at) || new Date().toISOString(),
    assets: Array.isArray(rawAccount.assets)
      ? rawAccount.assets.map(validateAssetData).filter((asset): asset is Asset => asset !== null)
      : [],
  };
}

export function validatePortfolioAccountData(account: PortfolioAccount | null | undefined): PortfolioAccount | null {
  if (!account) return null;
  if (!account.id || !account.name) return null; // example validation
  return account;
}


export function isLoadingValue(value: unknown): boolean {
  return value === null ||
         value === undefined ||
         value === '' ||
         (typeof value === 'number' && isNaN(value)) ||
         value === 'N/A' ||
         value === 'Invalid Date';
}

export function getPnLColorClass(pnl: number | null | undefined): string {
  if (isLoadingValue(pnl) || pnl === 0) {
    return 'text-gray-600';
  }
  return (pnl as number) >= 0 ? 'text-green-600' : 'text-red-600';
}

export function isValidAssetData(data: unknown): data is RawAssetData {
  return typeof data === 'object' && data !== null;
}

export function isValidAccountData(data: unknown): data is RawAccountData {
  return typeof data === 'object' && data !== null;
}

export type FormValue = string | number | null | undefined;

export function parseFormNumber(value: FormValue): number {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
  }
  return 0;
}

export function parseFormString(value: FormValue): string {
  if (typeof value === 'string') return value.trim();
  if (value === null || value === undefined) return '';
  return String(value);
}
