// ============ CORE PORTFOLIO TYPES ============

export interface Asset {
  id: number;
  account_id: number;
  symbol: string;
  name?: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  value: number;
  cost_basis: number;
  pnl: number;
  pnl_percent: number;
  day_change: number;
  day_change_percent: number;
  asset_type?: string;
  sector?: string;
  industry?: string;
  currency: string;
  exchange?: string;
  is_active: boolean;
  created_at: string;
  last_updated: string;
  price_updated_at: string;
}

export interface Account {
  id: number;
  clerk_user_id: string;
  name: string;
  account_type: string;
  description?: string;
  balance: number;
  cost_basis: number;
  pnl: number;
  pnl_percent: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  assets: Asset[];
}

export interface PortfolioAnalysis {
  total_value: number;
  diversity_score: number;
  risk_score: number;
  sentiment_score?: number;
  technical_score?: number;
  recommendation: string;
  confidence: number;
  insights: string[];
  analysis_type: string;
  symbols_analyzed?: number;
  performance?: {
    avg_rsi?: number;
    avg_momentum?: number;
    technical_signals?: number;
    news_coverage?: number;
  };
}

export interface PortfolioSummary {
  user_id: string;
  accounts: Account[];
  summary: {
    total_value: number;
    total_cost_basis: number;
    total_pnl: number;
    total_pnl_percent: number;
    total_accounts: number;
    total_assets: number;
  };
  analysis: PortfolioAnalysis;
  last_updated: string;
  status: string;
}

// Legacy interface for backward compatibility
export interface PortfolioData {
  accounts: Account[];
  total_value: number;
  total_assets: number;
  analysis: PortfolioAnalysis;
  last_updated: string;
  status: string;
}

// ============ FORM DATA TYPES (specific for forms) ============

export interface AccountCreateRequest {
  name: string;
  account_type: string;
  description?: string;
}

export interface AssetCreateRequest {
  account_id: number;
  symbol: string;
  shares: number;
  avg_cost: number;
}

// ============ PERFORMANCE TRACKING TYPES ============

export interface BenchmarkComparison {
  name: string;
  performance: number;
}

export interface RiskMetrics {
  beta: number;
  volatility: number;
  alpha: number;
  expense_ratio: number;
  sortino_ratio: number;
  value_at_risk: number;
}

export interface PerformancePortfolio {
  id: string;
  name: string;
  type: string;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_value: number;
  last_updated: string;
  benchmark_comparisons: BenchmarkComparison[];
  risk_metrics: RiskMetrics;
}

export interface PortfolioPerformanceSummary {
  total_portfolios: number;
  total_value: number;
  average_return: number;
  average_sharpe_ratio: number;
}

export type PortfolioSummaryStats = PortfolioPerformanceSummary;

export interface HoldingCreate {
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
}

export interface HoldingResponse {
  symbol: string;
  quantity: number;
  purchase_price: number;
  current_price: number;
  purchase_date: string;
  market_value: number;
  gain_loss: number;
  gain_loss_percentage: number;
}

export interface PortfolioCreate {
  name: string;
  type: string;
  initial_investment: number;
  expense_ratio?: number;
  holdings: HoldingCreate[];
}

// ============ AUTHENTICATION TYPES ============

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

export interface UserProfile {
  user_id: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  total_accounts: number;
  total_portfolio_value: number;
  last_active: string;
}

export interface AuthConfig {
  provider: string;
  configured: boolean;
  disabled: boolean;
  publishable_key?: string;
  domain?: string;
  mock_user?: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  message?: string;
}

// ============ MARKET DATA & ANALYSIS TYPES ============

export interface MarketStatus {
  status: string;
  timestamp: string;
  message: string;
  authenticated: boolean;
}

export interface AssetAnalysis {
  symbol: string;
  recommendation: string;
  technical: {
    rsi: number;
    rsi_signal: string;
    momentum: number;
    volatility: number;
    trend: string;
  };
  sentiment: {
    score: number;
    signal: string;
    confidence: number;
    news_count: number;
  };
  analysis_type: string;
}

// ============ UTILITY TYPES ============

export interface Benchmark {
  name: string;
  symbol: string;
  description: string;
}

export interface PerformanceMetrics {
  [key: string]: string;
}

export interface PortfolioFormData {
  name: string;
  type: string;
  initial_investment: number;
  expense_ratio: number;
}

export interface HoldingFormData {
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
}

export type FormValue = string | number | null | undefined;
