// flexpesa-client/src/lib/api.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

// ============ TYPE DEFINITIONS ============

interface AuthConfig {
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

interface UserProfile {
  user_id: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  total_accounts: number;
  total_portfolio_value: number;
  last_active: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

interface LoginResponse {
  user: User;
  message: string;
}

interface Account {
  id: number;
  name: string;
  account_type: string;
  balance: number;
  description?: string;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  total_value: number;
  asset_count: number;
}

interface AccountCreate {
  name: string;
  account_type: string;
  description?: string;
  currency?: string;
}

interface Asset {
  id: number;
  account_id: number;
  symbol: string;
  name?: string;
  shares: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  cost_basis: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  asset_type?: string;
  sector?: string;
  industry?: string;
  currency: string;
  exchange?: string;
  is_active: boolean;
  created_at: string;
  last_updated: string;
  price_updated_at?: string;
}

interface AssetCreate {
  account_id: number;
  symbol: string;
  shares: number;
  avg_cost: number;
}

interface PortfolioSummary {
  user_id: string;
  accounts: Array<{
    id: number;
    name: string;
    account_type: string;
    description?: string;
    balance: number;
    cost_basis: number;
    pnl: number;
    pnl_percent: number;
    currency: string;
    created_at: string;
    assets: Asset[];
  }>;
  summary: {
    total_value: number;
    total_cost_basis: number;
    total_pnl: number;
    total_pnl_percent: number;
    total_accounts: number;
    total_assets: number;
  };
  analysis: {
    total_value: number;
    diversity_score: number;
    risk_score: number;
    sentiment_score: number;
    technical_score: number;
    recommendation: string;
    confidence: number;
    insights: string[];
    analysis_type: string;
    symbols_analyzed: number;
    performance: {
      avg_rsi: number;
      avg_momentum: number;
      technical_signals: number;
      news_coverage: number;
    };
  };
  last_updated: string;
  status: string;
}

interface UpdatePricesResponse {
  updated_assets: number;
  total_assets: number;
  unique_symbols: number;
  failed_symbols: string[];
  duration: number;
  timestamp: string;
}

interface PerformancePortfolio {
  id: string;
  name: string;
  type: string;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_value: number;
  last_updated: string;
  benchmark_comparisons: Array<{
    name: string;
    performance: number;
  }>;
  risk_metrics: {
    beta: number;
    volatility: number;
    alpha: number;
    expense_ratio: number;
    sortino_ratio: number;
    value_at_risk: number;
  };
}

interface PortfolioSummaryStats {
  total_portfolios: number;
  total_value: number;
  average_return: number;
  average_sharpe_ratio: number;
}

interface QuickAnalysisResponse {
  analysis: Record<
    string,
    {
      sentiment: string;
      confidence: number;
      recommendation: string;
      note: string;
    }
  >;
}

interface AssetAnalysis {
  success: boolean;
  symbol: string;
  analysis: {
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
  };
  timestamp: string;
}

interface MarketStatus {
  status: string;
  timestamp: string;
  message: string;
  authenticated: boolean;
}

interface BenchmarksResponse {
  benchmarks: Array<{
    name: string;
    symbol: string;
    description: string;
  }>;
}

interface MetricsResponse {
  metrics: Record<string, string>;
}

interface HealthCheckResponse {
  message: string;
  status: string;
  version: string;
  environment: string;
  database: {
    database_type: string;
    database_name: string;
    connection_pool: string | object;
    status: string;
  };
  features: {
    real_time_data: boolean;
    ai_analysis: boolean;
    portfolio_tracking: boolean;
    authentication: string;
    database: string;
  };
  endpoints: {
    portfolio_summary: string;
    update_prices: string;
    accounts: string;
    assets: string;
    performance: string;
    docs: string;
  };
}

interface DetailedHealthResponse {
  status: string;
  timestamp: number;
  version: string;
  environment: string;
  checks: {
    database: string;
    api: string;
  };
}

interface ErrorResponse {
  error?: boolean;
  message?: string;
  detail?: string;
  status_code?: number;
  timestamp?: number;
}

// ============ API CONFIGURATION ============

const getApiBaseUrl = (): string => {
  const useCorsProxy = process.env.NEXT_PUBLIC_USE_CORS_PROXY === "true";

  if (useCorsProxy) return "/api/backend";
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

  const backendPort = process.env.NEXT_PUBLIC_BACKEND_PORT || "8000";
  const dockerBackendPort = process.env.NEXT_PUBLIC_DOCKER_BACKEND_PORT || "8080";

  if (process.env.NODE_ENV === "production") {
    return "https://api.yourdomain.com/api/v1";
  }

  const isDocker =
    process.env.DOCKER_ENV === "true" ||
    process.env.NEXT_PUBLIC_DOCKER_ENV === "true" ||
    (typeof window !== "undefined" && window.location.port === "3001");

  if (isDocker) return `http://localhost:${dockerBackendPort}/api/v1`;

  return `http://localhost:${backendPort}/api/v1`;
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 15000,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
  validateStatus: (status) => status < 500,
});

// ============ AUTH HELPER FUNCTION ============

async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    // For server-side requests
    if (typeof window === 'undefined') {
      const { auth } = await import('@clerk/nextjs/server');
      const { getToken } = await auth();
      const token = await getToken();

      return token ? {
        'Authorization': `Bearer ${token}`,
        'X-Clerk-Auth-Token': token
      } : {};
    }

