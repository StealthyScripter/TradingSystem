import axios from 'axios';

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

// API Functions
export const portfolioAPI = {
  // Get complete portfolio summary - MAIN ENDPOINT
  async getPortfolioSummary() {
    try {
      const response = await api.get('/portfolio/summary');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching portfolio summary:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // Update prices for all assets
  async updatePrices() {
    try {
      const response = await api.post('/portfolio/update-prices');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error updating prices:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // Get all accounts
  async getAccounts() {
    try {
      const response = await api.get('/accounts/');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching accounts:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // Create new account
  async createAccount(accountData) {
    try {
      const response = await api.post('/accounts/', accountData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error creating account:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // Add new asset
  async addAsset(assetData) {
    try {
      const response = await api.post('/assets/', assetData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error adding asset:', error);
      return {
        success: false,
        error: error.message
      };
    }
  },

  // Quick AI analysis
  async getQuickAnalysis(symbols) {
    try {
      const response = await api.post('/analysis/quick', symbols);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error getting analysis:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export default api;
