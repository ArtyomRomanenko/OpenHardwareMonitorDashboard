import React, { useState, useEffect, useCallback } from 'react';
import { metricsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
} from 'chart.js';
import { Line, Pie, Scatter, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
);

interface MetricData {
  metric_type: string;
  component: string;
  unit: string;
  values: number[];
  timestamps: string[];
}

interface AvailableDates {
  dates: string[];
  count: number;
  date_range: {
    start: string;
    end: string;
  };
}

interface MetricsResponse {
  data: MetricData[];
  time_range: string;
  total_records: number;
}

const Metrics: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [availableDates, setAvailableDates] = useState<AvailableDates | null>(null);
  const [selectedStartDate, setSelectedStartDate] = useState<string>('');
  const [selectedEndDate, setSelectedEndDate] = useState<string>('');
  const [metricsData, setMetricsData] = useState<MetricData[]>([]);
  const [selectedMetricTypes, setSelectedMetricTypes] = useState<string[]>([]);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [selectedChartType, setSelectedChartType] = useState<string>('line');
  const [chartOptions, setChartOptions] = useState<any>({});

  const metricTypes = [
    { value: 'cpu_temperature', label: 'CPU Temperature', color: 'rgb(239, 68, 68)' },
    { value: 'gpu_temperature', label: 'GPU Temperature', color: 'rgb(220, 38, 127)' },
    { value: 'cpu_usage', label: 'CPU Usage', color: 'rgb(59, 130, 246)' },
    { value: 'gpu_usage', label: 'GPU Usage', color: 'rgb(147, 51, 234)' },
    { value: 'memory_usage', label: 'Memory Usage', color: 'rgb(16, 185, 129)' },
    { value: 'disk_usage', label: 'Disk Usage', color: 'rgb(245, 158, 11)' },
    { value: 'fan_speed', label: 'Fan Speed', color: 'rgb(99, 102, 241)' }
  ];

  useEffect(() => {
    loadAvailableDates();
  }, []);

  useEffect(() => {
    if (availableDates && availableDates.dates.length > 0) {
      const lastDate = availableDates.dates[availableDates.dates.length - 1];
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      const sevenDaysAgoStr = sevenDaysAgo.toISOString().split('T')[0];
      
      setSelectedStartDate(sevenDaysAgoStr);
      setSelectedEndDate(lastDate);
    }
  }, [availableDates]);

  const loadMetrics = useCallback(async () => {
    if (!selectedStartDate || !selectedEndDate) return;
    
    try {
      setLoadingMetrics(true);
      console.log(`Loading metrics for ${selectedStartDate} to ${selectedEndDate} with types:`, selectedMetricTypes);
      
      const response = await metricsAPI.getTimeSeriesData(
        selectedStartDate,
        selectedEndDate,
        selectedMetricTypes.length > 0 ? selectedMetricTypes : undefined
      );
      
      console.log('Metrics response:', response.data);
      
      // Filter the data based on selected metric types if any are selected
      let filteredData = response.data.data || [];
      
      if (selectedMetricTypes.length > 0) {
        filteredData = filteredData.filter((metric: any) => 
          selectedMetricTypes.includes(metric.metric_type)
        );
        console.log(`Filtered to ${filteredData.length} metrics:`, filteredData.map((m: any) => m.metric_type));
      }
      
      setMetricsData(filteredData);
      setError(null);
    } catch (err) {
      setError('Failed to load metrics data');
      console.error('Error loading metrics:', err);
    } finally {
      setLoadingMetrics(false);
    }
  }, [selectedStartDate, selectedEndDate, selectedMetricTypes]);

  useEffect(() => {
    if (selectedStartDate && selectedEndDate) {
      loadMetrics();
    }
  }, [selectedStartDate, selectedEndDate, selectedMetricTypes, loadMetrics]);

  const loadAvailableDates = async () => {
    try {
      setLoading(true);
      const response = await metricsAPI.getAvailableDates();
      setAvailableDates(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load available dates');
      console.error('Error loading dates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMetricTypeToggle = (metricType: string) => {
    setSelectedMetricTypes(prev => 
      prev.includes(metricType) 
        ? prev.filter(t => t !== metricType)
        : [...prev, metricType]
    );
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getMetricStats = (values: any[]): { min: number; max: number; avg: number } => {
    try {
      // Deep safety check - ensure we have a valid array
      if (!Array.isArray(values)) {
        console.warn('getMetricStats: values is not an array:', typeof values, values);
        return { min: 0, max: 0, avg: 0 };
      }
      
      if (values.length === 0) {
        return { min: 0, max: 0, avg: 0 };
      }
      
      // Check for circular references by limiting depth
      const maxDepth = 10;
      let depth = 0;
      
      const flattenValues = (arr: any[], currentDepth: number = 0): number[] => {
        if (currentDepth > maxDepth) {
          console.warn('getMetricStats: Maximum depth exceeded, truncating data');
          return [];
        }
        
        const result: number[] = [];
        for (let i = 0; i < Math.min(arr.length, 1000); i++) { // Limit array size
          const item = arr[i];
          if (typeof item === 'number' && isFinite(item)) {
            result.push(item);
          } else if (Array.isArray(item)) {
            result.push(...flattenValues(item, currentDepth + 1));
          }
        }
        return result;
      };
      
      const validValues = flattenValues(values);
      
      if (validValues.length === 0) {
        console.warn('getMetricStats: No valid numeric values found');
        return { min: 0, max: 0, avg: 0 };
      }
      
      // Use safer math operations
      const sum = validValues.reduce((a, b) => a + b, 0);
      const min = Math.min(...validValues);
      const max = Math.max(...validValues);
      
      return {
        min: isFinite(min) ? min : 0,
        max: isFinite(max) ? max : 1, // Ensure max is never 0
        avg: isFinite(sum / validValues.length) ? sum / validValues.length : 0
      };
    } catch (error) {
      console.error('getMetricStats error:', error);
      return { min: 0, max: 1, avg: 0 };
    }
  };

  const getSafeChartData = (values: any[], maxPoints: number = 500): { values: number[], indices: number[] } => {
    try {
      if (!Array.isArray(values)) return { values: [], indices: [] };
      if (values.length === 0) return { values: [], indices: [] };
      
      // For very large datasets, use smart sampling to preserve time range
      if (values.length > maxPoints) {
        const step = Math.floor(values.length / maxPoints);
        const sampledIndices: number[] = [];
        const sampledValues: number[] = [];
        
        // Always include first and last points to preserve range boundaries
        sampledIndices.push(0);
        sampledValues.push(values[0]);
        
        // Sample middle points
        for (let i = step; i < values.length - step; i += step) {
          if (typeof values[i] === 'number' && isFinite(values[i])) {
            sampledIndices.push(i);
            sampledValues.push(values[i]);
          }
        }
        
        // Always include last point
        if (values.length > 1) {
          sampledIndices.push(values.length - 1);
          sampledValues.push(values[values.length - 1]);
        }
        
        return { 
          values: sampledValues.filter(v => typeof v === 'number' && isFinite(v)),
          indices: sampledIndices
        };
      }
      
      // For smaller datasets, return all data with sequential indices
      const validValues = values.filter(v => typeof v === 'number' && isFinite(v));
      const indices = validValues.map((_, i) => i);
      return { values: validValues, indices };
    } catch (error) {
      console.error('getSafeChartData error:', error);
      return { values: [], indices: [] };
    }
  };

  const calculateChartHeight = (value: number, maxValue: number): number => {
    try {
      if (!maxValue || maxValue === 0 || !isFinite(maxValue)) return 2;
      if (!value || !isFinite(value)) return 2;
      
      const height = (value / maxValue) * 100;
      return Math.max(Math.min(height, 100), 2); // Clamp between 2% and 100%
    } catch (error) {
      console.error('calculateChartHeight error:', error);
      return 2;
    }
  };

  const getChartData = (metric: any, chartType: string) => {
    try {
      if (!metric || !Array.isArray(metric.values)) return null;
      
      const chartData = getSafeChartData(metric.values, 500);
      const values = chartData.values;
      const indices = chartData.indices;
      
      // Get timestamps corresponding to the sampled indices
      const timestamps = metric.timestamps ? 
        indices.map(idx => metric.timestamps[idx]).filter(Boolean) : [];
      
      const colors = [
        'rgba(59, 130, 246, 0.8)',   // Blue
        'rgba(147, 51, 234, 0.8)',   // Purple
        'rgba(16, 185, 129, 0.8)',   // Green
        'rgba(245, 158, 11, 0.8)',   // Yellow
        'rgba(239, 68, 68, 0.8)',    // Red
        'rgba(99, 102, 241, 0.8)',   // Indigo
        'rgba(220, 38, 127, 0.8)'    // Pink
      ];
      
      const metricType = metricTypes.find(mt => mt.value === metric.metric_type);
      const color = metricType?.color || colors[0];
      
      switch (chartType) {
        case 'line':
          return {
            labels: timestamps.length > 0 ? timestamps.map((timestamp: any) => {
              try {
                const date = new Date(timestamp);
                if (isNaN(date.getTime())) {
                  return timestamp; // Return original if parsing fails
                }
                // Format as "MM/DD HH:MM" for better readability
                return date.toLocaleDateString('en-US', { 
                  month: '2-digit', 
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                });
              } catch (error) {
                return timestamp; // Return original if formatting fails
              }
            }) : values.map((_: any, i: number) => `Point ${i + 1}`),
            datasets: [{
              label: metricType?.label || metric.metric_type,
              data: values,
              borderColor: color,
              backgroundColor: 'transparent',
              borderWidth: 2,
              fill: false,
              tension: 0.4,
              pointRadius: 3,
              pointHoverRadius: 6
            }]
          };
          
        case 'pie':
          // For pie charts, we'll show the distribution of values in ranges
          const ranges = [0, 25, 50, 75, 100];
          const rangeLabels = ['0-25%', '25-50%', '50-75%', '75-100%'];
          const rangeCounts = ranges.slice(0, -1).map((start, i) => {
            const end = ranges[i + 1];
            return values.filter(v => v >= start && v < end).length;
          });
          
          return {
            labels: rangeLabels,
            datasets: [{
              data: rangeCounts,
              backgroundColor: colors.slice(0, rangeCounts.length),
              borderColor: colors.slice(0, rangeCounts.length).map(c => c.replace('0.8', '1')),
              borderWidth: 2
            }]
          };
          
        case 'scatter':
          return {
            datasets: [{
              label: metricType?.label || metric.metric_type,
              data: values.map((value, index) => {
                if (timestamps.length > index) {
                  try {
                    const timestamp = timestamps[index];
                    const date = new Date(timestamp);
                    if (!isNaN(date.getTime())) {
                      // Use timestamp as X value for scatter plot
                      return {
                        x: date.getTime(), // Use milliseconds since epoch
                        y: value
                      };
                    }
                  } catch (error) {
                    // Fallback to index if timestamp parsing fails
                  }
                }
                // Fallback to index-based positioning
                return {
                  x: indices[index] || index,
                  y: value
                };
              }),
              backgroundColor: color,
              borderColor: color.replace('0.8', '1'),
              pointRadius: 4,
              pointHoverRadius: 8
            }]
          };
          
        case 'doughnut':
          // For doughnut charts, show min, max, and average
          const stats = getMetricStats(metric.values);
          return {
            labels: ['Min', 'Average', 'Max'],
            datasets: [{
              data: [stats.min, stats.avg, stats.max],
              backgroundColor: [colors[0], colors[1], colors[2]],
              borderColor: [colors[0], colors[1], colors[2]].map(c => c.replace('0.8', '1')),
              borderWidth: 2
            }]
          };
          
        default:
          return null;
      }
    } catch (error) {
      console.error('getChartData error:', error);
      return null;
    }
  };

  const getChartOptions = (chartType: string, metric: any) => {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
          labels: {
            usePointStyle: true,
            padding: 20,
            font: {
              size: 12,
              weight: 'bold' as const
            }
          }
        },
        tooltip: {
          mode: 'index' as const,
          intersect: false,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: 'white',
          bodyColor: 'white',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: true
        }
      },
      interaction: {
        mode: 'nearest' as const,
        axis: 'x' as const,
        intersect: false
      }
    };

         // Only add scales for charts that need them
     if (chartType === 'line' || chartType === 'scatter') {
       return {
         ...baseOptions,
         scales: {
           x: {
             display: true,
             title: {
               display: true,
               text: chartType === 'line' ? 'Time' : 'Time',
               font: { weight: 'bold' as const }
             },
             grid: {
               color: 'rgba(0, 0, 0, 0.1)',
               drawBorder: false
             },
             // For line charts, rotate labels if they're too long
             ticks: chartType === 'line' ? {
               maxRotation: 45,
               minRotation: 0,
               autoSkip: true,
               maxTicksLimit: 15
             } : undefined
           },
           y: {
             display: true,
             title: {
               display: true,
               text: metric.unit || 'Value',
               font: { weight: 'bold' as const }
             },
             grid: {
               color: 'rgba(0, 0, 0, 0.1)',
               drawBorder: false
             }
           }
         }
       };
     }
    
    // For pie and doughnut charts, return base options without scales
    return baseOptions;
  };

  const renderMetricCard = (metric: any, index: number) => {
    try {
      // Validate metric structure
      if (!metric || typeof metric !== 'object') {
        console.warn('Invalid metric object:', metric);
        return null;
      }
      
      if (!Array.isArray(metric.values)) {
        console.warn('Metric values is not an array:', metric.values);
        return null;
      }
      
             // Get the same sampled data that's used in charts for consistent statistics
       const chartData = getSafeChartData(metric.values, 500);
       const stats = getMetricStats(chartData.values);
       const metricType = metricTypes.find(mt => mt.value === metric.metric_type);
       const isLargeDataset = metric.values.length > 1000;
      
      return (
        <div key={index} className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {metricType?.label || metric.metric_type || 'Unknown Metric'}
              </h3>
                             <p className="text-sm text-gray-500 dark:text-gray-400">
                 {metric.component || 'Unknown'} • {metric.unit || ''} • {chartData.values.length.toLocaleString()} displayed / {metric.values.length.toLocaleString()} total data points
                 {isLargeDataset && (
                   <span className="ml-2 text-yellow-600 dark:text-yellow-400 font-medium">
                     (Large dataset - chart shows full time range with smart sampling)
                   </span>
                 )}
               </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.avg.toFixed(1)}{metric.unit || ''}
              </div>
                             <div className="text-sm text-gray-500 dark:text-gray-400">
                 Min: {stats.min.toFixed(1)} | Max: {stats.max.toFixed(1)}
                 {isLargeDataset && (
                   <span className="block text-xs text-yellow-600 dark:text-yellow-400">
                     (based on sampled data)
                   </span>
                 )}
               </div>
            </div>
          </div>

          {/* Enhanced Chart Visualization */}
          <div className="h-64 bg-gray-50 dark:bg-gray-700 rounded-lg p-4 overflow-hidden">
            {(() => {
              const chartData = getChartData(metric, selectedChartType);
              const chartOptions = getChartOptions(selectedChartType, metric);
              
              if (!chartData) {
                return (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    <div className="text-center">
                      <div className="text-2xl mb-2">📊</div>
                      <div className="text-sm">Chart data unavailable</div>
                    </div>
                  </div>
                );
              }
              
              // Use type assertions to resolve Chart.js type compatibility issues
              // The chartData and chartOptions are properly structured but TypeScript
              // has strict type checking that doesn't match Chart.js's flexible typing
              try {
                switch (selectedChartType) {
                  case 'line':
                    return <Line data={chartData as any} options={chartOptions as any} />;
                  case 'scatter':
                    return <Scatter data={chartData as any} options={chartOptions as any} />;
                  case 'pie':
                    return <Pie data={chartData as any} options={chartOptions as any} />;
                  case 'doughnut':
                    return <Doughnut data={chartData as any} options={chartOptions as any} />;
                  default:
                    return <Line data={chartData as any} options={chartOptions as any} />;
                }
              } catch (error) {
                console.error('Chart rendering error:', error);
                return (
                  <div className="flex items-center justify-center h-full text-red-500">
                    <div className="text-center">
                      <div className="text-2xl mb-2">❌</div>
                      <div className="text-sm">Chart rendering failed</div>
                    </div>
                  </div>
                );
              }
            })()}
          </div>

                     {/* Data Table */}
           <div className="mt-4">
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                 Recent Data Points {isLargeDataset && `(showing first 10 of ${chartData.values.length.toLocaleString()} sampled from ${metric.values.length.toLocaleString()} total)`}
               </h4>
             <div className="max-h-40 overflow-y-auto">
               <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                 <thead className="bg-gray-50 dark:bg-gray-700">
                   <tr>
                     <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Time</th>
                     <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Value</th>
                   </tr>
                 </thead>
                 <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                   {(() => {
                     // Get sampled data for the table to match the chart
                     const chartData = getSafeChartData(metric.values, 500);
                     const tableValues = chartData.values.slice(0, 10);
                     const tableIndices = chartData.indices.slice(0, 10);
                     
                     return tableValues.map((value: any, tableIdx: number) => {
                       const originalIdx = tableIndices[tableIdx];
                       const timestamp = metric.timestamps && metric.timestamps[originalIdx] ? metric.timestamps[originalIdx] : null;
                       let timeDisplay = `Point ${originalIdx + 1}`;
                       
                       if (timestamp) {
                         try {
                           const date = new Date(timestamp);
                           if (!isNaN(date.getTime())) {
                             timeDisplay = date.toLocaleString('en-US', {
                               month: '2-digit',
                               day: '2-digit',
                               year: 'numeric',
                               hour: '2-digit',
                               minute: '2-digit',
                               second: '2-digit',
                               hour12: false
                             });
                           }
                         } catch (error) {
                           timeDisplay = timestamp; // Use original timestamp if parsing fails
                         }
                       }
                       
                       return (
                         <tr key={tableIdx}>
                           <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                             {timeDisplay}
                           </td>
                           <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                             {typeof value === 'number' ? value.toFixed(2) : String(value)}{metric.unit || ''}
                           </td>
                         </tr>
                       );
                     });
                   })()}
                 </tbody>
               </table>
             </div>
           </div>
        </div>
      );
    } catch (error) {
      console.error('Error rendering metric card:', error);
      return (
        <div key={index} className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-md p-6">
          <h3 className="text-lg font-medium text-red-800 dark:text-red-200">Error Rendering Metric</h3>
          <p className="text-red-700 dark:text-red-300">Failed to render metric data. Check console for details.</p>
        </div>
      );
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Hardware Metrics</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Detailed hardware metrics and time series analysis
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
              <p className="mt-1 text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Date Selection */}
      {availableDates && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Date Range</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Date</label>
              <select
                value={selectedStartDate}
                onChange={(e) => setSelectedStartDate(e.target.value)}
                className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select start date</option>
                {availableDates.dates.map(date => (
                  <option key={date} value={date}>{formatDate(date)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Date</label>
              <select
                value={selectedEndDate}
                onChange={(e) => setSelectedEndDate(e.target.value)}
                className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select end date</option>
                {availableDates.dates.map(date => (
                  <option key={date} value={date}>{formatDate(date)}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={loadMetrics}
                disabled={!selectedStartDate || !selectedEndDate || loadingMetrics}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingMetrics ? 'Loading...' : 'Load Metrics'}
              </button>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Available: {availableDates.count} dates from {formatDate(availableDates.date_range.start)} to {formatDate(availableDates.date_range.end)}
          </p>
        </div>
      )}

      {/* Chart Type Selection */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Chart Type</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { value: 'line', label: 'Line Chart', icon: '📈', description: 'Time series trends' },
            { value: 'scatter', label: 'Scatter Plot', icon: '🔵', description: 'Data point distribution' },
            { value: 'pie', label: 'Pie Chart', icon: '🥧', description: 'Value range distribution' },
            { value: 'doughnut', label: 'Doughnut Chart', icon: '🍩', description: 'Min/Avg/Max summary' }
          ].map(chartType => (
            <label key={chartType.value} className="flex flex-col items-center space-y-2 cursor-pointer p-3 border-2 border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <input
                type="radio"
                name="chartType"
                value={chartType.value}
                checked={selectedChartType === chartType.value}
                onChange={(e) => setSelectedChartType(e.target.value)}
                className="sr-only"
              />
              <div className={`text-2xl ${selectedChartType === chartType.value ? 'scale-110' : ''} transition-transform`}>
                {chartType.icon}
              </div>
              <div className="text-center">
                <div className={`font-medium text-sm ${selectedChartType === chartType.value ? 'text-blue-600 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'}`}>
                  {chartType.label}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {chartType.description}
                </div>
              </div>
              {selectedChartType === chartType.value && (
                <div className="w-2 h-2 bg-blue-600 dark:bg-blue-400 rounded-full"></div>
              )}
            </label>
          ))}
        </div>
        <p className="mt-3 text-sm text-gray-500 dark:text-gray-400 text-center">
          Select a chart type to visualize your metrics data. Each chart type offers different insights into your hardware performance.
        </p>
      </div>

      {/* Metric Type Selection */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Metric Types</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {metricTypes.map(metric => (
            <label key={metric.value} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedMetricTypes.length === 0 || selectedMetricTypes.includes(metric.value)}
                onChange={() => handleMetricTypeToggle(metric.value)}
                className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              <span className={`text-sm ${selectedMetricTypes.length > 0 && !selectedMetricTypes.includes(metric.value) ? 'text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'}`}>
                {metric.label}
              </span>
            </label>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {selectedMetricTypes.length === 0 ? 'All metric types selected' : `${selectedMetricTypes.length} metric types selected`}
          </p>
          {selectedMetricTypes.length > 0 && (
            <button
              onClick={() => setSelectedMetricTypes([])}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline"
            >
              Show All Types
            </button>
          )}
        </div>
        {selectedMetricTypes.length > 0 && (
          <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-md">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              <strong>Filtering Active:</strong> Only showing {selectedMetricTypes.join(', ')} metrics. 
              Data will reload automatically when you change the selection.
            </p>
          </div>
        )}
      </div>

      {/* Metrics Display */}
      {loadingMetrics && (
        <div className="flex items-center justify-center h-32">
          <LoadingSpinner />
        </div>
      )}

      {!loadingMetrics && metricsData.length > 0 && (
        <div className="space-y-6">
          {/* Large Dataset Warning */}
          {metricsData.some(metric => metric.values.length > 1000) && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">Large Dataset Detected</h3>
                                     <p className="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
                     Some metrics contain large amounts of data. Charts are automatically sampled to prevent performance issues while preserving the full time range. 
                     Statistics and charts show sampled data, full data is available in the data table below.
                   </p>
                </div>
              </div>
            </div>
          )}

          {metricsData.map((metric, index) => renderMetricCard(metric, index))}
        </div>
      )}

      {!loadingMetrics && metricsData.length === 0 && selectedStartDate && selectedEndDate && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Metrics Data</h3>
            <p className="text-gray-500 dark:text-gray-400">
              No metrics data found for the selected date range. Try selecting different dates or check if the backend is running.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Metrics;
