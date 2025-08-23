import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Activity } from 'lucide-react';

interface HealthStatusCardProps {
  healthSummary: {
    overall_health: string;
    insight_counts: {
      critical: number;
      warning: number;
      info: number;
      success: number;
    };
    total_insights: number;
    critical_issues: number;
    warnings: number;
    recommendations: number;
  };
}

const HealthStatusCard: React.FC<HealthStatusCardProps> = ({ healthSummary }) => {
  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'critical':
        return <XCircle className="h-8 w-8 text-red-500 dark:text-red-400" />;
      case 'warning':
        return <AlertTriangle className="h-8 w-8 text-yellow-500 dark:text-yellow-400" />;
      case 'good':
        return <CheckCircle className="h-8 w-8 text-green-500 dark:text-green-400" />;
      default:
        return <Activity className="h-8 w-8 text-blue-500 dark:text-blue-400" />;
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'critical':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700';
      case 'good':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700';
      default:
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700';
    }
  };

  const getHealthText = (health: string) => {
    switch (health) {
      case 'critical':
        return 'Critical Issues Detected';
      case 'warning':
        return 'Warnings Detected';
      case 'good':
        return 'System Healthy';
      default:
        return 'System Normal';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {getHealthIcon(healthSummary.overall_health)}
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                System Health
              </h3>
              <p className={`text-sm font-medium ${getHealthColor(healthSummary.overall_health)}`}>
                {getHealthText(healthSummary.overall_health)}
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {healthSummary.total_insights}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Total Insights</div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-red-600 dark:text-red-400">
              {healthSummary.critical_issues}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-yellow-600 dark:text-yellow-400">
              {healthSummary.warnings}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Warnings</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-blue-600 dark:text-blue-400">
              {healthSummary.insight_counts.info}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Info</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-green-600 dark:text-green-400">
              {healthSummary.insight_counts.success}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Success</div>
          </div>
        </div>

        {healthSummary.recommendations > 0 && (
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <CheckCircle className="h-5 w-5 text-blue-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  <span className="font-medium">{healthSummary.recommendations} recommendations</span> available to improve system performance.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthStatusCard;
