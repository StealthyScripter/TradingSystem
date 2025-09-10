import axios, { AxiosError } from 'axios';
import {
  Account,
  Asset,
  PortfolioSummary,
  PerformancePortfolio,
  PortfolioSummaryStats,
  HoldingCreate,
  HoldingResponse,
  PortfolioCreate,
  LoginRequest,
  RegisterRequest,
  User,
  UserProfile,
  AuthConfig,
  MarketStatus,
  AssetAnalysis,
  AccountCreateRequest,
  AssetCreateRequest
} from '@/types';

// ============ API CONFIGURATION ============

const getApiBaseUrl = (): string => {
  // Check for CORS bypass mode
  const useCorsProxy = process.env.NEXT_PUBLIC_USE_CORS_PROXY === 'true';

  if (useCorsProxy) {
    // Use Next.js proxy to bypass CORS during development
    const proxyUrl = '/api/backend';
    console.log('🔧 Using CORS proxy:', proxyUrl);
    return proxyUrl;
  }

  if (process.env.NEXT_PUBLIC_API_URL) {
    console.log('🔗 Using API URL from NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
    return process.env.NEXT_PUBLIC_API_URL;
  }

  const backendPort = process.env.NEXT_PUBLIC_BACKEND_PORT || '8000';
  const dockerBackendPort = process.env.NEXT_PUBLIC_DOCKER_BACKEND_PORT || '8080';

  if (process.env.NODE_ENV === 'production') {
    console.warn('⚠️ Production environment without NEXT_PUBLIC_API_URL, using fallback');
    return 'https://api.yourdomain.com/api/v1';
  }

  const isDocker = process.env.DOCKER_ENV === 'true' ||
                   process.env.NEXT_PUBLIC_DOCKER_ENV === 'true' ||
                   (typeof window !== 'undefined' && window.location.port === '3001');

  if (isDocker) {
    const dockerUrl = `http://localhost:${dockerBackendPort}/api/v1`;
    console.log('🐳 Docker environment detected, using:', dockerUrl);
    return dockerUrl;
  }

  const nativeUrl = `http://localhost:${backendPort}/api/v1`;
  console.log('🔧 Native development environment, using:', nativeUrl);
  return nativeUrl;
};

const API_BASE_URL = getApiBaseUrl();
console.log('🔗 API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '15000'),
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  validateStatus: status => status < 500,
});

// ============ REQUEST/RESPONSE INTERCEPTORS ============

api.interceptors.request.use(
  (config) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🌐 API Request:', config.method?.toUpperCase(), config.url);
    }

    // Add CORS headers for development
    config.headers?.set?.('Access-Control-Allow-Origin', '*');
    config.headers?.set?.('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    config.headers?.set?.('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('✅ API Response:', response.status, response.config.url);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    console.error('❌ API Response Error:', {
      status: error.response?.status,
      code: error.code,
      url: error.config?.url,
      message: error.message,
    });

    // Handle CORS / Network error
    if (error.code === 'ERR_NETWORK' || error.message.includes('CORS')) {
      console.warn('🚫 CORS or Network issue detected. Backend may be offline or misconfigured.');

      if (!originalRequest._corsRetry && originalRequest.baseURL?.includes('localhost')) {
        originalRequest._corsRetry = true;
        const fallbackUrl = originalRequest.baseURL.replace('localhost', '127.0.0.1');
        console.log('🔁 Retrying with fallback URL:', fallbackUrl);
        originalRequest.baseURL = fallbackUrl;
        return api(originalRequest);
      }
    }

    return Promise.reject({
      ...error,
      friendlyMessage: handleApiError(error),
    });
  }
);

// ============ ERROR HANDLING ============

interface ErrorResponse {
  detail?: string;
  message?: string;
  error?: string;
}

function hasFriendlyMessage(error: unknown): error is { friendlyMessage: string } {
  return typeof error === 'object' && error !== null && 'friendlyMessage' in error;
}

function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;

    if (hasFriendlyMessage(axiosError)) {
      return axiosError.friendlyMessage;
    }

    if (axiosError.code === 'ECONNREFUSED' || axiosError.code === 'ENOTFOUND') {
      return `Unable to connect to server at ${API_BASE_URL}. Please ensure the backend is running.`;
    }

    if (axiosError.code === 'ECONNABORTED') {
      return `Request timeout. The server at ${API_BASE_URL} is taking too long to respond.`;
    }

    if (axiosError.code === 'ERR_NETWORK' || axiosError.message.includes('CORS')) {
      return `CORS Error: Cannot connect to ${API_BASE_URL}. Please check backend or CORS setup.`;
    }

    if (axiosError.response?.status === 502 || axiosError.response?.status === 503) {
      return 'Server is temporarily unavailable. Please try again later.';
    }

    const data = axiosError.response?.data;
    return data?.detail || data?.message || data?.error || axiosError.message || 'Network error occurred';
  }

  return error instanceof Error ? error.message : 'An unknown error occurred';
}

