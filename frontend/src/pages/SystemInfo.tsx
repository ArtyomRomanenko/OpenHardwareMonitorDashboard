import React, { useState, useEffect } from 'react';
import { metricsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const SystemInfo: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Placeholder for system info page
    setLoading(false);
  }, []);

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
        <h1 className="text-2xl font-bold text-gray-900">System Information</h1>
        <p className="mt-1 text-sm text-gray-500">
          Detailed system specifications and hardware details
        </p>
      </div>
      
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              System Details
            </h3>
            <p className="text-gray-500">
              Comprehensive system information will be displayed here.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemInfo;
