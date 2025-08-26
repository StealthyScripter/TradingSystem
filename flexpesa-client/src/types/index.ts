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
