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
   * Classify multiple Bitcoin addresses in batch
   * @param {Array<string>} addresses - Array of Bitcoin addresses to classify
   * @returns {Promise<Object>} Batch classification results
   */
  async batchClassifyAddresses(addresses) {
    return this.post('/batch-classify', { addresses });
  },

  /**
   * Get classification history
   * @param {number} limit - Number of records to return
   * @param {number} offset - Number of records to skip
   * @param {Object} filters - Optional filters
   * @param {string} filters.search - Search term for addresses
   * @param {string} filters.classification - Filter by classification ('0' or '1')
   * @param {string} filters.dateRange - Filter by date range ('today', 'week', 'month', 'year')
   * @returns {Promise<Object>} History data
   */
  async getHistory(limit = 10, offset = 0, filters = {}) {
    const params = { limit, offset };
    
    if (filters.search) params.search = filters.search;
    if (filters.classification) params.classification = filters.classification;
    if (filters.dateRange) params.date_range = filters.dateRange;
    
    return this.get('/history', params);
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
  },

  /**
   * Test single address classification
   * @param {string} address - Bitcoin address to test
   * @returns {Promise<Object>} Test result with features and prediction
   */
  async testClassify(address) {
    return this.post('/test-classify', { address });
  },

  /**
   * Check API health status
   * @returns {Promise<Object>} Health status and service availability
   */
  async healthCheck() {
    return this.get('/health');
  }
}; 

// Alerts API helpers
export const alertsApi = {
  async list() {
    return api.get('/alerts').then(r => r.data);
  },
  async getTriggered() {
    return api.get('/alerts/triggered').then(r => r.data);
  },
  async create({ address, type, threshold, email }) {
    return api.post('/alerts', { address, type, threshold, email }).then(r => r.data);
  },
  async toggle(alertId) {
    return api.post(`/alerts/${alertId}/toggle`).then(r => r.data);
  },
  async remove(alertId) {
    return api.delete(`/alerts/${alertId}`).then(r => r.data);
  }
};

// Users API helpers
export const usersApi = {
  async getProfile() {
    return api.get('/users/profile').then(r => r.data);
  },
  async updateProfile(profileData) {
    return api.put('/users/profile', profileData).then(r => r.data);
  },
  async getPreferences() {
    return api.get('/users/preferences').then(r => r.data);
  },
  async updatePreferences(preferencesData) {
    return api.put('/users/preferences', preferencesData).then(r => r.data);
  },
  async getNotifications() {
    return api.get('/users/notifications').then(r => r.data);
  },
  async updateNotifications(notificationData) {
    return api.put('/users/notifications', notificationData).then(r => r.data);
  },
  async changePassword(passwordData) {
    return api.post('/users/change-password', passwordData).then(r => r.data);
  },
  async getActivity() {
    return api.get('/users/activity').then(r => r.data);
  },
  async getStats() {
    return api.get('/users/stats').then(r => r.data);
  },
  async exportData() {
    return api.post('/users/export-data').then(r => r.data);
  }
};

// Cases API helpers
export const casesApi = {
  async list(filters = {}) {
    return api.get('/cases', { params: filters }).then(r => r.data);
  },
  async get(id) {
    return api.get(`/cases/${id}`).then(r => r.data);
  },
  async create(caseData) {
    return api.post('/cases', caseData).then(r => r.data);
  },
  async update(id, caseData) {
    return api.put(`/cases/${id}`, caseData).then(r => r.data);
  },
  async delete(id) {
    return api.delete(`/cases/${id}`).then(r => r.data);
  },
  async addAddress(caseId, addressData) {
    return api.post(`/cases/${caseId}/addresses`, addressData).then(r => r.data);
  },

  async addAddressesBulk(caseId, addresses) {
    return api.post(`/cases/${caseId}/addresses/bulk`, { addresses }).then(r => r.data);
  },
  async removeAddress(caseId, addressId) {
    return api.delete(`/cases/${caseId}/addresses/${addressId}`).then(r => r.data);
  },
  async updateAddress(caseId, addressId, addressData) {
    return api.put(`/cases/${caseId}/addresses/${addressId}`, addressData).then(r => r.data);
  },

  async refreshAddressClassification(caseId, addressId) {
    return api.post(`/cases/${caseId}/addresses/${addressId}/refresh`).then(r => r.data);
  },
  async export(caseId) {
    return api.post(`/cases/${caseId}/export`).then(r => r.data);
  },
  async getStats() {
    return api.get('/cases/stats').then(r => r.data);
  }
};