import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Thermometer, 
  Cpu, 
  HardDrive, 
  AlertTriangle, 
  CheckCircle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { dashboardAPI } from '../services/api';
import MetricCard from '../components/MetricCard';
import InsightsCard from '../components/InsightsCard';
import HealthStatusCard from '../components/HealthStatusCard';
import SystemInfoCard from '../components/SystemInfoCard';
import LoadingSpinner from '../components/LoadingSpinner';

interface DashboardData {
  system_info: any;
  overview: any;
  health_summary: any;
  recent_insights: any;
  period: any;
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(7);

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardAPI.getOverview(timeRange);
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const { system_info, overview, health_summary, recent_insights } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Hardware monitoring overview for the last {timeRange} days
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>
      </div>

      {/* System Info */}
      {system_info && Object.keys(system_info).length > 0 && (
        <SystemInfoCard systemInfo={system_info} />
      )}

      {/* Health Status */}
      <HealthStatusCard healthSummary={health_summary} />

      {/* Quick Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {overview?.metrics && Object.entries(overview.metrics).map(([key, metric]: [string, any]) => (
          <MetricCard
            key={key}
            title={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            value={metric.current}
            unit={metric.unit}
            change={metric.average ? ((metric.current - metric.average) / metric.average * 100) : 0}
            icon={getMetricIcon(key)}
            status={getMetricStatus(key, metric.current)}
          />
        ))}
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <InsightsCard
          title="Recent Insights"
          insights={recent_insights?.insights || []}
          loading={false}
        />
        
        {/* Performance Summary */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Performance Summary
            </h3>
            <div className="space-y-4">
              {overview?.metrics && Object.entries(overview.metrics).map(([key, metric]: [string, any]) => (
                <div key={key} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${getStatusColor(key, metric.current)}`} />
                    <span className="text-sm font-medium text-gray-900">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {metric.current}{metric.unit} / {metric.average?.toFixed(1)}{metric.unit} avg
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Data Summary */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Data Summary
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {overview?.data_points || 0}
              </div>
              <div className="text-sm text-gray-500">Data Points</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {overview?.metrics ? Object.keys(overview.metrics).length : 0}
              </div>
              <div className="text-sm text-gray-500">Metrics Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {recent_insights?.total_insights || 0}
              </div>
              <div className="text-sm text-gray-500">Insights Generated</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const getMetricIcon = (metricType: string) => {
  switch (metricType) {
    case 'cpu_temperature':
      return Thermometer;
    case 'gpu_temperature':
      return Thermometer;
    case 'cpu_usage':
      return Cpu;
    case 'memory_usage':
      return Activity;
    case 'disk_usage':
      return HardDrive;
    default:
      return Activity;
  }
};

const getMetricStatus = (metricType: string, value: number) => {
  if (metricType.includes('temperature')) {
    if (value >= 90) return 'critical';
    if (value >= 80) return 'warning';
    if (value <= 60) return 'good';
    return 'normal';
  }
  if (metricType.includes('usage')) {
    if (value >= 95) return 'critical';
    if (value >= 85) return 'warning';
    if (value <= 50) return 'good';
    return 'normal';
  }
  return 'normal';
};

const getStatusColor = (metricType: string, value: number) => {
  const status = getMetricStatus(metricType, value);
  switch (status) {
    case 'critical':
      return 'bg-red-500';
    case 'warning':
      return 'bg-yellow-500';
    case 'good':
      return 'bg-green-500';
    default:
      return 'bg-gray-500';
  }
};

export default Dashboard;
