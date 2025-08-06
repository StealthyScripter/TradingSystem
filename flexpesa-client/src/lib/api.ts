import axios, { AxiosError } from 'axios';
import { PortfolioData, Account, Asset, APIResponse } from '@/types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-domain.com/api/v1'
  : 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to handle API errors
function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.message || 'An API error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

export const portfolioAPI = {
  async getPortfolioSummary(): Promise<APIResponse<PortfolioData>> {
    try {
      const response = await api.get<PortfolioData>('/portfolio/summary');
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
      const response = await api.post<{ updated_assets: number; total_assets: number }>('/portfolio/update-prices');
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
      const response = await api.get<Account[]>('/accounts/');
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
      const response = await api.post<Account>('/accounts/', accountData);
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
      const response = await api.post<Asset>('/assets/', assetData);
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
      const response = await api.post<{ analysis: Record<string, unknown> }>('/analysis/quick', symbols);
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
  }
};

export default api;
