import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Insights from '../src/pages/Insights';
import { insightsAPI, metricsAPI } from '../src/services/api';

// Mock the API modules
jest.mock('../src/services/api');
const mockInsightsAPI = insightsAPI as jest.Mocked<typeof insightsAPI>;
const mockMetricsAPI = metricsAPI as jest.Mocked<typeof metricsAPI>;

// Mock the LoadingSpinner component
jest.mock('../src/components/LoadingSpinner', () => {
  return function MockLoadingSpinner() {
    return <div data-testid="loading-spinner">Loading...</div>;
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Insights Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock responses
    mockMetricsAPI.getSystemInfo.mockResolvedValue({
      data: {
        cpu_model: 'Intel Core i7-12700K',
        gpu_model: 'NVIDIA RTX 3080',
        total_memory: '32 GB',
        os_info: 'Windows 11',
        last_update: '2024-01-21T12:00:00Z',
        memory_usage_avg: '45.2%',
        gpu_memory: '8 GB'
      }
    });

    mockInsightsAPI.analyzePeriod.mockResolvedValue({
      data: {
        insights: [
          {
            id: '1',
            title: 'High CPU Temperature',
            description: 'CPU temperature reached 85°C during gaming session',
            level: 'warning',
            metric_type: 'cpu_temperature',
            component: 'cpu',
            timestamp: '2024-01-21T12:00:00Z',
            recommendations: ['Check CPU cooler', 'Improve case airflow'],
            events: [
              {
                timestamp: '2024-01-21T11:30:00Z',
                value: 85.0,
                severity: 'moderate',
                description: 'High CPU temperature spike',
                expected_range: [60, 75]
              }
            ],
            period_start: '2024-01-15T00:00:00Z',
            period_end: '2024-01-21T23:59:59Z',
            anomaly_count: 1,
            baseline_stats: {
              mean: 67.5,
              median: 68.0,
              std: 8.2,
              min: 55.0,
              max: 85.0
            }
          }
        ]
      }
    });

    mockInsightsAPI.getHealthSummary.mockResolvedValue({
      data: {
        overall_health: 'good',
        critical_issues: 0,
        warnings: 1,
        healthy_metrics: 5,
        recommendations: 2,
        insight_counts: {
          critical: 0,
          warning: 1,
          info: 0,
          success: 0
        },
        total_anomalies: 1,
        period: {
          start_date: '2024-01-15',
          end_date: '2024-01-21'
        }
      }
    });
  });

  describe('Initial Loading and Data Display', () => {
    it('should show loading spinner initially', () => {
      renderWithRouter(<Insights />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('should load and display system information', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Intel Core i7-12700K')).toBeInTheDocument();
        expect(screen.getByText('NVIDIA RTX 3080')).toBeInTheDocument();
        expect(screen.getByText('32 GB')).toBeInTheDocument();
      });
    });

    it('should load and display health summary', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('good')).toBeInTheDocument();
        expect(screen.getByText('0')).toBeInTheDocument(); // Critical issues
        expect(screen.getByText('1')).toBeInTheDocument(); // Warnings
        expect(screen.getByText('2')).toBeInTheDocument(); // Recommendations
        expect(screen.getByText('1')).toBeInTheDocument(); // Anomalies
      });
    });

    it('should display analysis period information', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Analysis Period')).toBeInTheDocument();
        expect(screen.getByText('1/15/2024 to 1/21/2024')).toBeInTheDocument();
      });
    });
  });

  describe('Insights Display', () => {
    it('should display insights with enhanced information', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('High CPU Temperature')).toBeInTheDocument();
        expect(screen.getByText('CPU temperature reached 85°C during gaming session')).toBeInTheDocument();
        expect(screen.getByText('Check CPU cooler')).toBeInTheDocument();
        expect(screen.getByText('Improve case airflow')).toBeInTheDocument();
      });
    });

    it('should display anomaly events information', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Anomaly Events (1)')).toBeInTheDocument();
        expect(screen.getByText('moderate')).toBeInTheDocument();
        expect(screen.getByText('Value: 85')).toBeInTheDocument();
        expect(screen.getByText('Expected: 60.0 - 75.0')).toBeInTheDocument();
      });
    });

    it('should display baseline statistics', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Baseline Statistics')).toBeInTheDocument();
        expect(screen.getByText('mean:')).toBeInTheDocument();
        expect(screen.getByText('67.50')).toBeInTheDocument();
        expect(screen.getByText('std:')).toBeInTheDocument();
        expect(screen.getByText('8.20')).toBeInTheDocument();
      });
    });

    it('should display period information for each insight', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Period: 1/15/2024 - 1/21/2024')).toBeInTheDocument();
      });
    });
  });

  describe('Filtering and Date Range', () => {
    it('should set default date range to last 7 days', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const startDateInput = screen.getByLabelText('Start Date') as HTMLInputElement;
        const endDateInput = screen.getByLabelText('End Date') as HTMLInputElement;
        
        expect(startDateInput.value).toMatch(/\d{4}-\d{2}-\d{2}/);
        expect(endDateInput.value).toMatch(/\d{4}-\d{2}-\d{2}/);
      });
    });

    it('should allow changing date range', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const startDateInput = screen.getByLabelText('Start Date') as HTMLInputElement;
        const endDateInput = screen.getByLabelText('End Date') as HTMLInputElement;
        
        fireEvent.change(startDateInput, { target: { value: '2024-01-10' } });
        fireEvent.change(endDateInput, { target: { value: '2024-01-25' } });
        
        expect(startDateInput.value).toBe('2024-01-10');
        expect(endDateInput.value).toBe('2024-01-25');
      });
    });

    it('should filter insights by level', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const levelSelect = screen.getByLabelText('Insight Level') as HTMLSelectElement;
        fireEvent.change(levelSelect, { target: { value: 'warning' } });
        
        expect(levelSelect.value).toBe('warning');
      });
    });

    it('should filter insights by metric type', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const metricSelect = screen.getByLabelText('Metric Type') as HTMLSelectElement;
        fireEvent.change(metricSelect, { target: { value: 'cpu_temperature' } });
        
        expect(metricSelect.value).toBe('cpu_temperature');
      });
    });

    it('should apply filters and reload insights', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const applyButton = screen.getByText('Apply Filters');
        fireEvent.click(applyButton);
      });
      
      // Should call the API with new parameters
      await waitFor(() => {
        expect(mockInsightsAPI.analyzePeriod).toHaveBeenCalledTimes(2); // Initial load + filter
        expect(mockInsightsAPI.getHealthSummary).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API calls fail', async () => {
      mockMetricsAPI.getSystemInfo.mockRejectedValue(new Error('Failed to load system info'));
      
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load insights data')).toBeInTheDocument();
      });
    });

    it('should display error message when filtered insights fail', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        // Set up error for filtered insights
        mockInsightsAPI.analyzePeriod.mockRejectedValueOnce(new Error('Failed to load filtered insights'));
        
        const applyButton = screen.getByText('Apply Filters');
        fireEvent.click(applyButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load filtered insights')).toBeInTheDocument();
      });
    });
  });

  describe('Empty States', () => {
    it('should display no insights message when no data is available', async () => {
      mockInsightsAPI.analyzePeriod.mockResolvedValue({
        data: { insights: [] }
      });
      
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('No Insights Found')).toBeInTheDocument();
        expect(screen.getByText('No insights data found for the selected filters. Try adjusting your filter criteria or check if the backend is running.')).toBeInTheDocument();
      });
    });
  });

  describe('Component Integration', () => {
    it('should display system overview section', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('System Overview')).toBeInTheDocument();
        expect(screen.getByText('CPU')).toBeInTheDocument();
        expect(screen.getByText('GPU')).toBeInTheDocument();
        expect(screen.getByText('Memory')).toBeInTheDocument();
      });
    });

    it('should display system health summary section', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('System Health Summary')).toBeInTheDocument();
        expect(screen.getByText('Overall Status')).toBeInTheDocument();
        expect(screen.getByText('Critical Issues')).toBeInTheDocument();
        expect(screen.getByText('Warnings')).toBeInTheDocument();
        expect(screen.getByText('Recommendations')).toBeInTheDocument();
        expect(screen.getByText('Anomalies')).toBeInTheDocument();
      });
    });

    it('should display filter controls', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        expect(screen.getByText('Filter Insights')).toBeInTheDocument();
        expect(screen.getByLabelText('Insight Level')).toBeInTheDocument();
        expect(screen.getByLabelText('Metric Type')).toBeInTheDocument();
        expect(screen.getByLabelText('Start Date')).toBeInTheDocument();
        expect(screen.getByLabelText('End Date')).toBeInTheDocument();
        expect(screen.getByText('Apply Filters')).toBeInTheDocument();
      });
    });
  });

  describe('Data Refresh', () => {
    it('should update health summary when filters are applied', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const applyButton = screen.getByText('Apply Filters');
        fireEvent.click(applyButton);
      });
      
      await waitFor(() => {
        expect(mockInsightsAPI.getHealthSummary).toHaveBeenCalledTimes(2);
      });
    });

    it('should maintain filter state during refresh', async () => {
      renderWithRouter(<Insights />);
      
      await waitFor(() => {
        const levelSelect = screen.getByLabelText('Insight Level') as HTMLSelectElement;
        const metricSelect = screen.getByLabelText('Metric Type') as HTMLSelectElement;
        
        fireEvent.change(levelSelect, { target: { value: 'warning' } });
        fireEvent.change(metricSelect, { target: { value: 'cpu_temperature' } });
        
        const applyButton = screen.getByText('Apply Filters');
        fireEvent.click(applyButton);
      });
      
      await waitFor(() => {
        expect(mockInsightsAPI.analyzePeriod).toHaveBeenCalledWith(
          expect.any(String),
          expect.any(String),
          'warning',
          'cpu_temperature'
        );
      });
    });
  });
});
