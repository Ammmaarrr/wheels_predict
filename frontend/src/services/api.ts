/**
 * API service for communicating with the FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout to 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle network errors specifically
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (!error.response) {
      console.error('Network error - backend may be down');
    }
    
    return Promise.reject(error);
  }
);

// Types
export interface PriceRequest {
  make: string;
  model: string;
  year: number;
  mileage?: number;
  engine_capacity: number;
  transmission: string;
  location: string;
  variant?: string;
}

export interface EnhancedPriceResponse {
  predicted_price: number;
  confidence: number;
  price_range: {
    min: number;
    max: number;
    predicted: number;
  };
  model_info: {
    model_type: string;
    features_used: string;
    data_quality: string;
  };
}

export interface RecommendationRequest {
  budget: number;
  preferences?: Record<string, any>;
  location?: string;
  max_results?: number;
}

export interface EnhancedRecommendationResponse {
  recommendations: Array<{
    make: string;
    model: string;
    year: number;
    variant: string;
    engine_capacity: number;
    transmission: string;
    price: number;
    score: number;
    match_reason: string;
  }>;
  total_found: number;
  search_criteria: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface MonitoringMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  drift_score: number;
  prediction_count: number;
  error_rate: number;
  response_time: number;
}

export interface Alert {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  timestamp: string;
}

// API functions
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // System status
  async getSystemStatus() {
    const response = await api.get('/monitoring/status');
    return response.data;
  },

  // Enhanced price prediction
  async predictPrice(request: PriceRequest): Promise<EnhancedPriceResponse> {
    console.log('Making enhanced price prediction request:', request);
    console.log('API Base URL:', API_BASE_URL);
    
    try {
      const response = await api.post('/predict', request);
      console.log('Enhanced price prediction response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Enhanced price prediction error:', error);
      throw error;
    }
  },

  // Enhanced recommendations
  async getRecommendations(request: RecommendationRequest): Promise<EnhancedRecommendationResponse> {
    try {
      console.log('Making enhanced recommendations request:', request);
      console.log('API Base URL:', API_BASE_URL);
      
      // Use POST endpoint for enhanced recommendations
      const response = await api.post('/recommendations', request);
      
      console.log('Enhanced recommendations response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Enhanced recommendations API error:', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
      } else if (error.request) {
        console.error('Error request:', error.request);
      } else {
        console.error('Error message:', error.message);
      }
      throw error;
    }
  },

  // Budget-based recommendations (legacy GET endpoint)
  async getRecommendationsByBudget(params: {
    budget: number;
    car_type?: string;
    transmission?: string;
    min_year?: number;
    max_year?: number;
    make?: string;
  }) {
    try {
      console.log('Making budget recommendations request:', params);
      
      const response = await api.get('/recommendations', { params });
      
      console.log('Budget recommendations response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Budget recommendations error:', error);
      throw error;
    }
  },

  // Chat
  async sendChatMessage(request: ChatRequest) {
    const response = await api.post('/chat', request);
    return response.data;
  },

  // Monitoring
  async getMonitoringMetrics(): Promise<MonitoringMetrics> {
    const response = await api.get('/monitoring/metrics');
    return response.data;
  },

  async getPerformanceMetrics() {
    const response = await api.get('/monitoring/metrics');
    return response.data;
  },

  async getAlerts(): Promise<{ alerts: Alert[]; count: number }> {
    const response = await api.get('/monitoring/alerts');
    return response.data;
  },

  async triggerRetrain(force: boolean = false, models?: string[]) {
    const response = await api.post('/api/v1/monitoring/retrain', {
      force,
      models,
    });
    return response.data;
  },

  // Data
  async getDataStats() {
    const response = await api.get('/api/v1/data/stats');
    return response.data;
  },

  async getRecentData(limit: number = 100) {
    const response = await api.get(`/api/v1/data/recent?limit=${limit}`);
    return response.data;
  },

  // Enhanced dashboard stats
  async getDashboardStats() {
    try {
      console.log('Getting enhanced dashboard stats');
      
      const response = await api.get('/dashboard/stats');
      console.log('Enhanced dashboard stats:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Enhanced dashboard stats error:', error);
      throw error;
    }
  },

  // Model retraining
  async retrainModels() {
    try {
      console.log('Triggering model retraining');
      
      const response = await api.post('/admin/retrain-models');
      console.log('Model retraining response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Model retraining error:', error);
      throw error;
    }
  },
};

export default apiService;
