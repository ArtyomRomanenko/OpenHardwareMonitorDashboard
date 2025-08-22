import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.insights_engine import InsightsEngine
from app.models.hardware_models import (
    MetricType, InsightLevel, TimeSeriesData, AnomalyEvent
)


class TestInsightsEngine:
    """Test suite for the enhanced InsightsEngine with anomaly detection"""
    
    @pytest.fixture
    def insights_engine(self):
        """Create a fresh InsightsEngine instance for each test"""
        return InsightsEngine()
    
    @pytest.fixture
    def sample_temperature_data(self):
        """Create sample temperature data with some anomalies"""
        # Create timestamps for a day
        base_time = datetime(2024, 1, 15, 0, 0, 0)
        timestamps = [base_time + timedelta(minutes=i*5) for i in range(288)]  # 24 hours, 5-min intervals
        
        # Create normal temperature values (60-75°C) with some anomalies
        np.random.seed(42)  # For reproducible tests
        normal_temps = np.random.normal(67.5, 5, 280)  # 280 normal values
        normal_temps = np.clip(normal_temps, 60, 75)
        
        # Add some anomalies
        anomalies = [95.0, 98.0, 45.0, 100.0, 35.0]  # High and low anomalies
        anomaly_positions = [50, 100, 150, 200, 250]
        
        values = list(normal_temps)
        for pos, anomaly in zip(anomaly_positions, anomalies):
            values.insert(pos, anomaly)
        
        return TimeSeriesData(
            timestamps=timestamps[:len(values)],
            values=values,
            metric_type=MetricType.CPU_TEMP,
            component="cpu",
            unit="°C"
        )
    
    @pytest.fixture
    def sample_usage_data(self):
        """Create sample CPU usage data"""
        base_time = datetime(2024, 1, 15, 0, 0, 0)
        timestamps = [base_time + timedelta(minutes=i*5) for i in range(100)]
        
        # Normal usage pattern with some spikes
        np.random.seed(42)
        values = np.random.normal(45, 15, 100)
        values = np.clip(values, 5, 95)
        
        # Add some high usage spikes
        values[30:35] = [90, 92, 95, 93, 91]
        values[70:75] = [88, 90, 94, 89, 87]
        
        return TimeSeriesData(
            timestamps=timestamps,
            values=values.tolist(),
            metric_type=MetricType.CPU_USAGE,
            component="cpu",
            unit="%"
        )
    
    @pytest.fixture
    def mock_data_processor(self):
        """Mock DataProcessor for testing"""
        mock = Mock()
        mock.get_metrics_for_period.return_value = []
        return mock
    
    def test_insights_engine_initialization(self, insights_engine):
        """Test InsightsEngine initializes correctly with configuration"""
        assert insights_engine.anomaly_config is not None
        assert insights_engine.anomaly_config.z_score_threshold == 2.5
        assert insights_engine.anomaly_config.iqr_multiplier == 1.5
        assert insights_engine.anomaly_config.min_data_points == 10
        assert insights_engine.thresholds is not None
        assert MetricType.CPU_TEMP in insights_engine.thresholds
    
    def test_filter_data_to_period(self, insights_engine):
        """Test data filtering to exact date range"""
        # Create test data spanning multiple days
        base_time = datetime(2024, 1, 15, 12, 0, 0)
        timestamps = [
            base_time - timedelta(days=1),  # Before period
            base_time,                       # Start of period
            base_time + timedelta(hours=12), # Middle of period
            base_time + timedelta(days=1),   # End of period
            base_time + timedelta(days=2)    # After period
        ]
        
        test_data = TimeSeriesData(
            timestamps=timestamps,
            values=[10, 20, 30, 40, 50],
            metric_type=MetricType.CPU_TEMP,
            component="cpu",
            unit="°C"
        )
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 23, 59, 59)
        
        filtered = insights_engine._filter_data_to_period(test_data, start_dt, end_dt)
        
        assert len(filtered['values']) == 3
        assert filtered['values'] == [20, 30, 40]
        assert filtered['timestamps'] == [timestamps[1], timestamps[2], timestamps[3]]
    
    def test_anomaly_detection_z_score(self, insights_engine, sample_temperature_data):
        """Test Z-score based anomaly detection"""
        values = np.array(sample_temperature_data.values)
        timestamps = sample_temperature_data.timestamps
        
        anomalies = insights_engine._detect_anomalies(values, timestamps, MetricType.CPU_TEMP)
        
        # Should detect some anomalies
        assert len(anomalies) > 0
        
        # Check that anomalies have correct structure
        for anomaly in anomalies:
            assert isinstance(anomaly, AnomalyEvent)
            assert anomaly.timestamp in timestamps
            assert anomaly.value in values
            assert anomaly.severity in ['minor', 'moderate', 'severe']
            assert len(anomaly.expected_range) == 2
            assert anomaly.expected_range[0] < anomaly.expected_range[1]
    
    def test_anomaly_detection_iqr(self, insights_engine):
        """Test IQR based anomaly detection"""
        # Create data with clear outliers
        values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 100, 200])
        timestamps = [datetime.now() + timedelta(minutes=i) for i in range(len(values))]
        
        anomalies = insights_engine._detect_anomalies(values, timestamps, MetricType.CPU_USAGE)
        
        # Should detect the extreme outliers (100, 200)
        assert len(anomalies) >= 2
        
        anomaly_values = [a.value for a in anomalies]
        assert 100 in anomaly_values
        assert 200 in anomaly_values
    
    def test_anomaly_detection_threshold(self, insights_engine):
        """Test threshold-based anomaly detection for temperatures"""
        # Create data with values above critical threshold
        values = np.array([60, 70, 80, 90, 95, 100, 105])
        timestamps = [datetime.now() + timedelta(minutes=i) for i in range(len(values))]
        
        anomalies = insights_engine._detect_anomalies(values, timestamps, MetricType.CPU_TEMP)
        
        # Should detect values above critical threshold (default 100)
        critical_anomalies = [a for a in anomalies if a.value >= 100]
        assert len(critical_anomalies) >= 2  # 100, 105
    
    def test_remove_anomalies(self, insights_engine):
        """Test anomaly removal from dataset"""
        values = np.array([1, 2, 3, 100, 4, 5, 200, 6])
        anomalies = [
            AnomalyEvent(
                timestamp=datetime.now(),
                value=100,
                severity='moderate',
                description='Test anomaly',
                expected_range=(1, 10)
            ),
            AnomalyEvent(
                timestamp=datetime.now(),
                value=200,
                severity='severe',
                description='Test anomaly',
                expected_range=(1, 10)
            )
        ]
        
        clean_values = insights_engine._remove_anomalies(values, anomalies)
        
        # Should remove the anomalous values
        assert 100 not in clean_values
        assert 200 not in clean_values
        assert len(clean_values) == len(values) - 2
    
    def test_calculate_baseline_stats(self, insights_engine):
        """Test baseline statistics calculation"""
        values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
        stats = insights_engine._calculate_baseline_stats(values)
        
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'q25' in stats
        assert 'q75' in stats
        assert 'iqr' in stats
        
        assert stats['mean'] == 5.5
        assert stats['median'] == 5.5
        assert stats['min'] == 1.0
        assert stats['max'] == 10.0
        assert stats['q25'] == 3.25
        assert stats['q75'] == 7.75
        assert stats['iqr'] == 4.5
    
    def test_create_anomaly_insight(self, insights_engine, sample_temperature_data):
        """Test anomaly insight creation"""
        values = np.array(sample_temperature_data.values)
        timestamps = sample_temperature_data.timestamps
        
        anomalies = insights_engine._detect_anomalies(values, timestamps, MetricType.CPU_TEMP)
        baseline_stats = insights_engine._calculate_baseline_stats(values)
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insight = insights_engine._create_anomaly_insight(
            sample_temperature_data, anomalies, baseline_stats, start_dt, end_dt
        )
        
        assert insight.id is not None
        assert "Anomaly Detection" in insight.title
        assert insight.level in [InsightLevel.CRITICAL, InsightLevel.WARNING, InsightLevel.INFO]
        assert insight.metric_type == MetricType.CPU_TEMP
        assert insight.anomaly_count == len(anomalies)
        assert insight.events == anomalies
        assert insight.period_start == start_dt
        assert insight.period_end == end_dt
        assert insight.baseline_stats == baseline_stats
    
    def test_generate_threshold_insights(self, insights_engine, sample_temperature_data):
        """Test threshold-based insight generation"""
        values = np.array(sample_temperature_data.values)
        timestamps = sample_temperature_data.timestamps
        baseline_stats = insights_engine._calculate_baseline_stats(values)
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insights = insights_engine._generate_threshold_insights(
            sample_temperature_data, values, timestamps, baseline_stats,
            insights_engine.thresholds[MetricType.CPU_TEMP],
            start_dt, end_dt, False
        )
        
        # Should generate insights for high temperatures
        assert len(insights) > 0
        
        for insight in insights:
            assert insight.period_start == start_dt
            assert insight.period_end == end_dt
            assert insight.baseline_stats == baseline_stats
    
    def test_generate_performance_insights(self, insights_engine, sample_temperature_data):
        """Test performance insight generation"""
        values = np.array(sample_temperature_data.values)
        timestamps = sample_temperature_data.timestamps
        baseline_stats = insights_engine._calculate_baseline_stats(values)
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insights = insights_engine._generate_performance_insights(
            sample_temperature_data, values, timestamps, baseline_stats, start_dt, end_dt
        )
        
        # May or may not generate insights depending on data characteristics
        for insight in insights:
            assert insight.period_start == start_dt
            assert insight.period_end == end_dt
            assert insight.baseline_stats == baseline_stats
    
    def test_cross_metric_insights(self, insights_engine):
        """Test cross-metric insight generation"""
        # Create CPU and GPU temperature data
        base_time = datetime(2024, 1, 15, 12, 0, 0)
        timestamps = [base_time + timedelta(minutes=i*5) for i in range(100)]
        
        cpu_temps = TimeSeriesData(
            timestamps=timestamps,
            values=[80] * 100,  # High CPU temps
            metric_type=MetricType.CPU_TEMP,
            component="cpu",
            unit="°C"
        )
        
        gpu_temps = TimeSeriesData(
            timestamps=timestamps,
            values=[85] * 100,  # High GPU temps
            metric_type=MetricType.GPU_TEMP,
            component="gpu",
            unit="°C"
        )
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insights = insights_engine._generate_cross_metric_insights(
            [cpu_temps, gpu_temps], start_dt, end_dt
        )
        
        # Should generate insight about high system temperatures
        assert len(insights) > 0
        
        for insight in insights:
            assert insight.period_start == start_dt
            assert insight.period_end == end_dt
            assert insight.component == "system"
    
    def test_trend_analysis(self, insights_engine):
        """Test trend analysis and insight generation"""
        # Create data with clear increasing trend
        base_time = datetime(2024, 1, 15, 12, 0, 0)
        timestamps = [base_time + timedelta(minutes=i*5) for i in range(100)]
        
        # Increasing temperature trend
        values = [60 + i * 0.2 for i in range(100)]  # 60°C to 80°C
        
        temp_data = TimeSeriesData(
            timestamps=timestamps,
            values=values,
            metric_type=MetricType.CPU_TEMP,
            component="cpu",
            unit="°C"
        )
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insights = insights_engine._analyze_trends([temp_data], start_dt, end_dt)
        
        # Should detect increasing trend
        assert len(insights) > 0
        
        for insight in insights:
            assert insight.period_start == start_dt
            assert insight.period_end == end_dt
            assert 'trend_slope' in insight.data
    
    def test_analyze_period_with_anomalies(self, insights_engine, sample_temperature_data):
        """Test full period analysis with anomaly detection"""
        # Mock the data processor
        with patch.object(insights_engine, 'data_processor') as mock_dp:
            mock_dp.get_metrics_for_period.return_value = [sample_temperature_data]
            
            start_date = "2024-01-15"
            end_date = "2024-01-16"
            
            insights = insights_engine.analyze_period(start_date, end_date)
            
            # Should generate insights
            assert len(insights) > 0
            
            # Check that insights have period information
            for insight in insights:
                assert insight.period_start is not None
                assert insight.period_end is not None
    
    def test_health_summary_generation(self, insights_engine):
        """Test health summary generation"""
        start_date = "2024-01-15"
        end_date = "2024-01-16"
        
        # Mock the analyze_period method
        with patch.object(insights_engine, 'analyze_period') as mock_analyze:
            mock_insights = [
                Mock(level=InsightLevel.CRITICAL, anomaly_count=2),
                Mock(level=InsightLevel.WARNING, anomaly_count=1),
                Mock(level=InsightLevel.SUCCESS, anomaly_count=0),
                Mock(level=InsightLevel.INFO, anomaly_count=0),
            ]
            mock_analyze.return_value = mock_insights
            
            summary = insights_engine.get_health_summary(start_date, end_date)
            
            assert summary['overall_health'] == 'critical'
            assert summary['critical_issues'] == 1
            assert summary['warnings'] == 1
            assert summary['total_anomalies'] == 3
            assert 'period' in summary
            assert summary['period']['start_date'] == start_date
            assert summary['period']['end_date'] == end_date
    
    def test_insufficient_data_handling(self, insights_engine):
        """Test handling of insufficient data for analysis"""
        # Create data with too few points
        insufficient_data = TimeSeriesData(
            timestamps=[datetime.now() + timedelta(minutes=i) for i in range(5)],
            values=[1, 2, 3, 4, 5],
            metric_type=MetricType.CPU_TEMP,
            component="cpu",
            unit="°C"
        )
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insights = insights_engine._analyze_metric_with_anomalies(
            insufficient_data, start_dt, end_dt
        )
        
        # Should return no insights due to insufficient data
        assert len(insights) == 0
    
    def test_reliability_warning(self, insights_engine):
        """Test reliability warning when too many anomalies detected"""
        # Create data with mostly anomalies
        base_time = datetime(2024, 1, 15, 12, 0, 0)
        timestamps = [base_time + timedelta(minutes=i*5) for i in range(20)]
        
        # Create mostly anomalous values
        values = [100] * 15 + [60, 61, 62, 63, 64]  # 15 high temps, 5 normal
        
        temp_data = TimeSeriesData(
            timestamps=timestamps,
            values=values,
            metric_type=MetricType.CPU_TEMP,
            component="cpu",
            unit="°C"
        )
        
        start_dt = datetime(2024, 1, 15, 0, 0, 0)
        end_dt = datetime(2024, 1, 16, 0, 0, 0)
        
        insights = insights_engine._analyze_metric_with_anomalies(
            temp_data, start_dt, end_dt
        )
        
        # Should include reliability warning
        reliability_warnings = [i for i in insights if 'Data Reliability Warning' in i.title]
        assert len(reliability_warnings) > 0
    
    def test_anomaly_recommendations(self, insights_engine):
        """Test anomaly-specific recommendation generation"""
        # Test CPU temperature anomalies
        cpu_anomalies = [
            AnomalyEvent(
                timestamp=datetime.now(),
                value=95,
                severity='severe',
                description='High CPU temp',
                expected_range=(60, 80)
            )
        ]
        
        recommendations = insights_engine._get_anomaly_recommendations(
            MetricType.CPU_TEMP, cpu_anomalies
        )
        
        assert len(recommendations) > 0
        assert any('temperature' in rec.lower() for rec in recommendations)
        
        # Test CPU usage anomalies
        usage_anomalies = [
            AnomalyEvent(
                timestamp=datetime.now(),
                value=98,
                severity='moderate',
                description='High CPU usage',
                expected_range=(20, 80)
            )
        ]
        
        usage_recs = insights_engine._get_anomaly_recommendations(
            MetricType.CPU_USAGE, usage_anomalies
        )
        
        assert len(usage_recs) > 0
        assert any('application' in rec.lower() for rec in usage_recs)


if __name__ == "__main__":
    pytest.main([__file__])
