import axios, { AxiosError } from 'axios';
import { PortfolioData, Account, Asset, APIResponse, PerformancePortfolio, PortfolioSummary, HoldingCreate, PortfolioCreate, HoldingResponse, LoginRequest, RegisterRequest, User } from '@/types';

// API Base URL configuration for different environments
const getApiBaseUrl = (): string => {
  // Priority 1: Explicit NEXT_PUBLIC_API_URL from environment
  if (process.env.NEXT_PUBLIC_API_URL) {
    console.log('🔗 Using API URL from NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Priority 2: Build API URL from port environment variables
  const backendPort = process.env.NEXT_PUBLIC_BACKEND_PORT || '8000';
  const dockerBackendPort = process.env.NEXT_PUBLIC_DOCKER_BACKEND_PORT || '8080';

  // Priority 3: Environment-specific defaults
  if (process.env.NODE_ENV === 'production') {
    // Production should always have NEXT_PUBLIC_API_URL set
    console.warn('⚠️ Production environment without NEXT_PUBLIC_API_URL, using fallback');
    return 'https://api.yourdomain.com/api/v1';
  }

  // Priority 4: Check if we're in a Docker environment
  const isDocker = process.env.DOCKER_ENV === 'true' ||
                   process.env.NEXT_PUBLIC_DOCKER_ENV === 'true' ||
                   typeof window !== 'undefined' && window.location.port === '3001'; // Docker often shifts frontend port

  if (isDocker) {
    const dockerUrl = `http://localhost:${dockerBackendPort}/api/v1`;
    console.log('🐳 Docker environment detected, using:', dockerUrl);
    return dockerUrl;
  }

  // Priority 5: Default for local development (native backend)
  const nativeUrl = `http://localhost:${backendPort}/api/v1`;
  console.log('🔧 Native development environment, using:', nativeUrl);
  return nativeUrl;
};

//Get the API base URl
const API_BASE_URL = getApiBaseUrl();

console.log('🔗 API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '15000'),
  headers: {
    'Content-Type': 'application/json',
  },
  // Retry configuration
  withCredentials:true,
  validateStatus: (status) => status < 500, // Don't retry on client errors
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🌐 API Request:', config.method?.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('✅ API Response:', response.status, response.config.url);
    }
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

// Define error response type
interface ErrorResponse {
  detail?: string;
  message?: string;
  error?: string;
}

// Helper function to handle API errors with retry logic
function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;

    if (axiosError.code === 'ECONNREFUSED' || axiosError.code === 'ENOTFOUND') {
      return `Unable to connect to server at ${API_BASE_URL}. Please ensure the backend is running.`;
    }

    if (axiosError.code === 'ECONNABORTED') {
      return `Request timeout. The server at ${API_BASE_URL} is taking too long to respond.`;
    }

    if (axiosError.response?.status === 502 || axiosError.response?.status === 503) {
      return 'Server is temporarily unavailable. Please try again in a moment.';
    }

    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }

    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }

    return axiosError.message || 'Network error occurred';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unknown error occurred';
}

// Retry helper for failed requests
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

// Export API configuration for debugging
export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: api.defaults.timeout,
  environment: process.env.NODE_ENV,
  isDocker: process.env.DOCKER_ENV === 'true',
};

