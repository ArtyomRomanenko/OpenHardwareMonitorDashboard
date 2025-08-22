import React, { useState, useEffect } from 'react';
import { metricsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const SystemInfo: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [loadingSystemInfo, setLoadingSystemInfo] = useState(false);

  useEffect(() => {
    loadSystemInfo();
  }, []);

  const loadSystemInfo = async () => {
    try {
      setLoadingSystemInfo(true);
      console.log('🔍 Loading system info...');
      
      const response = await metricsAPI.getSystemInfo();
      console.log('✅ System info response received:', response);
      console.log('📊 Response data:', response.data);
      console.log('🔧 Response status:', response.status);
      
      setSystemInfo(response.data);
      console.log('💾 System info state updated:', response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('❌ Error loading system info:', err);
      console.error('❌ Error details:', {
        message: err.message,
        status: err.response?.status,
        data: err.response?.data,
        stack: err.stack
      });
      setError('Failed to load system information');
      setLoading(false);
    } finally {
      setLoadingSystemInfo(false);
      console.log('🏁 System info loading finished');
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
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Information</h1>
          <p className="mt-1 text-sm text-gray-500">
            Detailed system specifications and hardware details
          </p>
        </div>
        
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
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">System Information</h1>
        <p className="mt-1 text-sm text-gray-500">
          Detailed system specifications and hardware details
        </p>
      </div>

      {/* Debug Info */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
        
        {/* Debug Info */}
        <div className="mb-4 p-3 bg-gray-100 rounded-md text-xs">
          <div className="font-medium text-gray-700 mb-2">Debug Info:</div>
          <div>Loading: {loadingSystemInfo ? 'Yes' : 'No'}</div>
          <div>System Info: {systemInfo ? 'Loaded' : 'Not loaded'}</div>
          <div>System Info Keys: {systemInfo ? Object.keys(systemInfo).join(', ') : 'None'}</div>
          {systemInfo && (
            <div className="mt-2">
              <details>
                <summary className="cursor-pointer text-blue-600">Raw System Info Data</summary>
                <pre className="mt-2 text-xs bg-white p-2 rounded border overflow-auto">
                  {JSON.stringify(systemInfo, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
        
        {loadingSystemInfo ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : systemInfo ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Memory Usage */}
            {systemInfo.memory_usage_avg && (
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-blue-900">Memory Usage</h4>
                    <p className="text-2xl font-bold text-blue-900">
                      {systemInfo.memory_usage_avg.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-16 h-16 relative">
                    <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-blue-200"
                        stroke="currentColor"
                        strokeWidth="3"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="text-blue-600"
                        stroke="currentColor"
                        strokeWidth="3"
                        strokeDasharray={`${systemInfo.memory_usage_avg}, 100`}
                        strokeLinecap="round"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-blue-900">
                      {systemInfo.memory_usage_avg.toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-blue-700 mt-2">
                  Average memory usage across the selected period
                </p>
              </div>
            )}

            {/* GPU Memory */}
            {systemInfo.gpu_memory && (
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-purple-900">GPU Memory</h4>
                    <p className="text-2xl font-bold text-purple-900">
                      {systemInfo.gpu_memory.toFixed(1)} GB
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                  </div>
                </div>
                <p className="text-xs text-purple-700 mt-2">
                  GPU memory usage information
                </p>
              </div>
            )}

            {/* Disk Usage */}
            {systemInfo.disk_usage && (
              <div className="bg-orange-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-orange-900">Disk Usage</h4>
                    <p className="text-2xl font-bold text-orange-900">
                      {systemInfo.disk_usage.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-16 h-16 relative">
                    <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-orange-200"
                        stroke="currentColor"
                        strokeWidth="3"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="text-orange-600"
                        stroke="currentColor"
                        strokeWidth="3"
                        strokeDasharray={`${systemInfo.disk_usage}, 100`}
                        strokeLinecap="round"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-orange-900">
                      {systemInfo.disk_usage.toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-orange-700 mt-2">
                  Disk space usage percentage
                </p>
              </div>
            )}

            {/* CPU Info */}
            {systemInfo.cpu_info && (
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-green-900">CPU Information</h4>
                    <p className="text-lg font-bold text-green-900">
                      {systemInfo.cpu_info}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                  </div>
                </div>
                <p className="text-xs text-green-700 mt-2">
                  CPU model and specifications
                </p>
              </div>
            )}

            {/* GPU Info */}
            {systemInfo.gpu_info && (
              <div className="bg-indigo-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-indigo-900">GPU Information</h4>
                    <p className="text-lg font-bold text-indigo-900">
                      {systemInfo.gpu_info}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                  </div>
                </div>
                <p className="text-xs text-indigo-700 mt-2">
                  Graphics card information
                </p>
              </div>
            )}

            {/* System Summary */}
            <div className="bg-gray-50 rounded-lg p-4 col-span-full">
              <h4 className="text-sm font-medium text-gray-900 mb-3">System Summary</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                {systemInfo.total_files && (
                  <div>
                    <span className="text-gray-500">Total Files:</span>
                    <span className="ml-2 font-medium text-gray-900">{systemInfo.total_files.toLocaleString()}</span>
                  </div>
                )}
                {systemInfo.date_range && (
                  <div>
                    <span className="text-gray-500">Data Range:</span>
                    <span className="ml-2 font-medium text-gray-900">
                      {new Date(systemInfo.date_range.start).toLocaleDateString()} - {new Date(systemInfo.date_range.end).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {systemInfo.monitoring_duration && (
                  <div>
                    <span className="text-gray-500">Monitoring:</span>
                    <span className="ml-2 font-medium text-gray-900">{systemInfo.monitoring_duration}</span>
                  </div>
                )}
                {systemInfo.data_points && (
                  <div>
                    <span className="text-gray-500">Data Points:</span>
                    <span className="ml-2 font-medium text-gray-900">{systemInfo.data_points.toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No system information available</p>
            <button
              onClick={loadSystemInfo}
              className="mt-2 text-blue-600 hover:text-blue-800 underline text-sm"
            >
              Try loading again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemInfo;
