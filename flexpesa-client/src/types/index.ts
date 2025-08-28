export interface Asset {
  id: number;
  account_id: number;
  symbol: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  value: number;
  last_updated: string;
  pnl: number;
  pnl_percent: number;
}

export interface Account {
  id: number;
  name: string;
  account_type: string;
  balance: number;
  assets: Asset[];
  created_at: string;
}

export interface PortfolioAnalysis {
  total_value: number;
  diversity_score: number;
  risk_score: number;
  recommendation: string;
  confidence: number;
  insights: string[];
}

export interface PortfolioData {
  accounts: Account[];
  total_value: number;
  total_assets: number;
  analysis: PortfolioAnalysis;
  last_updated: string;
  status: string;
}

export type APIResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string };


export interface AssetCreate {
  account_id: number;
  symbol: string;
  shares: number;
  avg_cost: number;
}

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

export interface PortfolioSummary {
  total_portfolios: number;
  total_value: number;
  average_return: number;
  average_sharpe_ratio: number;
}

export interface HoldingCreate {
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
}

export interface PortfolioCreate {
  name: string;
  type: string;
  initial_investment: number;
  expense_ratio?: number;
  holdings: HoldingCreate[];
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

export interface Asset {
  id: number;
  account_id: number;
  symbol: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  value: number;
  last_updated: string;
  pnl: number;
  pnl_percent: number;
}

export interface Account {
  id: number;
  name: string;
  account_type: string;
  balance: number;
  assets: Asset[];
  created_at: string;
}

export interface PortfolioAnalysis {
  total_value: number;
  diversity_score: number;
  risk_score: number;
  recommendation: string;
  confidence: number;
  insights: string[];
}

export interface PortfolioData {
  accounts: Account[];
  total_value: number;
  total_assets: number;
  analysis: PortfolioAnalysis;
  last_updated: string;
  status: string;
}

export interface BenchmarkComparison {
  name: string;
  performance: number; // positive means outperform, negative means underperform
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

export interface HoldingCreate {
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
}

export interface PortfolioCreate {
  name: string;
  type: string;
  initial_investment: number;
  expense_ratio?: number;
  holdings: HoldingCreate[];
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
