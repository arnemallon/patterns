import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);

    if (error.response) {
      // Server responded with an error status
      // We'll throw a new error object with more details
      throw {
        status: error.response.status,
        message: error.response.data?.error || 'Server Error',
        details: error.response.data?.details || 'An unexpected error occurred on the server.'
      };
    } else if (error.request) {
      // The request was made but no response was received
      throw { message: 'Network Error', details: 'No response from server. Please check your connection and ensure the backend is running.' };
    } else {
      // Something happened in setting up the request that triggered an Error
      throw { message: 'Request Failed', details: error.message };
    }
  }
);

export const apiService = {
  async get(endpoint, params = {}) {
    try {
      const response = await api.get(endpoint, { params });
      return response.data;
    } catch (error) {
      console.error('API GET Error:', error.response || error.message);
      throw {
        message: error.response?.data?.error || 'Network Error',
        details: error.response?.data?.details || 'Could not connect to the API server.'
      };
    }
  },

  async post(endpoint, data = {}) {
    try {
      const response = await api.post(endpoint, data);
      return response.data;
    } catch (error) {
      console.error('API POST Error:', error.response || error.message);
      throw {
        message: error.response?.data?.error || 'Request Failed',
        details: error.response?.data?.details || 'The server could not process the request.'
      };
    }
  },

  /**
   * Classify a Bitcoin address
   * @param {string} address - Bitcoin address to classify
   * @returns {Promise<Object>} Classification result
   */
  async classifyAddress(address) {
    return this.post('/classify', { address });
  },

  /**
   * Get classification history
   * @param {number} limit - Number of records to return
   * @param {number} offset - Number of records to skip
   * @returns {Promise<Object>} History data
   */
  async getHistory(limit = 10, offset = 0) {
    return this.get(`/history?limit=${limit}&offset=${offset}`);
  },

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get transaction graph data for an address
   * @param {string} address - Bitcoin address to get graph data for
   * @returns {Promise<Object>} Graph data with nodes and edges
   */
  async getTransactionGraph(address) {
    return this.get(`/graph/${address}`);
  },

  /**
   * Get dashboard statistics
   * @returns {Promise<Object>} Statistics data including total addresses, suspicious addresses, etc.
   */
  async getStatistics() {
    return this.get('/stats');
  },

  /**
   * Get category distribution for bar chart
   * @returns {Promise<Object>} Category distribution data
   */
  async getCategoryDistribution() {
    return this.get('/category-distribution');
  },

  /**
   * Get address count over time (last 30 days)
   * @returns {Promise<Object>} Date-to-count mapping
   */
  async getAddressCountOverTime() {
    return this.get('/address-count-over-time');
  }
}; 