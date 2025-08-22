import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from app.models.hardware_models import MetricType, InsightLevel, TimeSeriesData, AnomalyEvent

# AsyncClient will be used in async test methods


class TestDashboardAPI:
    """Test suite for Dashboard API endpoints"""
    
    @pytest.fixture
    def mock_data_processor(self):
        """Mock DataProcessor for testing"""
        mock = Mock()
        mock.get_system_info.return_value = {
            'cpu_model': 'Intel Core i7-12700K',
            'gpu_model': 'NVIDIA RTX 3080',
            'total_memory': '32 GB',
            'os_info': 'Windows 11',
            'last_update': datetime.now().isoformat(),
            'total_files': 7,
            'date_range': '2024-01-15 to 2024-01-21',
            'monitoring_duration': '7 days',
            'data_points': 10080
        }
        return mock
    
    @pytest.fixture
    def mock_insights_engine(self):
        """Mock InsightsEngine for testing"""
        mock = Mock()
        mock.get_health_summary.return_value = {
            'overall_health': 'good',
            'insight_counts': {
                'critical': 0,
                'warning': 2,
                'info': 1,
                'success': 3
            },
            'total_insights': 6,
            'total_anomalies': 5,
            'critical_issues': 0,
            'warnings': 2,
            'recommendations': 6,
            'period': {
                'start_date': '2024-01-15',
                'end_date': '2024-01-21'
            }
        }
        return mock
    
    async def test_get_dashboard_overview_success(self, mock_data_processor, mock_insights_engine):
        """Test successful dashboard overview retrieval"""
        with patch('app.api.dashboard.data_processor', mock_data_processor):
            with patch('app.api.dashboard.insights_engine', mock_insights_engine):
                # Mock metrics data
                mock_data_processor.get_metrics_for_period.return_value = [
                    Mock(
                        metric_type=Mock(value='cpu_temperature'),
                        values=[65.0, 67.0, 69.0],
                        unit='°C'
                    ),
                    Mock(
                        metric_type=Mock(value='gpu_temperature'),
                        values=[75.0, 77.0, 79.0],
                        unit='°C'
                    )
                ]
                
                # Mock insights
                mock_insights_engine.analyze_period.return_value = [
                    Mock(
                        id='1',
                        title='Test Insight',
                        description='Test description',
                        level=Mock(value='warning'),
                        metric_type=Mock(value='cpu_temperature'),
                        component='cpu',
                        timestamp=datetime.now(),
                        recommendations=['Test recommendation']
                    )
                ]
                
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/dashboard/overview?days=7")
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert 'system_info' in data
                    assert 'overview' in data
                    assert 'health_summary' in data
                    assert 'recent_insights' in data
                    assert 'period' in data
                    
                    # Check overview structure
                    assert 'metrics' in data['overview']
                    assert 'data_points' in data['overview']
                    assert 'cpu_temperature' in data['overview']['metrics']
                    assert 'gpu_temperature' in data['overview']['metrics']
                    
                    # Check insights structure
                    assert 'insights' in data['recent_insights']
                    assert 'total_insights' in data['recent_insights']
    
    async def test_get_dashboard_overview_invalid_days(self):
        """Test dashboard overview with invalid days parameter"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/dashboard/overview?days=0")
            assert response.status_code == 422  # Validation error
            
            response = await client.get("/dashboard/overview?days=31")
            assert response.status_code == 422  # Validation error
    
    async def test_get_dashboard_overview_no_data(self, mock_data_processor, mock_insights_engine):
        """Test dashboard overview when no data is available"""
        with patch('app.api.dashboard.data_processor', mock_data_processor):
            with patch('app.api.dashboard.insights_engine', mock_insights_engine):
                # Mock no metrics data
                mock_data_processor.get_metrics_for_period.return_value = []
                mock_insights_engine.analyze_period.return_value = []
                
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/dashboard/overview?days=7")
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Should return empty overview
                    assert data['overview']['metrics'] == {}
                    assert data['overview']['data_points'] == 0
                    assert data['recent_insights']['insights'] == []
                    assert data['recent_insights']['total_insights'] == 0
    
    async def test_get_health_status_success(self, mock_insights_engine):
        """Test successful health status retrieval"""
        with patch('app.api.dashboard.insights_engine', mock_insights_engine):
            # Mock insights for health status
            mock_insights_engine.analyze_period.return_value = [
                Mock(
                    level=Mock(value='warning'),
                    metric_type=Mock(value='cpu_temperature')
                ),
                Mock(
                    level=Mock(value='success'),
                    metric_type=Mock(value='gpu_temperature')
                )
            ]
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/dashboard/health-status?start_date=2024-01-15&end_date=2024-01-21")
                
                assert response.status_code == 200
                data = response.json()
                
                assert 'overall_health' in data
                assert 'cpu_health' in data
                assert 'gpu_health' in data
                assert 'system_health' in data
                assert 'alerts' in data
    
    async def test_get_health_status_invalid_dates(self):
        """Test health status with invalid date formats"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/dashboard/health-status?start_date=invalid&end_date=2024-01-21")
            assert response.status_code == 400
        
        response = client.get("/dashboard/health-status?start_date=2024-01-15&end_date=invalid")
        assert response.status_code == 400
    
    def test_get_trends_analysis_success(self, mock_data_processor):
        """Test successful trends analysis"""
        with patch('app.api.dashboard.data_processor', mock_data_processor):
            # Mock metrics data with trend
            mock_data_processor.get_metrics_for_period.return_value = [
                Mock(
                    metric_type=Mock(value='cpu_temperature'),
                    values=[60.0, 62.0, 64.0, 66.0, 68.0],  # Increasing trend
                    unit='°C'
                )
            ]
            
            response = client.get("/dashboard/trends?start_date=2024-01-15&end_date=2024-01-21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'trends' in data
            assert 'period' in data
            assert 'metrics_analyzed' in data
            assert 'cpu_temperature' in data['trends']
            
            trend = data['trends']['cpu_temperature']
            assert 'direction' in trend
            assert 'strength' in trend
            assert 'slope' in trend
    
    def test_get_performance_summary_success(self, mock_data_processor):
        """Test successful performance summary"""
        with patch('app.api.dashboard.data_processor', mock_data_processor):
            # Mock metrics data
            mock_data_processor.get_metrics_for_period.return_value = [
                Mock(
                    metric_type=Mock(value='cpu_temperature'),
                    values=[65.0, 67.0, 69.0],
                    unit='°C'
                )
            ]
            
            response = client.get("/dashboard/performance-summary?start_date=2024-01-15&end_date=2024-01-21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'performance_summary' in data
            assert 'period' in data
            assert 'overall_rating' in data
            assert 'cpu_temperature' in data['performance_summary']
            
            perf = data['performance_summary']['cpu_temperature']
            assert 'average' in perf
            assert 'maximum' in perf
            assert 'minimum' in perf
            assert 'rating' in perf
            assert 'unit' in perf
            assert 'data_points' in perf
    
    def test_test_insights_endpoint(self, mock_data_processor, mock_insights_engine):
        """Test the debug insights endpoint"""
        with patch('app.api.dashboard.data_processor', mock_data_processor):
            with patch('app.api.dashboard.insights_engine', mock_insights_engine):
                # Mock test data
                mock_data_processor.get_metrics_for_period.return_value = [
                    Mock(metric_type=Mock(value='cpu_temperature'))
                ]
                mock_insights_engine.analyze_period.return_value = [
                    Mock(
                        id='1',
                        title='Test Insight',
                        description='Test description',
                        level=Mock(value='warning'),
                        metric_type=Mock(value='cpu_temperature'),
                        component='cpu',
                        timestamp=datetime.now(),
                        recommendations=['Test recommendation']
                    )
                ]
                
                response = client.get("/dashboard/test-insights")
                
                assert response.status_code == 200
                data = response.json()
                
                assert 'test_period' in data
                assert 'metrics_count' in data
                assert 'insights_count' in data
                assert 'insights' in data


class TestInsightsAPI:
    """Test suite for Insights API endpoints"""
    
    @pytest.fixture
    def mock_insights_engine(self):
        """Mock InsightsEngine for testing"""
        mock = Mock()
        return mock
    
    def test_analyze_period_success(self, mock_insights_engine):
        """Test successful period analysis"""
        with patch('app.api.insights.insights_engine', mock_insights_engine):
            # Mock insights data
            mock_insights_engine.analyze_period.return_value = [
                Mock(
                    id='1',
                    title='Test Insight',
                    description='Test description',
                    level=Mock(value='warning'),
                    metric_type=Mock(value='cpu_temperature'),
                    component='cpu',
                    timestamp=datetime.now(),
                    recommendations=['Test recommendation'],
                    events=[],
                    period_start=datetime(2024, 1, 15),
                    period_end=datetime(2024, 1, 21),
                    anomaly_count=0,
                    baseline_stats={}
                )
            ]
            
            response = client.get("/insights/analyze?start_date=2024-01-15&end_date=2024-01-21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'insights' in data
            assert 'summary' in data
            assert len(data['insights']) == 1
            
            insight = data['insights'][0]
            assert 'id' in insight
            assert 'title' in insight
            assert 'description' in insight
            assert 'level' in insight
            assert 'metric_type' in insight
            assert 'component' in insight
            assert 'timestamp' in insight
            assert 'recommendations' in insight
            assert 'events' in insight
            assert 'period_start' in insight
            assert 'period_end' in insight
            assert 'anomaly_count' in insight
            assert 'baseline_stats' in insight
    
    def test_analyze_period_invalid_dates(self):
        """Test period analysis with invalid dates"""
        response = client.get("/insights/analyze?start_date=invalid&end_date=2024-01-21")
        assert response.status_code == 400
        
        response = client.get("/insights/analyze?start_date=2024-01-15&end_date=invalid")
        assert response.status_code == 400
    
    def test_get_health_summary_success(self, mock_insights_engine):
        """Test successful health summary retrieval"""
        with patch('app.api.insights.insights_engine', mock_insights_engine):
            # Mock health summary
            mock_insights_engine.get_health_summary.return_value = {
                'overall_health': 'good',
                'insight_counts': {
                    'critical': 0,
                    'warning': 2,
                    'info': 1,
                    'success': 3
                },
                'total_insights': 6,
                'total_anomalies': 5,
                'critical_issues': 0,
                'warnings': 2,
                'recommendations': 6,
                'period': {
                    'start_date': '2024-01-15',
                    'end_date': '2024-01-21'
                }
            }
            
            response = client.get("/insights/health-summary?start_date=2024-01-15&end_date=2024-01-21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'overall_health' in data
            assert 'insight_counts' in data
            assert 'total_insights' in data
            assert 'total_anomalies' in data
            assert 'period' in data
    
    def test_get_insights_by_metric_success(self, mock_insights_engine):
        """Test successful insights retrieval by metric"""
        with patch('app.api.insights.insights_engine', mock_insights_engine):
            # Mock filtered insights
            mock_insights_engine.analyze_period.return_value = [
                Mock(
                    id='1',
                    title='CPU Temperature Insight',
                    description='High CPU temperature detected',
                    level=Mock(value='warning'),
                    metric_type=Mock(value='cpu_temperature'),
                    component='cpu',
                    timestamp=datetime.now(),
                    recommendations=['Check cooling'],
                    events=[],
                    period_start=datetime(2024, 1, 15),
                    period_end=datetime(2024, 1, 21),
                    anomaly_count=0,
                    baseline_stats={}
                )
            ]
            
            response = client.get("/insights/by-metric/cpu_temperature?start_date=2024-01-15&end_date=2024-01-21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'insights' in data
            assert len(data['insights']) == 1
            assert data['insights'][0]['metric_type'] == 'cpu_temperature'
    
    def test_get_insights_by_level_success(self, mock_insights_engine):
        """Test successful insights retrieval by level"""
        with patch('app.api.insights.insights_engine', mock_insights_engine):
            # Mock filtered insights
            mock_insights_engine.analyze_period.return_value = [
                Mock(
                    id='1',
                    title='Warning Insight',
                    description='Warning level insight',
                    level=Mock(value='warning'),
                    metric_type=Mock(value='cpu_temperature'),
                    component='cpu',
                    timestamp=datetime.now(),
                    recommendations=['Take action'],
                    events=[],
                    period_start=datetime(2024, 1, 15),
                    period_end=datetime(2024, 1, 21),
                    anomaly_count=0,
                    baseline_stats={}
                )
            ]
            
            response = client.get("/insights/by-level/warning?start_date=2024-01-15&end_date=2024-01-21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'insights' in data
            assert len(data['insights']) == 1
            assert data['insights'][0]['level'] == 'warning'


class TestMetricsAPI:
    """Test suite for Metrics API endpoints"""
    
    @pytest.fixture
    def mock_data_processor(self):
        """Mock DataProcessor for testing"""
        mock = Mock()
        return mock
    
    def test_get_metrics_for_period_success(self, mock_data_processor):
        """Test successful metrics retrieval for period"""
        with patch('app.api.metrics.data_processor', mock_data_processor):
            # Mock metrics data
            mock_data_processor.get_metrics_for_period.return_value = [
                Mock(
                    timestamps=[datetime.now()],
                    values=[65.0],
                    metric_type=Mock(value='cpu_temperature'),
                    component='cpu',
                    unit='°C'
                )
            ]
            
            response = client.get("/metrics/period?start_date=2024-01-15&end_date=2024-01-21&metric_types=cpu_temperature")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'data' in data
            assert 'time_range' in data
            assert 'total_records' in data
            assert len(data['data']) == 1
            
            metric = data['data'][0]
            assert 'timestamps' in metric
            assert 'values' in metric
            assert 'metric_type' in metric
            assert 'component' in metric
            assert 'unit' in metric
    
    def test_get_metrics_for_period_invalid_dates(self):
        """Test metrics retrieval with invalid dates"""
        response = client.get("/metrics/period?start_date=invalid&end_date=2024-01-21&metric_types=cpu_temperature")
        assert response.status_code == 400
        
        response = client.get("/metrics/period?start_date=2024-01-15&end_date=invalid&metric_types=cpu_temperature")
        assert response.status_code == 400
    
    def test_get_system_info_success(self, mock_data_processor):
        """Test successful system info retrieval"""
        with patch('app.api.metrics.data_processor', mock_data_processor):
            # Mock system info
            mock_data_processor.get_system_info.return_value = {
                'cpu_model': 'Intel Core i7-12700K',
                'gpu_model': 'NVIDIA RTX 3080',
                'total_memory': '32 GB',
                'os_info': 'Windows 11',
                'last_update': datetime.now().isoformat(),
                'total_files': 7,
                'date_range': '2024-01-15 to 2024-01-21',
                'monitoring_duration': '7 days',
                'data_points': 10080
            }
            
            response = client.get("/metrics/system-info")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'cpu_model' in data
            assert 'gpu_model' in data
            assert 'total_memory' in data
            assert 'os_info' in data
            assert 'last_update' in data
            assert 'total_files' in data
            assert 'date_range' in data
            assert 'monitoring_duration' in data
            assert 'data_points' in data
    
    def test_get_available_dates_success(self, mock_data_processor):
        """Test successful available dates retrieval"""
        with patch('app.api.metrics.data_processor', mock_data_processor):
            # Mock available dates
            mock_data_processor.get_available_dates.return_value = [
                '2024-01-15',
                '2024-01-16',
                '2024-01-17'
            ]
            
            response = client.get("/metrics/available-dates")
            
            assert response.status_code == 200
            data = response.json()
            
            assert 'dates' in data
            assert len(data['dates']) == 3
            assert '2024-01-15' in data['dates']
            assert '2024-01-16' in data['dates']
            assert '2024-01-17' in data['dates']


class TestErrorHandling:
    """Test suite for API error handling"""
    
    def test_internal_server_error_handling(self):
        """Test handling of internal server errors"""
        with patch('app.api.dashboard.data_processor') as mock_dp:
            # Mock an exception
            mock_dp.get_system_info.side_effect = Exception("Test error")
            
            response = client.get("/dashboard/overview?days=7")
            
            assert response.status_code == 500
            data = response.json()
            assert 'detail' in data
            assert 'Error generating dashboard overview' in data['detail']
    
    def test_not_found_error_handling(self):
        """Test handling of not found errors"""
        with patch('app.api.dashboard.data_processor') as mock_dp:
            # Mock no data found
            mock_dp.get_metrics_for_period.return_value = []
            mock_dp.get_system_info.return_value = {}
            
            response = client.get("/dashboard/overview?days=7")
            
            # Should return 200 with empty data, not 404
            assert response.status_code == 200
            data = response.json()
            assert data['overview']['metrics'] == {}


if __name__ == "__main__":
    pytest.main([__file__])