    // For client-side requests, we'll return empty headers
    // and let components handle auth via useAuth hook
    return {};
  } catch (error) {
    console.warn('Failed to get auth token:', error);
    return {};
  }
}

// ============ INTERCEPTORS ============

api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Add auth headers
    const authHeaders = await getAuthHeaders();

    // Properly assign headers using Object.assign to avoid type issues
    Object.assign(config.headers, authHeaders);

    if (process.env.NODE_ENV === "development") {
      console.log("🌐 API Request:", config.method?.toUpperCase(), config.url);
      if (authHeaders.Authorization) {
        console.log("🔐 Auth: Token included");
      }
    }
    return config;
  },
  (error) => {
    console.error("❌ API Request Error:", error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === "development") {
      console.log("✅ API Response:", response.status, response.config.url);
      console.log("📊 Response data:", response.data);
    }
    return response;
  },
  (error) => {
    console.error("❌ API Response Error:", {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
      url: error.config?.url,
    });
    return Promise.reject(error);
  }
);

// ============ ERROR HANDLING ============

export class APIError extends Error {
  status?: number;
  detail?: string;
  timestamp?: number;

  constructor(message: string, status?: number, detail?: string, timestamp?: number) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.detail = detail;
    this.timestamp = timestamp;
  }
}

