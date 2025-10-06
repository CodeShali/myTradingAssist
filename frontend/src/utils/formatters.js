import { format, formatDistance, formatRelative } from 'date-fns';

// Currency formatting
export const formatCurrency = (value, decimals = 2) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

// Percentage formatting
export const formatPercent = (value, decimals = 2) => {
  return `${(value * 100).toFixed(decimals)}%`;
};

// Number formatting with commas
export const formatNumber = (value, decimals = 2) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

// Date formatting
export const formatDate = (date, formatStr = 'MMM dd, yyyy') => {
  return format(new Date(date), formatStr);
};

export const formatDateTime = (date) => {
  return format(new Date(date), 'MMM dd, yyyy HH:mm:ss');
};

export const formatTimeAgo = (date) => {
  return formatDistance(new Date(date), new Date(), { addSuffix: true });
};

export const formatRelativeTime = (date) => {
  return formatRelative(new Date(date), new Date());
};

// P&L color class
export const getPnLColorClass = (value) => {
  if (value > 0) return 'text-green-600';
  if (value < 0) return 'text-red-600';
  return 'text-gray-600';
};

// P&L with sign
export const formatPnL = (value) => {
  const formatted = formatCurrency(Math.abs(value));
  if (value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
};

// Option symbol parsing
export const parseOptionSymbol = (symbol) => {
  // Example: AAPL250117C00150000
  const match = symbol.match(/^([A-Z]+)(\d{6})([CP])(\d{8})$/);
  if (!match) return null;

  const [, underlying, date, type, strikeRaw] = match;
  const strike = parseInt(strikeRaw) / 1000;
  
  return {
    underlying,
    date,
    type: type === 'C' ? 'Call' : 'Put',
    strike,
  };
};

// Format option symbol for display
export const formatOptionSymbol = (symbol) => {
  const parsed = parseOptionSymbol(symbol);
  if (!parsed) return symbol;
  
  return `${parsed.underlying} ${parsed.strike} ${parsed.type}`;
};

// Compact number format (1K, 1M, etc.)
export const formatCompactNumber = (value) => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toFixed(0);
};

// Greeks formatting
export const formatGreek = (value, decimals = 4) => {
  return value.toFixed(decimals);
};
