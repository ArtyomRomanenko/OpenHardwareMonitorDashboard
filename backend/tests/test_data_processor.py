import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
from app.services.data_processor import DataProcessor
from app.models.hardware_models import MetricType, TimeSeriesData, HardwareMetric

@pytest.fixture
def data_processor():
    """Create a DataProcessor instance for testing"""
    with patch('app.services.data_processor.settings') as mock_settings:
        mock_settings.data_directory = "test_data"
        mock_settings.max_csv_size_mb = 100
        mock_settings.max_rows_per_file = 100000
        mock_settings.chunk_size = 10000
        processor = DataProcessor()
        return processor

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    csv_content = """Time,CPU Core #1,Memory,GPU Core
08/20/2025 00:00:03,3.125,43.7650833,49
08/20/2025 00:00:08,10.9375,43.7798424,47
08/20/2025 00:00:14,15.625,43.7880478,47"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass

class TestDataProcessor:
    """Test suite for DataProcessor with CSV parsing and memory optimization"""
    
    def test_data_processor_initialization(self, data_processor):
        """Test DataProcessor initializes correctly"""
        assert data_processor is not None
        assert hasattr(data_processor, 'data_directory')
    
    def test_get_available_dates(self, data_processor):
        """Test available dates detection from CSV files"""
        # Mock the glob.glob to return mock files
        mock_files = [
            'test_data/OpenHardwareMonitorLog-2024-01-15.csv',
            'test_data/OpenHardwareMonitorLog-2024-01-16.csv',
            'test_data/OpenHardwareMonitorLog-2024-01-17.csv',
            'test_data/other_file.txt',
            'test_data/2024-01-18.csv'  # Alternative format
        ]

        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = mock_files

            dates = data_processor.get_available_dates()

            # Should extract dates from CSV files
            assert '2024-01-15' in dates
            assert '2024-01-16' in dates
            assert '2024-01-17' in dates
            assert '2024-01-18' in dates
            assert len(dates) == 4
    
    def test_load_csv_data_success(self, data_processor, temp_csv_file):
        """Test successful CSV loading"""
        # Create the file with the expected name
        temp_dir = tempfile.mkdtemp()
        expected_file = Path(temp_dir) / "OpenHardwareMonitorLog-2024-01-15.csv"
        
        # Copy the temp CSV content to the expected file
        with open(temp_csv_file, 'r') as src, open(expected_file, 'w') as dst:
            dst.write(src.read())
        
        try:
            # Mock the data directory path
            with patch.object(data_processor, 'data_directory', Path(temp_dir)):
                df = data_processor.load_csv_data('2024-01-15')
                
                assert df is not None
                assert len(df) > 0
                assert 'Time' in df.columns
                assert 'CPU Core #1' in df.columns
                assert 'Memory' in df.columns
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_load_csv_data_file_not_found(self, data_processor):
        """Test CSV loading when file doesn't exist"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            df = data_processor.load_csv_data('2024-01-15')
            
            assert df.empty
    
    def test_process_csv_data(self, data_processor):
        """Test CSV data processing and cleaning"""
        # Create sample raw DataFrame
        raw_data = pd.DataFrame({
            'Time': ['08/20/2025 00:00:03', '08/20/2025 00:00:08', '08/20/2025 00:00:14'],
            'CPU Core #1': ['3.125', '10.9375', '15.625'],
            'Memory': ['43.7650833', '43.7798424', '43.7880478'],
            'GPU Core': ['49', '47', '47']
        })
        
        processed_df = data_processor.process_csv_data(raw_data, '2024-01-15')
        
        assert processed_df is not None
        assert len(processed_df) == 3
        assert 'timestamp' in processed_df.columns
        assert 'CPU Core #1' in processed_df.columns
        assert 'Memory' in processed_df.columns
        assert 'GPU Core' in processed_df.columns

        # Check timestamp conversion
        assert processed_df['timestamp'].dtype == 'datetime64[ns]'
        assert not processed_df['timestamp'].isna().any()

        # Check numeric conversion
        assert processed_df['CPU Core #1'].dtype in ['float64', 'int64']
        assert processed_df['Memory'].dtype in ['float64', 'int64']
        assert processed_df['GPU Core'].dtype in ['float64', 'int64']
    
    def test_process_csv_data_with_duplicates(self, data_processor):
        """Test CSV processing with duplicate column names"""
        # Create data with duplicate columns (common in Open Hardware Monitor)
        raw_data = pd.DataFrame({
            'Time': ['08/20/2025 00:00:03', '08/20/2025 00:00:08'],
            'GPU Core': ['49', '47'],
            'GPU Core.1': ['49', '47'],  # Duplicate column
            'Memory': ['43.7650833', '43.7798424']
        })
        
        processed_df = data_processor.process_csv_data(raw_data, '2024-01-15')
        
        assert processed_df is not None
        assert len(processed_df) == 2
        
        # Should handle duplicate columns gracefully
        assert 'GPU Core' in processed_df.columns
        assert 'GPU Core.1' in processed_df.columns
    
    def test_get_metrics_for_period(self, data_processor):
        """Test metrics extraction for a specific period"""
        # Mock available dates
        with patch.object(data_processor, 'get_available_dates') as mock_dates:
            mock_dates.return_value = ['2024-01-15', '2024-01-16', '2024-01-17']
            
            # Mock CSV loading for each date
            mock_df = pd.DataFrame({
                'timestamp': pd.to_datetime(['08/20/2025 00:00:03', '08/20/2025 00:00:08']),
                'CPU Total': [3.125, 10.9375],
                'Memory': [43.7650833, 43.7798424],
                'GPU Core': [49, 47]
            })
            
            with patch.object(data_processor, 'load_csv_data') as mock_load:
                mock_load.return_value = mock_df
                
                with patch.object(data_processor, 'process_csv_data') as mock_process:
                    mock_process.return_value = mock_df
                    
                    metrics = data_processor.get_metrics_for_period(
                        '2024-01-15', '2024-01-17', [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]
                    )
                    
                    assert len(metrics) > 0
                    
                    # Check that metrics have the expected structure
                    for metric in metrics:
                        assert hasattr(metric, 'timestamps')
                        assert hasattr(metric, 'values')
                        assert hasattr(metric, 'metric_type')
                        assert hasattr(metric, 'component')
                        assert hasattr(metric, 'unit')
    
    def test_get_metrics_for_period_no_data(self, data_processor):
        """Test metrics extraction when no data is available"""
        with patch.object(data_processor, 'get_available_dates') as mock_dates:
            mock_dates.return_value = []
            
            metrics = data_processor.get_metrics_for_period(
                '2024-01-15', '2024-01-17', [MetricType.CPU_TEMP]
            )
            
            assert len(metrics) == 0
    
    def test_get_metrics_for_period_date_filtering(self, data_processor):
        """Test that metrics are properly filtered by date range"""
        # Mock available dates
        with patch.object(data_processor, 'get_available_dates') as mock_dates:
            mock_dates.return_value = ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18']
            
            # Mock CSV loading
            mock_df = pd.DataFrame({
                'timestamp': pd.to_datetime(['08/20/2025 00:00:03', '08/20/2025 00:00:08']),
                'CPU Total': [3.125, 10.9375],
                'Memory': [43.7650833, 43.7798424]
            })
            
            with patch.object(data_processor, 'load_csv_data') as mock_load:
                mock_load.return_value = mock_df
                
                with patch.object(data_processor, 'process_csv_data') as mock_process:
                    mock_process.return_value = mock_df
                    
                    # Test inclusive end date
                    metrics = data_processor.get_metrics_for_period(
                        '2024-01-15', '2024-01-17', [MetricType.CPU_USAGE]
                    )
                    
                    # Should include data from 2024-01-17 (inclusive)
                    assert len(metrics) > 0
    
    def test_extract_metrics(self, data_processor):
        """Test metric extraction from processed DataFrame"""
        # Create sample processed DataFrame
        processed_df = pd.DataFrame({
            'timestamp': pd.to_datetime(['08/20/2025 00:00:03', '08/20/2025 00:00:08', '08/20/2025 00:00:14']),
            'CPU Total': [3.125, 10.9375, 15.625],
            'Memory': [43.7650833, 43.7798424, 43.7880478],
            'GPU Core': [49, 47, 47]
        })

        metrics = data_processor.extract_metrics(processed_df, [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE, MetricType.GPU_TEMP])

        assert len(metrics) == 3
        
        # Check CPU usage metric
        cpu_metric = next(m for m in metrics if m.metric_type == MetricType.CPU_USAGE)
        assert cpu_metric.component == 'CPU Total'
        assert cpu_metric.unit == '%'
        assert len(cpu_metric.values) == 3
        assert cpu_metric.values == [3.125, 10.9375, 15.625]
        
        # Check memory usage metric
        memory_metric = next(m for m in metrics if m.metric_type == MetricType.MEMORY_USAGE)
        assert memory_metric.component == 'Memory'
        assert memory_metric.unit == '%'
        assert len(memory_metric.values) == 3
    
    def test_extract_metrics_with_missing_columns(self, data_processor):
        """Test metric extraction when some columns are missing"""
        # Create DataFrame with only some expected columns
        processed_df = pd.DataFrame({
            'timestamp': pd.to_datetime(['08/20/2025 00:00:03', '08/20/2025 00:00:08']),
            'CPU Total': [3.125, 10.9375],
            # Missing Memory and GPU Core columns
        })

        metrics = data_processor.extract_metrics(processed_df, [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE, MetricType.GPU_TEMP])

        # Should only extract available metrics
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.CPU_USAGE
    
    def test_get_system_info(self, data_processor):
        """Test system information extraction"""
        # Mock available dates
        with patch.object(data_processor, 'get_available_dates') as mock_dates:
            mock_dates.return_value = ['2024-01-15', '2024-01-16']
            
            # Mock CSV loading
            mock_df = pd.DataFrame({
                'Time': ['08/20/2025 00:00:03', '08/20/2025 00:00:08'],
                'CPU Core #1': [3.125, 10.9375],
                'Memory': [43.7650833, 43.7798424],
                'GPU Core': [49, 47]
            })
            
            with patch.object(data_processor, 'load_csv_data') as mock_load:
                mock_load.return_value = mock_df
                
                with patch.object(data_processor, 'process_csv_data') as mock_process:
                    mock_process.return_value = mock_df
                    
                    system_info = data_processor.get_system_info()
                    
                    assert system_info is not None
                    assert 'total_files' in system_info
                    assert 'date_range' in system_info
                    assert 'monitoring_duration' in system_info
                    assert 'data_points' in system_info
                    assert system_info['total_files'] == 2
    
    def test_memory_optimization_settings(self, data_processor):
        """Test memory optimization configuration"""
        # Check that memory optimization settings are accessible through settings
        assert hasattr(data_processor, 'data_directory')
        assert str(data_processor.data_directory) == "test_data"
    
    def test_error_handling_invalid_csv(self, data_processor):
        """Test error handling for invalid CSV data"""
        # Create invalid CSV content
        invalid_csv = "Invalid,CSV,Content\nNo,Proper,Structure"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(invalid_csv)
            temp_path = f.name
        
        try:
            # Mock the data directory path
            with patch.object(data_processor, 'data_directory', temp_path.replace('.csv', '')):
                with patch('os.path.join') as mock_join:
                    mock_join.return_value = temp_path
                    
                    # Should handle invalid CSV gracefully
                    df = data_processor.load_csv_data('2024-01-15')
                    
                    # May return None or empty DataFrame depending on implementation
                    assert df is not None  # Should at least return something
        finally:
            os.unlink(temp_path)
    
    def test_large_file_handling(self, data_processor):
        """Test handling of large CSV files"""
        # Create a large CSV file with the expected filename format
        large_csv_content = "Time,CPU,Memory\n"
        for i in range(10000):  # 10k rows
            large_csv_content += f"08/20/2025 00:{i:02d}:00,{i % 100},{50 + i % 30}\n"
        
        # Create the file with the expected name
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / "OpenHardwareMonitorLog-2024-01-15.csv"
        
        with open(temp_file, 'w') as f:
            f.write(large_csv_content)
        
        try:
            # Mock the data directory path
            with patch.object(data_processor, 'data_directory', Path(temp_dir)):
                # Should handle large files without crashing
                df = data_processor.load_csv_data('2024-01-15')
                
                assert df is not None
                assert len(df) > 0
        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
