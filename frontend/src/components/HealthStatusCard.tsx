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
        return <XCircle className="h-8 w-8 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-8 w-8 text-yellow-500" />;
      case 'good':
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      default:
        return <Activity className="h-8 w-8 text-blue-500" />;
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'good':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-blue-600 bg-blue-50 border-blue-200';
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
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {getHealthIcon(healthSummary.overall_health)}
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                System Health
              </h3>
              <p className={`text-sm font-medium ${getHealthColor(healthSummary.overall_health)}`}>
                {getHealthText(healthSummary.overall_health)}
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">
              {healthSummary.total_insights}
            </div>
            <div className="text-sm text-gray-500">Total Insights</div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-red-600">
              {healthSummary.critical_issues}
            </div>
            <div className="text-xs text-gray-500">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-yellow-600">
              {healthSummary.warnings}
            </div>
            <div className="text-xs text-gray-500">Warnings</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-blue-600">
              {healthSummary.insight_counts.info}
            </div>
            <div className="text-xs text-gray-500">Info</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-green-600">
              {healthSummary.insight_counts.success}
            </div>
            <div className="text-xs text-gray-500">Success</div>
          </div>
        </div>

        {healthSummary.recommendations > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <CheckCircle className="h-5 w-5 text-blue-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-700">
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
