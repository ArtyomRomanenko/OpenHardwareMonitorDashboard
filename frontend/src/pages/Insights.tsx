import React, { useState, useEffect, useCallback } from 'react';
import { insightsAPI, metricsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

interface AnomalyEvent {
  timestamp: string;
  value: number;
  severity: 'minor' | 'moderate' | 'severe';
  description: string;
  expected_range: [number, number];
}

interface HardwareInsight {
  id: string;
  title: string;
  description: string;
  level: 'critical' | 'warning' | 'info' | 'success';
  metric_type: string;
  component: string;
  timestamp: string;
  recommendations: string[];
  data: Record<string, any>;
  // New enhanced fields
  events: AnomalyEvent[];
  period_start: string;
  period_end: string;
  anomaly_count: number;
  baseline_stats: Record<string, number>;
}

interface HealthSummary {
  overall_health: string;
  critical_issues: number;
  warnings: number;
  healthy_metrics: number;
  recommendations: number;
  insight_counts: Record<string, number>;
  total_anomalies: number;
  period: {
    start_date: string;
    end_date: string;
  };
}

interface SystemInfo {
  cpu_model: string;
  gpu_model: string;
  total_memory: string;
  os_info: string;
  last_update: string;
  memory_usage_avg: string;
  gpu_memory: string;
}

const Insights: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<HardwareInsight[]>([]);
  const [healthSummary, setHealthSummary] = useState<HealthSummary | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [selectedMetric, setSelectedMetric] = useState<string>('all');
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  const insightLevels = [
    { value: 'all', label: 'All Levels', color: 'gray' },
    { value: 'critical', label: 'Critical', color: 'red' },
    { value: 'warning', label: 'Warning', color: 'yellow' },
    { value: 'info', label: 'Info', color: 'blue' },
    { value: 'success', label: 'Success', color: 'green' }
  ];

  const metricTypes = [
    { value: 'all', label: 'All Metrics' },
    { value: 'cpu_temperature', label: 'CPU Temperature' },
    { value: 'gpu_temperature', label: 'GPU Temperature' },
    { value: 'cpu_usage', label: 'CPU Usage' },
    { value: 'gpu_usage', label: 'GPU Usage' },
    { value: 'memory_usage', label: 'Memory Usage' },
    { value: 'disk_usage', label: 'Disk Usage' },
    { value: 'fan_speed', label: 'Fan Speed' }
  ];

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load system info first
      const systemResponse = await metricsAPI.getSystemInfo();
      setSystemInfo(systemResponse.data);
      
      // Set default date range to last 7 days
      const endDate = new Date();
      const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      setDateRange({
        start: startDate.toISOString().split('T')[0],
        end: endDate.toISOString().split('T')[0]
      });
      
      // Load insights for default period
      const insightsResponse = await insightsAPI.analyzePeriod(
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );
      setInsights(insightsResponse.data.insights || insightsResponse.data || []);
      
      // Load health summary
      const healthResponse = await insightsAPI.getHealthSummary(
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );
      setHealthSummary(healthResponse.data);
      
      setError(null);
    } catch (err) {
      setError('Failed to load insights data');
      console.error('Error loading insights:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadFilteredInsights = useCallback(async () => {
    if (!dateRange.start || !dateRange.end) return;
    
    try {
      setLoadingInsights(true);
      let response;
      
      if (selectedMetric !== 'all') {
        response = await insightsAPI.getInsightsByMetric(
          selectedMetric,
          dateRange.start,
          dateRange.end
        );
      } else if (selectedLevel !== 'all') {
        response = await insightsAPI.getInsightsByLevel(
          selectedLevel,
          dateRange.start,
          dateRange.end
        );
      } else {
        response = await insightsAPI.analyzePeriod(dateRange.start, dateRange.end);
      }
      
      setInsights(response.data.insights || response.data || []);
      
      // Also update health summary for the new period
      const healthResponse = await insightsAPI.getHealthSummary(dateRange.start, dateRange.end);
      setHealthSummary(healthResponse.data);
      
      setError(null);
    } catch (err) {
      setError('Failed to load filtered insights');
      console.error('Error loading filtered insights:', err);
    } finally {
      setLoadingInsights(false);
    }
  }, [dateRange.start, dateRange.end, selectedLevel, selectedMetric]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'success': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'info':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
      case 'success':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const formatTime = (timestamp: string) => {
    // Handle both ISO string and other timestamp formats
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return timestamp; // Return original if parsing fails
      }
      return date.toLocaleString();
    } catch {
      return timestamp; // Return original if parsing fails
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'severe': return 'bg-red-100 text-red-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'minor': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Hardware Insights</h1>
        <p className="mt-1 text-sm text-gray-500">
          Intelligent analysis and recommendations for your hardware with anomaly detection
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* System Information */}
      {systemInfo && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900">CPU</h4>
              <p className="text-blue-700">{systemInfo.cpu_model}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-medium text-purple-900">GPU</h4>
              <p className="text-purple-700">{systemInfo.gpu_model}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-medium text-green-900">Memory</h4>
              <p className="text-green-700">{systemInfo.total_memory}</p>
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-500">
            Last updated: {formatDate(systemInfo.last_update)}
          </div>
        </div>
      )}

      {/* Health Summary */}
      {healthSummary && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Health Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{healthSummary.overall_health}</div>
              <div className="text-sm text-gray-500">Overall Status</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{healthSummary.critical_issues}</div>
              <div className="text-sm text-gray-500">Critical Issues</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{healthSummary.warnings}</div>
              <div className="text-sm text-gray-500">Warnings</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{healthSummary.recommendations}</div>
              <div className="text-sm text-gray-500">Recommendations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{healthSummary.total_anomalies || 0}</div>
              <div className="text-sm text-gray-500">Anomalies</div>
            </div>
          </div>
          {healthSummary.insight_counts && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">Insight Breakdown</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                {Object.entries(healthSummary.insight_counts).map(([level, count]) => (
                  <div key={level} className="flex justify-between">
                    <span className="capitalize">{level}:</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {healthSummary.period && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Analysis Period</h4>
              <div className="text-sm text-gray-600">
                {formatDate(healthSummary.period.start_date)} to {formatDate(healthSummary.period.end_date)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Insight Level</label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {insightLevels.map(level => (
                <option key={level.value} value={level.value}>{level.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Metric Type</label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {metricTypes.map(metric => (
                <option key={metric.value} value={metric.value}>{metric.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={loadFilteredInsights}
            disabled={!dateRange.start || !dateRange.end || loadingInsights}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loadingInsights ? 'Loading...' : 'Apply Filters'}
          </button>
        </div>
      </div>

      {/* Insights Display */}
      {loadingInsights && (
        <div className="flex items-center justify-center h-32">
          <LoadingSpinner />
        </div>
      )}

      {!loadingInsights && insights.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Hardware Insights ({insights.length})</h3>
          {insights.map((insight, index) => (
            <div key={index} className={`bg-white shadow rounded-lg p-6 border-l-4 ${getLevelColor(insight.level)}`}>
              <div className="flex items-start">
                <div className="flex-shrink-0 mt-0.5">
                  {getLevelIcon(insight.level)}
                </div>
                <div className="ml-3 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">
                      {insight.title}
                    </h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLevelColor(insight.level)}`}>
                      {insight.level}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-700">{insight.description}</p>
                  
                  {/* Anomaly Events */}
                  {insight.events && insight.events.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">
                        Anomaly Events ({insight.anomaly_count})
                      </h5>
                      <div className="space-y-2">
                        {insight.events.slice(0, 5).map((event, eventIdx) => (
                          <div key={eventIdx} className="flex items-center justify-between text-xs">
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(event.severity)}`}>
                                {event.severity}
                              </span>
                              <span className="text-gray-600">
                                {formatTime(event.timestamp)}
                              </span>
                            </div>
                            <div className="text-right">
                              <span className="font-medium text-gray-900">
                                Value: {event.value}
                              </span>
                              <div className="text-gray-500">
                                Expected: {event.expected_range[0].toFixed(1)} - {event.expected_range[1].toFixed(1)}
                              </div>
                            </div>
                          </div>
                        ))}
                        {insight.events.length > 5 && (
                          <div className="text-xs text-gray-500 text-center">
                            +{insight.events.length - 5} more events
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Baseline Statistics */}
                  {insight.baseline_stats && Object.keys(insight.baseline_stats).length > 0 && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <h5 className="text-sm font-medium text-blue-900 mb-2">Baseline Statistics</h5>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        {Object.entries(insight.baseline_stats).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-blue-700 capitalize">{key}:</span>
                            <span className="font-medium text-blue-900">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {insight.recommendations && insight.recommendations.length > 0 && (
                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-900">Recommendations:</p>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                        {insight.recommendations.map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                    <span>Metric: {insight.metric_type.replace('_', ' ').toUpperCase()}</span>
                    <span>Component: {insight.component}</span>
                    <span>Generated: {formatTime(insight.timestamp)}</span>
                    {insight.period_start && insight.period_end && (
                      <span>Period: {formatDate(insight.period_start)} - {formatDate(insight.period_end)}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loadingInsights && insights.length === 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Insights Found</h3>
            <p className="text-gray-500">
              No insights data found for the selected filters. Try adjusting your filter criteria or check if the backend is running.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Insights;
