import React from 'react';
import { Cpu, Monitor, HardDrive, Clock } from 'lucide-react';

interface SystemInfoCardProps {
  systemInfo: {
    cpu_model?: string;
    gpu_model?: string;
    total_memory?: number;
    os_info?: string;
    last_update: string;
  };
}

const SystemInfoCard: React.FC<SystemInfoCardProps> = ({ systemInfo }) => {
  const formatMemory = (memoryGB?: number) => {
    if (!memoryGB) return 'Unknown';
    return `${memoryGB} GB`;
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
          System Information
        </h3>
        
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {systemInfo.cpu_model && (
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Cpu className="h-5 w-5 text-blue-500 dark:text-blue-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">CPU</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{systemInfo.cpu_model}</p>
              </div>
            </div>
          )}

          {systemInfo.gpu_model && (
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Monitor className="h-5 w-5 text-green-500 dark:text-green-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">GPU</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{systemInfo.gpu_model}</p>
              </div>
            </div>
          )}

          {systemInfo.total_memory && (
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <HardDrive className="h-5 w-5 text-purple-500 dark:text-purple-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">Memory</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{formatMemory(systemInfo.total_memory)}</p>
              </div>
            </div>
          )}

          {systemInfo.os_info && (
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Monitor className="h-5 w-5 text-orange-500 dark:text-orange-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">Operating System</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{systemInfo.os_info}</p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-4 w-4 text-gray-400 dark:text-gray-500" />
            </div>
            <div className="ml-2">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Last updated: {formatDate(systemInfo.last_update)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemInfoCard;
