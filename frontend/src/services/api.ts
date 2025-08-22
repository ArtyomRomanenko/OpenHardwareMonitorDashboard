import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased from 10000 to 60000 (60 seconds)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Metrics API
export const metricsAPI = {
  getAvailableDates: () => api.get('/metrics/available-dates'),
  getTimeSeriesData: (startDate: string, endDate: string, metricTypes?: string[]) => 
    api.get('/metrics/time-series', {
      params: { start_date: startDate, end_date: endDate, metric_types: metricTypes }
    }),
  getStatistics: (startDate: string, endDate: string, metricType: string) =>
    api.get('/metrics/statistics', {
      params: { start_date: startDate, end_date: endDate, metric_type: metricType }
    }),
  getSystemInfo: () => api.get('/metrics/system-info'),
  getQuickOverview: (days: number = 7) =>
    api.get('/metrics/quick-overview', { params: { days } }),
  getMetricTypes: () => api.get('/metrics/metric-types'),
};

// Insights API
export const insightsAPI = {
  analyzePeriod: (startDate: string, endDate: string) =>
    api.get('/insights/analyze', {
      params: { start_date: startDate, end_date: endDate }
    }),
  getHealthSummary: (startDate: string, endDate: string) =>
    api.get('/insights/health-summary', {
      params: { start_date: startDate, end_date: endDate }
    }),
  getRecentInsights: (days: number = 7) =>
    api.get('/insights/recent', { params: { days } }),
  getInsightsByLevel: (level: string, startDate: string, endDate: string) =>
    api.get('/insights/by-level', {
      params: { level, start_date: startDate, end_date: endDate }
    }),
  getInsightsByMetric: (metricType: string, startDate: string, endDate: string) =>
    api.get('/insights/by-metric', {
      params: { metric_type: metricType, start_date: startDate, end_date: endDate }
    }),
  getRecommendations: (startDate: string, endDate: string) =>
    api.get('/insights/recommendations', {
      params: { start_date: startDate, end_date: endDate }
    }),
};

// Dashboard API
export const dashboardAPI = {
  getOverview: (days: number = 7) =>
    api.get('/dashboard/overview', { params: { days } }),
  getHealthStatus: (startDate: string, endDate: string) =>
    api.get('/dashboard/health-status', {
      params: { start_date: startDate, end_date: endDate }
    }),
  getTrendsAnalysis: (startDate: string, endDate: string, metricTypes?: string[]) =>
    api.get('/dashboard/trends', {
      params: { start_date: startDate, end_date: endDate, metric_types: metricTypes }
    }),
  getPerformanceSummary: (startDate: string, endDate: string) =>
    api.get('/dashboard/performance-summary', {
      params: { start_date: startDate, end_date: endDate }
    }),
  getConfig: () => api.get('/dashboard/config'),
};

export default api;