// ============ RETRY HELPER ============

async function retryRequest<T>(
  requestFn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }

      // Don't retry on client errors (4xx)
      if (axios.isAxiosError(error) && error.response?.status && error.response.status < 500) {
        throw error;
      }

      console.warn(`🔄 Request failed (attempt ${attempt}/${maxRetries}), retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2; // Exponential backoff
    }
  }

  throw new Error('Max retries exceeded');
}

// ============ API CONFIGURATION INFO ============

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: api.defaults.timeout,
  environment: process.env.NODE_ENV,
  isDocker: process.env.DOCKER_ENV === 'true',
};

// ============ MAIN API OBJECT ============

export const portfolioAPI = {
  // ============ AUTHENTICATION ============

  async getAuthConfig(): Promise<AuthConfig> {
    try {
      const response = await api.get<AuthConfig>('/auth/config');
      return response.data;
    } catch (error: unknown) {
      console.error('Error getting auth config:', error);
      throw new Error(handleApiError(error));
    }
  },

  async getUserProfile(): Promise<UserProfile> {
    try {
      const response = await retryRequest(
        () => api.get<UserProfile>('/auth/profile'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error getting user profile:', error);
      throw new Error(handleApiError(error));
    }
  },

  async login(credentials: LoginRequest): Promise<{ user: User }> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await api.post<{ user: User }>('/auth/cookie/login', formData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async register(userData: RegisterRequest): Promise<User> {
    try {
      const response = await api.post<User>('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/cookie/logout');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>('/users/me');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // ============ CORE PORTFOLIO ============

  async getPortfolioSummary(): Promise<PortfolioSummary> {
    try {
      const response = await retryRequest(
        () => api.get<PortfolioSummary>('/portfolio/summary'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching portfolio summary:', error);
      throw new Error(handleApiError(error));
    }
  },

  async updatePrices(): Promise<{ updated_assets: number; total_assets: number; duration: number; timestamp: string }> {
    try {
      const response = await retryRequest(
        () => api.post<{ updated_assets: number; total_assets: number; duration: number; timestamp: string }>('/portfolio/update-prices'),
        2,
        2000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error updating prices:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ ACCOUNTS ============

  async getAccounts(): Promise<Account[]> {
    try {
      const response = await retryRequest(
        () => api.get<Account[]>('/accounts/'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching accounts:', error);
      throw new Error(handleApiError(error));
    }
  },

  async createAccount(accountData: AccountCreateRequest): Promise<Account> {
    try {
      const response = await retryRequest(
        () => api.post<Account>('/accounts/', accountData),
        2,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error creating account:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ ASSETS ============

  async addAsset(assetData: AssetCreateRequest): Promise<Asset> {
    try {
      const response = await retryRequest(
        () => api.post<Asset>('/assets/', assetData),
        2,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error adding asset:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ MARKET DATA ============

  async getMarketStatus(): Promise<MarketStatus> {
    try {
      const response = await api.get<MarketStatus>('/market/status');
      return response.data;
    } catch (error: unknown) {
      console.error('Error getting market status:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ AI ANALYSIS ============

  async getQuickAnalysis(symbols: string[]): Promise<{ analysis: Record<string, unknown> }> {
    try {
      if (symbols.length > 20) {
        throw new Error('Maximum 20 symbols allowed for quick analysis');
      }

      const response = await retryRequest(
        () => api.post<{ analysis: Record<string, unknown> }>('/analysis/quick', symbols),
        2,
        2000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error getting analysis:', error);
      throw new Error(handleApiError(error));
    }
  },

  async getAssetAnalysis(symbol: string): Promise<AssetAnalysis> {
    try {
      const response = await retryRequest(
        () => api.post<AssetAnalysis>(`/analysis/asset/${symbol}`),
        2,
        2000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error getting asset analysis:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ PORTFOLIO PERFORMANCE ============

  async getAllPortfolioPerformance(): Promise<PerformancePortfolio[]> {
    try {
      const response = await retryRequest(
        () => api.get<PerformancePortfolio[]>('/portfolios/performance'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching portfolio performance:', error);
      throw new Error(handleApiError(error));
    }
  },

  async getPortfolioPerformanceSummary(): Promise<PortfolioSummaryStats> {
    try {
      const response = await retryRequest(
        () => api.get<PortfolioSummaryStats>('/portfolios/performance/summary'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching portfolio performance summary:', error);
      throw new Error(handleApiError(error));
    }
  },

  async getPortfolioPerformance(portfolioId: string): Promise<PerformancePortfolio> {
    try {
      const response = await retryRequest(
        () => api.get<PerformancePortfolio>(`/portfolios/${portfolioId}/performance`),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching single portfolio performance:', error);
      throw new Error(handleApiError(error));
    }
  },

  async createPortfolioWithPerformance(portfolioData: PortfolioCreate): Promise<PerformancePortfolio> {
    try {
      const response = await retryRequest(
        () => api.post<PerformancePortfolio>('/portfolios/', portfolioData),
        2,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error creating portfolio:', error);
      throw new Error(handleApiError(error));
    }
  },

  async updatePortfolio(portfolioId: string, updateData: { name?: string; type?: string; expense_ratio?: number }): Promise<PerformancePortfolio> {
    try {
      const response = await retryRequest(
        () => api.put<PerformancePortfolio>(`/portfolios/${portfolioId}/performance`, updateData),
        2,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error updating portfolio:', error);
      throw new Error(handleApiError(error));
    }
  },

  async deletePortfolio(portfolioId: string): Promise<void> {
    try {
      await retryRequest(
        () => api.delete(`/portfolios/${portfolioId}/performance`),
        2,
        1000
      );
    } catch (error: unknown) {
      console.error('Error deleting portfolio:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ PORTFOLIO HOLDINGS ============

  async getPortfolioHoldings(portfolioId: string): Promise<HoldingResponse[]> {
    try {
      const response = await retryRequest(
        () => api.get<HoldingResponse[]>(`/portfolios/${portfolioId}/holdings`),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching portfolio holdings:', error);
      throw new Error(handleApiError(error));
    }
  },

  async addHoldingsToPortfolio(portfolioId: string, holdings: HoldingCreate[]): Promise<{ message: string }> {
    try {
      const response = await retryRequest(
        () => api.post<{ message: string }>(`/portfolios/${portfolioId}/holdings`, holdings),
        2,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error adding holdings:', error);
      throw new Error(handleApiError(error));
    }
  },

  async updateDailyData(portfolioId: string, priceData: { date: string; holdings_prices: Record<string, number> }): Promise<{ message: string; result: unknown }> {
    try {
      const response = await retryRequest(
        () => api.post<{ message: string; result: unknown }>(`/portfolios/${portfolioId}/daily-data`, priceData),
        2,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error updating daily data:', error);
      throw new Error(handleApiError(error));
    }
  },

  async recalculatePerformance(portfolioId: string): Promise<PerformancePortfolio> {
    try {
      const response = await retryRequest(
        () => api.post<{ message: string; result: PerformancePortfolio }>(`/portfolios/${portfolioId}/recalculate`),
        2,
        2000
      );
      return response.data.result;
    } catch (error: unknown) {
      console.error('Error recalculating performance:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ UTILITY ENDPOINTS ============

  async getAvailableBenchmarks(): Promise<{ benchmarks: Array<{ name: string; symbol: string; description: string }> }> {
    try {
      const response = await retryRequest(
        () => api.get<{ benchmarks: Array<{ name: string; symbol: string; description: string }> }>('/portfolios/performance/benchmarks'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching benchmarks:', error);
      throw new Error(handleApiError(error));
    }
  },

  async getAvailableMetrics(): Promise<{ metrics: Record<string, string> }> {
    try {
      const response = await retryRequest(
        () => api.get<{ metrics: Record<string, string> }>('/portfolios/performance/metrics'),
        3,
        1000
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Error fetching metrics:', error);
      throw new Error(handleApiError(error));
    }
  },

  // ============ HEALTH CHECK ============

  async healthCheck(): Promise<{ status: string; config: typeof apiConfig }> {
    try {
      const response = await api.get<{ status: string }>('/');
      return {
        ...response.data,
        config: apiConfig
      };
    } catch (error: unknown) {
      throw new Error(handleApiError(error));
    }
  },

  async detailedHealthCheck(): Promise<unknown> {
    try {
      const response = await api.get('/health/detailed');
      return response.data;
    } catch (error: unknown) {
      throw new Error(handleApiError(error));
    }
  },
};

export default api;
