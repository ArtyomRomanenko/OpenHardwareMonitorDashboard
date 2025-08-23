import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Thermometer, 
  Cpu, 
  HardDrive, 
  AlertTriangle, 
  CheckCircle,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Clock
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
  const [retryCount, setRetryCount] = useState(0);
  const [loadingTime, setLoadingTime] = useState(0);
  const [isLongRequest, setIsLongRequest] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (loading && isLongRequest) {
      interval = setInterval(() => {
        setLoadingTime(prev => prev + 1);
      }, 1000);
    } else {
      setLoadingTime(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading, isLongRequest]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      setLoadingTime(0);
      
      // Set long request flag for time ranges that might take longer
      setIsLongRequest(timeRange >= 14);
      
      console.log(`Fetching dashboard data for ${timeRange} days...`);
      
      const response = await dashboardAPI.getOverview(timeRange);
      console.log('Dashboard response:', response.data);
      
      setData(response.data);
      setIsLongRequest(false);
    } catch (err: any) {
      console.error('Dashboard error:', err);
      setIsLongRequest(false);
      
      let errorMessage = 'Failed to load dashboard data';
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = `Request timed out after ${loadingTime} seconds. The ${timeRange}-day period contains a lot of data and may take longer to process.`;
      } else if (err.response) {
        // Server responded with error status
        const status = err.response.status;
        const detail = err.response.data?.detail || 'Unknown server error';
        
        if (status === 500) {
          errorMessage = `Server error: ${detail}`;
        } else if (status === 404) {
          errorMessage = `Data not found for ${timeRange} days`;
        } else if (status === 400) {
          errorMessage = `Invalid request: ${detail}`;
        } else {
          errorMessage = `HTTP ${status}: ${detail}`;
        }
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Is the backend running?';
      } else {
        // Something else happened
        errorMessage = err.message || 'Network error occurred';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    fetchDashboardData();
  };

  const handleTimeRangeChange = (newTimeRange: number) => {
    setTimeRange(newTimeRange);
    setError(null); // Clear previous errors when changing time range
    setRetryCount(0); // Reset retry count
  };

  const getTimeRangeWarning = (days: number) => {
    if (days >= 30) {
      return "⚠️ 30+ days may take 1-2 minutes to load due to large data volume";
    } else if (days >= 14) {
      return "⏱️ 14+ days may take 30-60 seconds to process";
    }
    return null;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-1 text-sm text-gray-500">
              Hardware monitoring overview for the last {timeRange} days
            </p>
            {getTimeRangeWarning(timeRange) && (
              <p className="mt-1 text-sm text-yellow-600">
                {getTimeRangeWarning(timeRange)}
              </p>
            )}
          </div>
          <div className="mt-4 sm:mt-0">
            <select
              value={timeRange}
              onChange={(e) => handleTimeRangeChange(Number(e.target.value))}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
            </select>
          </div>
        </div>

        {/* Loading State */}
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <LoadingSpinner />
            <div className="mt-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Loading Dashboard Data
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Processing {timeRange} days of hardware monitoring data...
              </p>
              
              {isLongRequest && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-md p-4 max-w-md mx-auto">
                  <div className="flex items-center">
                    <Clock className="h-5 w-5 text-blue-400 mr-2" />
                    <div className="text-sm text-blue-700 dark:text-blue-300">
                      <p className="font-medium">Large dataset detected</p>
                      <p>This may take {timeRange >= 30 ? '1-2 minutes' : '30-60 seconds'} to process</p>
                      <p className="mt-1">Elapsed time: {loadingTime}s</p>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="mt-4 text-sm text-gray-400 dark:text-gray-500">
                Please wait while we analyze your hardware data...
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-1 text-sm text-gray-500">
              Hardware monitoring overview for the last {timeRange} days
            </p>
            {getTimeRangeWarning(timeRange) && (
              <p className="mt-1 text-sm text-yellow-600">
                {getTimeRangeWarning(timeRange)}
              </p>
            )}
          </div>
          <div className="mt-4 sm:mt-0">
            <select
              value={timeRange}
              onChange={(e) => handleTimeRangeChange(Number(e.target.value))}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
            </select>
          </div>
        </div>

        {/* Error Display */}
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-md p-6">
          <div className="flex items-start">
            <AlertTriangle className="h-6 w-6 text-red-400 mt-0.5" />
            <div className="ml-3 flex-1">
              <h3 className="text-lg font-medium text-red-800 dark:text-red-200">Error loading dashboard</h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">{error}</div>
              
              {/* Troubleshooting Tips */}
              <div className="mt-4 bg-red-100 dark:bg-red-900/30 rounded-md p-4">
                <h4 className="font-medium text-red-800 dark:text-red-200 mb-2">Troubleshooting Tips:</h4>
                <ul className="list-disc list-inside text-sm text-red-700 dark:text-red-300 space-y-1">
                  <li>Make sure the backend server is running</li>
                  <li>Try selecting a shorter time period first (7 days instead of 30)</li>
                  <li>Large time ranges (30+ days) may timeout - try 14 days first</li>
                  <li>Check the browser console for more detailed error information</li>
                  <li>Your data contains {timeRange} days of CSV files which may be large</li>
                </ul>
              </div>
              
              {/* Action Buttons */}
              <div className="mt-4 flex space-x-3">
                <button
                  onClick={handleRetry}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry ({retryCount})
                </button>
                
                <button
                  onClick={() => handleTimeRangeChange(7)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Try 7 Days
                </button>
                
                <button
                  onClick={() => handleTimeRangeChange(14)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Try 14 Days
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-1 text-sm text-gray-500">
              Hardware monitoring overview for the last {timeRange} days
            </p>
            {getTimeRangeWarning(timeRange) && (
              <p className="mt-1 text-sm text-yellow-600">
                {getTimeRangeWarning(timeRange)}
              </p>
            )}
          </div>
          <div className="mt-4 sm:mt-0">
            <select
              value={timeRange}
              onChange={(e) => handleTimeRangeChange(Number(e.target.value))}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
            </select>
          </div>
        </div>

        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-md p-6">
          <div className="text-center">
            <h3 className="text-lg font-medium text-yellow-800 dark:text-yellow-200 mb-2">No Dashboard Data</h3>
            <p className="text-yellow-700 dark:text-yellow-300">
              No dashboard data available. Try selecting a different time period or check if the backend is running.
            </p>
          </div>
        </div>
      </div>
    );
  }

    const { system_info, overview, health_summary, recent_insights } = data;
  
  // Debug data structure
  console.log('Dashboard data structure:', {
    system_info: !!system_info,
    overview: overview,
    health_summary: !!health_summary,
    recent_insights: recent_insights
  });
  console.log('Overview metrics:', overview?.metrics);
  console.log('Overview data points:', overview?.data_points);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Hardware monitoring overview for the last {timeRange} days
          </p>
          {getTimeRangeWarning(timeRange) && (
            <p className="mt-1 text-sm text-yellow-600 dark:text-yellow-400">
              {getTimeRangeWarning(timeRange)}
            </p>
          )}
        </div>
        <div className="mt-4 sm:mt-0">
          <select
            value={timeRange}
            onChange={(e) => handleTimeRangeChange(Number(e.target.value))}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
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
         {overview?.metrics && Object.keys(overview.metrics).length > 0 ? (
           Object.entries(overview.metrics).map(([key, metric]: [string, any]) => (
             <MetricCard
               key={key}
               title={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
               value={metric.current}
               unit={metric.unit}
               change={metric.average ? ((metric.current - metric.average) / metric.average * 100) : 0}
               icon={getMetricIcon(key)}
               status={getMetricStatus(key, metric.current)}
             />
           ))
         ) : (
           <div className="col-span-full bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-md p-6">
             <div className="text-center">
               <h3 className="text-lg font-medium text-yellow-800 dark:text-yellow-200 mb-2">No Metrics Data</h3>
               <p className="text-yellow-700 dark:text-yellow-300">
                 No hardware metrics data available for the selected time period. 
                 This may indicate that no CSV files were found or the data format is not recognized.
               </p>
             </div>
           </div>
         )}
       </div>

      {/* Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <InsightsCard
          title="Recent Insights"
          insights={recent_insights?.insights || []}
          loading={false}
        />
        
                 {/* Performance Summary */}
         <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
           <div className="px-4 py-5 sm:p-6">
             <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
               Performance Summary
             </h3>
             <div className="space-y-4">
               {overview?.metrics && Object.keys(overview.metrics).length > 0 ? (
                 Object.entries(overview.metrics).map(([key, metric]: [string, any]) => (
                   <div key={key} className="flex items-center justify-between">
                     <div className="flex items-center">
                       <div className={`w-3 h-3 rounded-full mr-3 ${getStatusColor(key, metric.current)}`} />
                       <span className="text-sm font-medium text-gray-900 dark:text-white">
                         {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                       </span>
                     </div>
                     <div className="text-sm text-gray-500 dark:text-gray-400">
                       {metric.current}{metric.unit} / {metric.average?.toFixed(1)}{metric.unit} avg
                     </div>
                   </div>
                 ))
               ) : (
                 <div className="text-center py-8">
                   <div className="text-gray-400 dark:text-gray-500 text-4xl mb-2">📊</div>
                   <p className="text-sm text-gray-500 dark:text-gray-400">No performance data available</p>
                 </div>
               )}
             </div>
           </div>
         </div>
      </div>

      {/* Data Summary */}
      <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
            Data Summary
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {overview?.data_points || 0}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Data Points</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {overview?.metrics ? Object.keys(overview.metrics).length : 0}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Metrics Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {recent_insights?.total_insights || 0}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Insights Generated</div>
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
