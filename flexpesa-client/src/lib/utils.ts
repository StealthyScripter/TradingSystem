import { clsx, ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Asset, Account } from '@/types';

interface RawAssetData {
  id?: number;
  account_id?: number;
  symbol?: string;
  shares?: number | string;
  avg_cost?: number | string;
  current_price?: number | string;
  value?: number | string;
  last_updated?: string;
  pnl?: number | string;
  pnl_percent?: number | string;
  [key: string]: unknown; 
}

interface RawAccountData {
  id?: number;
  name?: string;
  account_type?: string;
  balance?: number | string;
  assets?: RawAssetData[];
  created_at?: string;
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
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
  }
  return 0;
}

function safeString(value: unknown): string {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return '';
  return String(value);
}

export function validateAssetData(asset: unknown): Asset | null {
  if (!asset || typeof asset !== 'object' || asset === null) {
    return null;
  }
  
  const rawAsset = asset as RawAssetData;
  
  return {
    id: safeNumber(rawAsset.id),
    account_id: safeNumber(rawAsset.account_id),
    symbol: safeString(rawAsset.symbol) || 'UNKNOWN',
    shares: safeNumber(rawAsset.shares),
    avg_cost: safeNumber(rawAsset.avg_cost),
    current_price: safeNumber(rawAsset.current_price),
    value: safeNumber(rawAsset.value),
    last_updated: safeString(rawAsset.last_updated) || new Date().toISOString(),
    pnl: safeNumber(rawAsset.pnl),
    pnl_percent: safeNumber(rawAsset.pnl_percent),
  };
}

export function validateAccountData(account: unknown): Account | null {
  if (!account || typeof account !== 'object' || account === null) {
    return null;
  }
  
  const rawAccount = account as RawAccountData;
  
  return {
    id: safeNumber(rawAccount.id),
    name: safeString(rawAccount.name) || 'Unknown Account',
    account_type: safeString(rawAccount.account_type) || 'brokerage',
    balance: safeNumber(rawAccount.balance),
    assets: Array.isArray(rawAccount.assets) 
      ? rawAccount.assets.map(validateAssetData).filter((asset): asset is Asset => asset !== null)
      : [],
    created_at: safeString(rawAccount.created_at) || new Date().toISOString(),
  };
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
