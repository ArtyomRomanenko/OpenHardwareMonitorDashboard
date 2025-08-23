import React from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

interface Insight {
  id: string;
  title: string;
  description: string;
  level: 'critical' | 'warning' | 'info' | 'success';
  metric_type: string;
  component: string;
  timestamp: string;
  recommendations: string[];
}

interface InsightsCardProps {
  title: string;
  insights: Insight[];
  loading: boolean;
}

const InsightsCard: React.FC<InsightsCardProps> = ({ title, insights, loading }) => {
  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-500 dark:text-red-400" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500 dark:text-yellow-400" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500 dark:text-green-400" />;
      default:
        return <Info className="h-5 w-5 text-blue-500 dark:text-blue-400" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'border-red-200 dark:border-red-700 bg-red-50 dark:bg-red-900/20';
      case 'warning':
        return 'border-yellow-200 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/20';
      case 'success':
        return 'border-green-200 dark:border-green-700 bg-green-50 dark:bg-green-900/20';
      default:
        return 'border-blue-200 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
        
        {insights.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No issues detected</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Your hardware is performing well within normal parameters.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.slice(0, 5).map((insight) => (
              <div
                key={insight.id}
                className={`border rounded-lg p-4 ${getLevelColor(insight.level)}`}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    {getLevelIcon(insight.level)}
                  </div>
                  <div className="ml-3 flex-1">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                      {insight.title}
                    </h4>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                      {insight.description}
                    </p>
                    {insight.recommendations && insight.recommendations.length > 0 && (
                      <div className="mt-3">
                        <h5 className="text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                          Recommendations:
                        </h5>
                        <ul className="mt-1 text-sm text-gray-600 dark:text-gray-300 space-y-1">
                          {insight.recommendations.slice(0, 2).map((rec, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-gray-400 dark:text-gray-500 mr-2">•</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      {insight.metric_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} • {insight.component}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {insights.length > 5 && (
              <div className="text-center pt-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Showing 5 of {insights.length} insights
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightsCard;