function handleApiError(error: unknown): APIError {
  if (axios.isAxiosError<ErrorResponse>(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    const status = axiosError.response?.status;
    const data = axiosError.response?.data;

    if (axiosError.code === "ECONNREFUSED" || axiosError.code === "ENOTFOUND") {
      return new APIError(
        `Unable to connect to server at ${API_BASE_URL}. Please ensure the backend is running.`,
        status
      );
    }

    if (axiosError.code === "ERR_NETWORK") {
      return new APIError(
        `Network error: Cannot connect to ${API_BASE_URL}. Please check your connection.`,
        status
      );
    }

    const message =
      data?.detail || data?.message || data?.error?.toString() || axiosError.message || "Network error occurred";

    return new APIError(message, status, data?.detail, data?.timestamp);
  }

  return new APIError(error instanceof Error ? error.message : "An unknown error occurred");
}

// ============ MAIN API OBJECT ============

export const portfolioAPI = {
  // Helper method to make authenticated requests from React components
  async makeAuthenticatedRequest<T>(
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    data?: unknown,
    token?: string
  ): Promise<T> {
    const headers: Record<string, string> = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      headers['X-Clerk-Auth-Token'] = token;
    }

    const config = {
      method,
      url,
      data,
      headers
    };

    try {
      const response = await api.request<T>(config);
      return response.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getAuthConfig(): Promise<AuthConfig> {
    try {
      const res = await api.get<AuthConfig>("/auth/config");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getUserProfile(token?: string): Promise<UserProfile> {
    if (token) {
      return this.makeAuthenticatedRequest<UserProfile>('get', '/auth/profile', undefined, token);
    }
    try {
      const res = await api.get<UserProfile>("/auth/profile");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async register(userData: RegisterRequest): Promise<User> {
    try {
      const res = await api.post<User>("/auth/register", userData);
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const res = await api.post<LoginResponse>("/auth/cookie/login", credentials);
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getAccounts(token?: string): Promise<Account[]> {
    if (token) {
      return this.makeAuthenticatedRequest<Account[]>('get', '/accounts/', undefined, token);
    }
    try {
      const res = await api.get<Account[]>("/accounts/");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async createAccount(accountData: AccountCreate, token?: string): Promise<Account> {
    if (token) {
      return this.makeAuthenticatedRequest<Account>('post', '/accounts/', accountData, token);
    }
    try {
      const res = await api.post<Account>("/accounts/", accountData);
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async addAsset(assetData: AssetCreate, token?: string): Promise<Asset> {
    if (token) {
      return this.makeAuthenticatedRequest<Asset>('post', '/assets/', assetData, token);
    }
    try {
      const res = await api.post<Asset>("/assets/", assetData);
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getPortfolioSummary(token?: string): Promise<PortfolioSummary> {
    if (token) {
      return this.makeAuthenticatedRequest<PortfolioSummary>('get', '/portfolio/summary', undefined, token);
    }
    try {
      const res = await api.get<PortfolioSummary>("/portfolio/summary");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async updatePrices(token?: string): Promise<UpdatePricesResponse> {
    if (token) {
      return this.makeAuthenticatedRequest<UpdatePricesResponse>('post', '/portfolio/update-prices', undefined, token);
    }
    try {
      const res = await api.post<UpdatePricesResponse>("/portfolio/update-prices");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getPortfoliosPerformance(token?: string): Promise<PerformancePortfolio[]> {
    if (token) {
      return this.makeAuthenticatedRequest<PerformancePortfolio[]>('get', '/portfolios/performance', undefined, token);
    }
    try {
      const res = await api.get<PerformancePortfolio[]>("/portfolios/performance");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getPortfolioPerformanceSummary(token?: string): Promise<PortfolioSummaryStats> {
    if (token) {
      return this.makeAuthenticatedRequest<PortfolioSummaryStats>('get', '/portfolios/performance/summary', undefined, token);
    }
    try {
      const res = await api.get<PortfolioSummaryStats>("/portfolios/performance/summary");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getPortfolioPerformance(portfolioId: string, token?: string): Promise<PerformancePortfolio> {
    if (token) {
      return this.makeAuthenticatedRequest<PerformancePortfolio>('get', `/portfolios/${portfolioId}/performance`, undefined, token);
    }
    try {
      const res = await api.get<PerformancePortfolio>(`/portfolios/${portfolioId}/performance`);
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getQuickAnalysis(symbols: string[], token?: string): Promise<QuickAnalysisResponse> {
    if (symbols.length > 20) throw new APIError("Maximum 20 symbols allowed");

    if (token) {
      return this.makeAuthenticatedRequest<QuickAnalysisResponse>('post', '/analysis/quick', { symbols }, token);
    }
    try {
      const res = await api.post<QuickAnalysisResponse>("/analysis/quick", { symbols });
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getAssetAnalysis(symbol: string, token?: string): Promise<AssetAnalysis> {
    if (token) {
      return this.makeAuthenticatedRequest<AssetAnalysis>('post', `/analysis/asset/${symbol}`, undefined, token);
    }
    try {
      const res = await api.post<AssetAnalysis>(`/analysis/asset/${symbol}`);
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getMarketStatus(): Promise<MarketStatus> {
    try {
      const res = await api.get<MarketStatus>("/market/status");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getBenchmarks(): Promise<BenchmarksResponse> {
    try {
      const res = await api.get<BenchmarksResponse>("/portfolios/performance/benchmarks");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async getPerformanceMetrics(): Promise<MetricsResponse> {
    try {
      const res = await api.get<MetricsResponse>("/portfolios/performance/metrics");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const res = await api.get<HealthCheckResponse>("/");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },

  async detailedHealthCheck(): Promise<DetailedHealthResponse> {
    try {
      const res = await api.get<DetailedHealthResponse>("/health");
      return res.data;
    } catch (e) {
      throw handleApiError(e);
    }
  },
};

// ============ CLERK AUTH TESTING ============

export const testClerkAuth = {
  async testAuthenticatedRequest() {
    try {
      console.log("🧪 Testing authenticated API request...");
      const response = await portfolioAPI.getUserProfile();
      console.log("✅ Authenticated request successful:", response);
      return true;
    } catch (error) {
      console.error("❌ Authenticated request failed:", error);
      return false;
    }
  },

  async testUnauthenticatedRequest() {
    try {
      console.log("🧪 Testing public API request...");
      const response = await portfolioAPI.healthCheck();
      console.log("✅ Public request successful:", response);
      return true;
    } catch (error) {
      console.error("❌ Public request failed:", error);
      return false;
    }
  }
};

// ============ TEST HARNESS ============

export const testAPI = {
  async testAllEndpoints() {
    console.log("🧪 Testing all API endpoints...\n");

    try {
      console.log("1. Auth Config...");
      console.log(await portfolioAPI.getAuthConfig());

      console.log("\n2. User Profile...");
      console.log(await portfolioAPI.getUserProfile());

      console.log("\n3. Accounts...");
      console.log(await portfolioAPI.getAccounts());

      console.log("\n4. Portfolio Summary...");
      console.log(await portfolioAPI.getPortfolioSummary());

      console.log("\n5. Portfolio Performance...");
      console.log(await portfolioAPI.getPortfoliosPerformance());

      console.log("\n6. Market Status...");
      console.log(await portfolioAPI.getMarketStatus());

      console.log("\n✅ All tests completed successfully!");
    } catch (e) {
      console.error("❌ Test failed:", e);
    }
  },
};

export default portfolioAPI;