export const portfolioAPI = {
  async getPortfolioSummary(): Promise<APIResponse<PortfolioData>> {
    try {
      const response = await retryRequest(
        () => api.get<PortfolioData>('/portfolio/summary'),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching portfolio summary:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  async getAccounts(): Promise<APIResponse<Account[]>> {
    try {
      const response = await retryRequest(
        () => api.get<Account[]>('/accounts/'),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching accounts:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  async createAccount(accountData: Partial<Account>): Promise<APIResponse<Account>> {
    try {
      const response = await retryRequest(
        () => api.post<Account>('/accounts/', accountData),
        2,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error creating account:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  async addAsset(assetData: Partial<Asset>): Promise<APIResponse<Asset>> {
    try {
      const response = await retryRequest(
        () => api.post<Asset>('/assets/', assetData),
        2,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error adding asset:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  async getQuickAnalysis(symbols: string[]): Promise<APIResponse<{ analysis: Record<string, unknown> }>> {
    try {
      const response = await retryRequest(
        () => api.post<{ analysis: Record<string, unknown> }>('/analysis/quick', symbols),
        2,
        2000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error getting analysis:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  async getAllPortfolioPerformance(): Promise<APIResponse<PerformancePortfolio[]>> {
    try {
      const response = await retryRequest(
        () => api.get<PerformancePortfolio[]>('/portfolios/performance'),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching portfolio performance:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Get portfolio performance summary
  async getPortfolioPerformanceSummary(): Promise<APIResponse<PortfolioSummary>> {
    try {
      const response = await retryRequest(
        () => api.get<PortfolioSummary>('/portfolios/performance/summary'),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching portfolio performance summary:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Get specific portfolio performance
  async getPortfolioPerformance(portfolioId: string): Promise<APIResponse<PerformancePortfolio>> {
    try {
      const response = await retryRequest(
        () => api.get<PerformancePortfolio>(`/portfolios/${portfolioId}/performance`),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching single portfolio performance:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Create new portfolio with performance tracking
  async createPortfolioWithPerformance(portfolioData: PortfolioCreate): Promise<APIResponse<PerformancePortfolio>> {
    try {
      const response = await retryRequest(
        () => api.post<PerformancePortfolio>('/portfolios/', portfolioData),
        2,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error creating portfolio:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Update portfolio
  async updatePortfolio(portfolioId: string, updateData: { name?: string; type?: string; expense_ratio?: number }): Promise<APIResponse<PerformancePortfolio>> {
    try {
      const response = await retryRequest(
        () => api.put<PerformancePortfolio>(`/portfolios/${portfolioId}/performance`, updateData),
        2,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error updating portfolio:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Delete portfolio
  async deletePortfolio(portfolioId: string): Promise<APIResponse<void>> {
    try {
      await retryRequest(
        () => api.delete(`/portfolios/${portfolioId}/performance`),
        2,
        1000
      );

      return {
        success: true,
        data: undefined
      };
    } catch (error: unknown) {
      console.error('Error deleting portfolio:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Get portfolio holdings with performance
  async getPortfolioHoldings(portfolioId: string): Promise<APIResponse<HoldingResponse[]>> {
    try {
      const response = await retryRequest(
        () => api.get<HoldingResponse[]>(`/portfolios/${portfolioId}/holdings`),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching portfolio holdings:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Add holdings to portfolio
  async addHoldingsToPortfolio(portfolioId: string, holdings: HoldingCreate[]): Promise<APIResponse<{ message: string }>> {
    try {
      const response = await retryRequest(
        () => api.post<{ message: string }>(`/portfolios/${portfolioId}/holdings`, holdings),
        2,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error adding holdings:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Update daily price data
  async updateDailyData(portfolioId: string, priceData: { date: string; holdings_prices: Record<string, number> }): Promise<APIResponse<{ message: string; result: unknown }>> {
    try {
      const response = await retryRequest(
        () => api.post<{ message: string; result: unknown }>(`/portfolios/${portfolioId}/daily-data`, priceData),
        2,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error updating daily data:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Recalculate portfolio performance
  async recalculatePerformance(portfolioId: string): Promise<APIResponse<PerformancePortfolio>> {
    try {
      const response = await retryRequest(
        () => api.post<{ message: string; result: PerformancePortfolio }>(`/portfolios/${portfolioId}/recalculate`),
        2,
        2000
      );

      return {
        success: true,
        data: response.data.result
      };
    } catch (error: unknown) {
      console.error('Error recalculating performance:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Get available benchmarks
  async getAvailableBenchmarks(): Promise<APIResponse<{ benchmarks: Array<{ name: string; symbol: string; description: string }> }>> {
    try {
      const response = await retryRequest(
        () => api.get<{ benchmarks: Array<{ name: string; symbol: string; description: string }> }>('/portfolios/performance/benchmarks'),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching benchmarks:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // Get available metrics
  async getAvailableMetrics(): Promise<APIResponse<{ metrics: Record<string, string> }>> {
    try {
      const response = await retryRequest(
        () => api.get<{ metrics: Record<string, string> }>('/portfolios/performance/metrics'),
        3,
        1000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error fetching metrics:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  async login(credentials: LoginRequest): Promise<APIResponse<{ user: User }>> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await api.post<{ user: User }>('/auth/cookie/login', formData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: handleApiError(error) };
    }
  },

  async register(userData: RegisterRequest): Promise<APIResponse<User>> {
    try {
      const response = await api.post<User>('/auth/register', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: handleApiError(error) };
    }
  },

  async logout(): Promise<APIResponse<void>> {
    try {
      await api.post('/auth/cookie/logout');
      return { success: true, data: undefined };
    } catch (error) {
      return { success: false, error: handleApiError(error) };
    }
  },

  async getCurrentUser(): Promise<APIResponse<User>> {
    try {
      const response = await api.get<User>('/users/me');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: handleApiError(error) };
    }
  },

  // Health check endpoint with API config info
  async healthCheck(): Promise<APIResponse<{ status: string; config: typeof apiConfig }>> {
    try {
      const response = await api.get<{ status: string }>('/');
      return {
        success: true,
        data: {
          ...response.data,
          config: apiConfig
        }
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

  // ... rest of your existing API methods remain the same ...
  async updatePrices(): Promise<APIResponse<{ updated_assets: number; total_assets: number }>> {
    try {
      const response = await retryRequest(
        () => api.post<{ updated_assets: number; total_assets: number }>('/portfolio/update-prices'),
        2,
        2000
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      console.error('Error updating prices:', error);
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  },

};

export default api;
