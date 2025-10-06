import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  logout: () => api.post('/api/auth/logout'),
  getProfile: () => api.get('/api/auth/profile'),
};

// Signals endpoints
export const signalsAPI = {
  getAll: (params) => api.get('/api/signals', { params }),
  getById: (id) => api.get(`/api/signals/${id}`),
  approve: (id) => api.post(`/api/signals/${id}/approve`),
  reject: (id) => api.post(`/api/signals/${id}/reject`),
};

// Positions endpoints
export const positionsAPI = {
  getAll: (params) => api.get('/api/positions', { params }),
  getById: (id) => api.get(`/api/positions/${id}`),
  close: (id, data) => api.post(`/api/positions/${id}/close`, data),
  getHistory: (params) => api.get('/api/positions/history', { params }),
};

// Analytics endpoints
export const analyticsAPI = {
  getPerformance: (params) => api.get('/api/analytics/performance', { params }),
  getMetrics: () => api.get('/api/analytics/metrics'),
  getEquityCurve: (params) => api.get('/api/analytics/equity-curve', { params }),
  getTradeHistory: (params) => api.get('/api/analytics/trades', { params }),
};

// Watchlist endpoints
export const watchlistAPI = {
  getAll: () => api.get('/api/watchlist'),
  add: (symbol) => api.post('/api/watchlist', { symbol }),
  remove: (symbol) => api.delete(`/api/watchlist/${symbol}`),
};

// Settings endpoints
export const settingsAPI = {
  get: () => api.get('/api/settings'),
  update: (settings) => api.put('/api/settings', settings),
  updateProfile: (profile) => api.put('/api/settings/profile', profile),
  updateTradingConfig: (config) => api.put('/api/settings/trading', config),
};

// Dashboard endpoints
export const dashboardAPI = {
  getStats: () => api.get('/api/dashboard/stats'),
  getActivity: () => api.get('/api/dashboard/activity'),
  getPerformance: () => api.get('/api/dashboard/performance'),
  getPositions: () => api.get('/api/dashboard/positions'),
};

export default api;
