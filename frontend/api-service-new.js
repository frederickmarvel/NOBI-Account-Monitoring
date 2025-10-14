// Simplified API Service - Calls Python Flask Backend
// All blockchain API logic is now handled server-side

class BlockchainAPIService {
  constructor() {
    // Auto-detect environment: local development vs production
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.protocol === 'file:';
    
    // Use local backend in development, relative path in production
    this.backendUrl = isDevelopment 
      ? 'http://localhost:8085/api'
      : window.location.origin + '/api';
    
    console.log(`API Backend: ${this.backendUrl}`);
    this.cache = new Map();
  }

  // Cache helper
  getCached(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < 60000) { // 60 second cache
      return cached.data;
    }
    return null;
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // Fetch with error handling
  async fetchAPI(endpoint) {
    try {
      const response = await fetch(endpoint);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'API request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Get complete analysis for an address
  async analyzeAddress(blockchain, address, startDate, endDate) {
    const cacheKey = `${blockchain}-${address}-${startDate}-${endDate}`;
    const cached = this.getCached(cacheKey);
    if (cached) {
      console.log('Using cached data');
      return cached;
    }

    const endpoint = `${this.backendUrl}/analyze/${blockchain}/${address}?start_date=${startDate}&end_date=${endDate}`;
    const data = await this.fetchAPI(endpoint);
    
    this.setCache(cacheKey, data);
    return data;
  }

  // Get balance only
  async getBalance(blockchain, address, startDate, endDate) {
    const endpoint = `${this.backendUrl}/balance/${blockchain}/${address}?start_date=${startDate}&end_date=${endDate}`;
    return await this.fetchAPI(endpoint);
  }

  // Get transactions only  
  async getTransactions(blockchain, address, startDate, endDate) {
    const endpoint = `${this.backendUrl}/transactions/${blockchain}/${address}?start_date=${startDate}&end_date=${endDate}`;
    return await this.fetchAPI(endpoint);
  }

  // Export PDF with USD/AED conversions
  async exportPDF(blockchain, address, startDate, endDate) {
    const endpoint = `${this.backendUrl}/export/pdf/${blockchain}/${address}?start_date=${startDate}&end_date=${endDate}`;
    
    try {
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        throw new Error(`Failed to generate PDF: ${response.statusText}`);
      }
      
      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'account_statement.pdf';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/);
        if (match) filename = match[1];
      }
      
      // Download the file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      return { success: true, filename };
    } catch (error) {
      console.error('PDF export error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.backendUrl}/health`);
      return await response.json();
    } catch (error) {
      console.error('Backend health check failed:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }
}

// Create global instance
const apiService = new BlockchainAPIService();
