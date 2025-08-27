import axios, { AxiosError } from 'axios';
import { PortfolioData, Account, Asset, APIResponse } from '@/types';

// API Base URL configuration for different environments
const getApiBaseUrl = (): string => {
  // In production, use environment variable
  if (process.env.NODE_ENV === 'production') {
    return process.env.NEXT_PUBLIC_API_URL || 'https://api.yourdomain.com/api/v1';
  }

  // In development, check for Docker environment
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Default for local development
  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

console.log('🔗 API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout for Docker startup
  headers: {
    'Content-Type': 'application/json',
  },
  // Retry configuration
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
      return 'Unable to connect to server. Please ensure the backend is running.';
    }

    if (axiosError.code === 'ECONNABORTED') {
      return 'Request timeout. The server is taking too long to respond.';
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

  async updatePrices(): Promise<APIResponse<{ updated_assets: number; total_assets: number }>> {
    try {
      const response = await retryRequest(
        () => api.post<{ updated_assets: number; total_assets: number }>('/portfolio/update-prices'),
        2, // Fewer retries for POST requests
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

  // Health check endpoint
  async healthCheck(): Promise<APIResponse<{ status: string }>> {
    try {
      const response = await api.get<{ status: string }>('/');
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: handleApiError(error)
      };
    }
  }
};

export default api;
