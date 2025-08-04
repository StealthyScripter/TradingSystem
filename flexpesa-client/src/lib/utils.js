import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount, decimals = 2) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(amount);
}

export function formatNumber(num, decimals = 2) {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
}

export function formatPercent(num, decimals = 2) {
  return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
}

export function getAccountIcon(accountName) {
  const iconMap = {
    'Wells Fargo Intuitive': '🏦',
    'Stack Well': '📈',
    'Cash App Investing': '📱',
    'Robinhood': '💳',
  };
  return iconMap[accountName] || '💼';
}
