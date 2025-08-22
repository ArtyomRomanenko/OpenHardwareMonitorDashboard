import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import uuid
from scipy import stats
from app.models.hardware_models import (
    HardwareInsight, InsightLevel, MetricType, TimeSeriesData, 
    AnomalyEvent, AnomalyDetectionConfig
)
from app.core.config import settings
from app.services.data_processor import DataProcessor

class InsightsEngine:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.anomaly_config = AnomalyDetectionConfig()
        
        # Hardware thresholds and benchmarks
        self.thresholds = {
            MetricType.CPU_TEMP: {
                'warning': settings.cpu_temp_warning,
                'critical': settings.cpu_temp_critical,
                'optimal_max': 70.0,
                'unit': '°C'
            },
            MetricType.GPU_TEMP: {
                'warning': settings.gpu_temp_warning,
                'critical': settings.gpu_temp_critical,
                'optimal_max': 75.0,
                'unit': '°C'
            },
            MetricType.CPU_USAGE: {
                'warning': 90.0,
                'critical': 95.0,
                'optimal_max': 80.0,
                'unit': '%'
            },
            MetricType.GPU_USAGE: {
                'warning': 95.0,
                'critical': 98.0,
                'optimal_max': 85.0,
                'unit': '%'
            },
            MetricType.MEMORY_USAGE: {
                'warning': 85.0,
                'critical': 95.0,
                'optimal_max': 75.0,
                'unit': '%'
            },
            MetricType.DISK_USAGE: {
                'warning': 85.0,
                'critical': 95.0,
                'optimal_max': 80.0,
                'unit': '%'
            }
        }
        
        # CPU model specific recommendations
        self.cpu_recommendations = {
            'intel': {
                'high_temp_threshold': 85.0,
                'recommendations': [
                    "Consider improving CPU cooling with better thermal paste",
                    "Check if CPU cooler is properly seated",
                    "Ensure adequate case airflow",
                    "Monitor for thermal throttling"
                ]
            },
            'amd': {
                'high_temp_threshold': 80.0,
                'recommendations': [
                    "AMD processors can run hotter, but monitor for stability",
                    "Check CPU cooler compatibility",
                    "Ensure proper thermal paste application",
                    "Monitor for performance degradation"
                ]
            }
        }
    
    def analyze_period(self, start_date: str, end_date: str) -> List[HardwareInsight]:
        """Analyze hardware data for a specific period and generate insights"""
        insights = []
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get all metrics for the period
        metrics_data = self.data_processor.get_metrics_for_period(start_date, end_date)
        
        if not metrics_data:
            return insights
        
        # Analyze each metric type with anomaly detection
        for metric_data in metrics_data:
            metric_insights = self._analyze_metric_with_anomalies(
                metric_data, start_dt, end_dt
            )
            insights.extend(metric_insights)
        
        # Generate cross-metric insights
        cross_insights = self._generate_cross_metric_insights(metrics_data, start_dt, end_dt)
        insights.extend(cross_insights)
        
        # Generate trend insights
        trend_insights = self._analyze_trends(metrics_data, start_dt, end_dt)
        insights.extend(trend_insights)
        
        return insights
    
    def _analyze_metric_with_anomalies(self, metric_data: TimeSeriesData, 
                                     start_dt: datetime, end_dt: datetime) -> List[HardwareInsight]:
        """Analyze a specific metric with anomaly detection and generate insights"""
        insights = []
        
        if len(metric_data.values) < self.anomaly_config.min_data_points:
            return insights
        
        # Filter data to exact date range
        filtered_data = self._filter_data_to_period(metric_data, start_dt, end_dt)
        if not filtered_data['values']:
            return insights
        
        values = np.array(filtered_data['values'])
        timestamps = filtered_data['timestamps']
        metric_type = metric_data.metric_type
        thresholds = self.thresholds.get(metric_type, {})
        
        # Detect anomalies and exclude them from baseline calculations
        anomalies = self._detect_anomalies(values, timestamps, metric_type)
        clean_values = self._remove_anomalies(values, anomalies)
        
        if len(clean_values) < self.anomaly_config.min_data_points:
            # If too many anomalies, use original data but mark as unreliable
            clean_values = values
            reliability_warning = True
        else:
            reliability_warning = False
        
        # Calculate baseline statistics from clean data
        baseline_stats = self._calculate_baseline_stats(clean_values)
        
        # Generate insights based on anomalies
        if anomalies:
            anomaly_insight = self._create_anomaly_insight(
                metric_data, anomalies, baseline_stats, start_dt, end_dt
            )
            insights.append(anomaly_insight)
        
        # Generate threshold-based insights
        threshold_insights = self._generate_threshold_insights(
            metric_data, clean_values, timestamps, baseline_stats, 
            thresholds, start_dt, end_dt, reliability_warning
        )
        insights.extend(threshold_insights)
        
        # Generate performance insights
        performance_insights = self._generate_performance_insights(
            metric_data, clean_values, timestamps, baseline_stats, 
            start_dt, end_dt
        )
        insights.extend(performance_insights)
        
        return insights
    
    def _filter_data_to_period(self, metric_data: TimeSeriesData, 
                              start_dt: datetime, end_dt: datetime) -> Dict[str, List]:
        """Filter data to exact date range"""
        filtered_values = []
        filtered_timestamps = []
        
        for i, timestamp in enumerate(metric_data.timestamps):
            if start_dt <= timestamp <= end_dt:
                filtered_values.append(metric_data.values[i])
                filtered_timestamps.append(timestamp)
        
        return {
            'values': filtered_values,
            'timestamps': filtered_timestamps
        }
    
    def _detect_anomalies(self, values: np.ndarray, timestamps: List[datetime], 
                          metric_type: MetricType) -> List[AnomalyEvent]:
        """Detect anomalies using multiple statistical methods"""
        anomalies = []
        
        if len(values) < self.anomaly_config.min_data_points:
            return anomalies
        
        # Method 1: Z-score based detection
        z_scores = np.abs(stats.zscore(values))
        z_anomaly_indices = np.where(z_scores > self.anomaly_config.z_score_threshold)[0]
        
        # Method 2: IQR based detection
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - self.anomaly_config.iqr_multiplier * iqr
        upper_bound = q3 + self.anomaly_config.iqr_multiplier * iqr
        iqr_anomaly_indices = np.where((values < lower_bound) | (values > upper_bound))[0]
        
        # Method 3: Threshold-based detection for critical metrics
        threshold_anomaly_indices = []
        if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
            thresholds = self.thresholds.get(metric_type, {})
            critical_threshold = thresholds.get('critical', 100)
            threshold_anomaly_indices = np.where(values >= critical_threshold)[0]
        
        # Combine all anomaly indices
        all_anomaly_indices = set(z_anomaly_indices) | set(iqr_anomaly_indices) | set(threshold_anomaly_indices)
        
        # Create anomaly events
        for idx in all_anomaly_indices:
            value = values[idx]
            timestamp = timestamps[idx]
            
            # Determine severity
            if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
                if value >= thresholds.get('critical', 100):
                    severity = 'severe'
                elif value >= thresholds.get('warning', 80):
                    severity = 'moderate'
                else:
                    severity = 'minor'
            else:
                if idx in z_anomaly_indices and idx in iqr_anomaly_indices:
                    severity = 'moderate'
                else:
                    severity = 'minor'
            
            # Calculate expected range
            if len(values) >= 10:
                expected_min = np.percentile(values, 5)
                expected_max = np.percentile(values, 95)
            else:
                expected_min = np.min(values)
                expected_max = np.max(values)
            
            anomaly_event = AnomalyEvent(
                timestamp=timestamp,
                value=float(value),
                severity=severity,
                description=f"Anomalous {metric_type.value.replace('_', ' ')} value detected",
                expected_range=(float(expected_min), float(expected_max))
            )
            anomalies.append(anomaly_event)
        
        return anomalies
    
    def _remove_anomalies(self, values: np.ndarray, anomalies: List[AnomalyEvent]) -> np.ndarray:
        """Remove anomalous values from the dataset"""
        if not anomalies:
            return values
        
        # Create mask for non-anomalous values
        anomaly_mask = np.ones(len(values), dtype=bool)
        for anomaly in anomalies:
            # Find the closest value to the anomaly
            closest_idx = np.argmin(np.abs(values - anomaly.value))
            if closest_idx < len(anomaly_mask):
                anomaly_mask[closest_idx] = False
        
        return values[anomaly_mask]
    
    def _calculate_baseline_stats(self, values: np.ndarray) -> Dict[str, float]:
        """Calculate baseline statistics from clean data"""
        if len(values) == 0:
            return {}
        
        return {
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'q25': float(np.percentile(values, 25)),
            'q75': float(np.percentile(values, 75)),
            'iqr': float(np.percentile(values, 75) - np.percentile(values, 25))
        }
    
    def _create_anomaly_insight(self, metric_data: TimeSeriesData, 
                               anomalies: List[AnomalyEvent], 
                               baseline_stats: Dict[str, float],
                               start_dt: datetime, end_dt: datetime) -> HardwareInsight:
        """Create insight for detected anomalies"""
        metric_type = metric_data.metric_type
        severity_counts = {}
        
        for anomaly in anomalies:
            severity_counts[anomaly.severity] = severity_counts.get(anomaly.severity, 0) + 1
        
        # Determine overall level
        if severity_counts.get('severe', 0) > 0:
            level = InsightLevel.CRITICAL
        elif severity_counts.get('moderate', 0) > 0:
            level = InsightLevel.WARNING
        else:
            level = InsightLevel.INFO
        
        # Create description
        total_anomalies = len(anomalies)
        severe_count = severity_counts.get('severe', 0)
        moderate_count = severity_counts.get('moderate', 0)
        
        description = f"Detected {total_anomalies} anomalous {metric_type.value.replace('_', ' ')} values "
        description += f"({severe_count} severe, {moderate_count} moderate) during the selected period. "
        description += f"Baseline: {baseline_stats.get('mean', 0):.1f} ± {baseline_stats.get('std', 0):.1f}"
        
        return HardwareInsight(
            id=str(uuid.uuid4()),
            title=f"Anomaly Detection - {metric_type.value.replace('_', ' ').title()}",
            description=description,
            level=level,
            metric_type=metric_type,
            component=metric_data.component,
            timestamp=datetime.now(),
            recommendations=self._get_anomaly_recommendations(metric_type, anomalies),
            data=baseline_stats,
            events=anomalies,
            period_start=start_dt,
            period_end=end_dt,
            anomaly_count=total_anomalies,
            baseline_stats=baseline_stats
        )
    
    def _generate_threshold_insights(self, metric_data: TimeSeriesData, 
                                   clean_values: np.ndarray, 
                                   timestamps: List[datetime],
                                   baseline_stats: Dict[str, float],
                                   thresholds: Dict, 
                                   start_dt: datetime, end_dt: datetime,
                                   reliability_warning: bool) -> List[HardwareInsight]:
        """Generate insights based on threshold violations"""
        insights = []
        metric_type = metric_data.metric_type
        
        if len(clean_values) == 0:
            return insights
        
        max_val = np.max(clean_values)
        mean_val = baseline_stats.get('mean', 0)
        
        # Check for critical temperatures
        if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
            if max_val >= thresholds.get('critical', 100):
                insights.append(self._create_threshold_insight(
                    f"Critical {metric_type.value.replace('_', ' ').title()}",
                    f"Maximum {metric_type.value.replace('_', ' ')} reached {max_val:.1f}°C during the period. "
                    f"Immediate action required to prevent hardware damage.",
                    InsightLevel.CRITICAL,
                    metric_data, start_dt, end_dt, baseline_stats,
                    recommendations=[
                        "Shutdown intensive applications immediately",
                        "Check cooling system functionality",
                        "Clean dust from heatsinks and fans",
                        "Consider hardware replacement if issue persists"
                    ]
                ))
            
            elif max_val >= thresholds.get('warning', 80):
                insights.append(self._create_threshold_insight(
                    f"High {metric_type.value.replace('_', ' ').title()}",
                    f"Maximum {metric_type.value.replace('_', ' ')} reached {max_val:.1f}°C during the period. "
                    f"Monitor closely and consider cooling improvements.",
                    InsightLevel.WARNING,
                    metric_data, start_dt, end_dt, baseline_stats,
                    recommendations=self._get_cooling_recommendations(metric_type)
                ))
        
        # Check for usage patterns
        if metric_type in [MetricType.CPU_USAGE, MetricType.GPU_USAGE, MetricType.MEMORY_USAGE]:
            if mean_val >= thresholds.get('warning', 90):
                insights.append(self._create_threshold_insight(
                    f"High {metric_type.value.replace('_', ' ').title()}",
                    f"Average {metric_type.value.replace('_', ' ')} is {mean_val:.1f}% during the period. "
                    f"Consider optimizing applications or upgrading hardware.",
                    InsightLevel.WARNING,
                    metric_data, start_dt, end_dt, baseline_stats,
                    recommendations=[
                        "Identify resource-intensive applications",
                        "Close unnecessary background processes",
                        "Consider hardware upgrade if usage is consistently high"
                    ]
                ))
        
        # Add reliability warning if needed
        if reliability_warning:
            insights.append(self._create_threshold_insight(
                f"Data Reliability Warning - {metric_type.value.replace('_', ' ').title()}",
                f"High number of anomalies detected. Analysis may not be reliable. "
                f"Consider selecting a different time period or investigating data quality.",
                InsightLevel.WARNING,
                metric_data, start_dt, end_dt, baseline_stats,
                recommendations=[
                    "Select a different time period",
                    "Check data source quality",
                    "Verify monitoring system functionality"
                ]
            ))
        
        return insights
    
    def _generate_performance_insights(self, metric_data: TimeSeriesData,
                                     clean_values: np.ndarray,
                                     timestamps: List[datetime],
                                     baseline_stats: Dict[str, float],
                                     start_dt: datetime, end_dt: datetime) -> List[HardwareInsight]:
        """Generate performance-related insights"""
        insights = []
        metric_type = metric_data.metric_type
        
        if len(clean_values) < 5:
            return insights
        
        mean_val = baseline_stats.get('mean', 0)
        std_val = baseline_stats.get('std', 0)
        
        # Check for unusual patterns
        if std_val > mean_val * 0.3:  # High variability
            insights.append(self._create_threshold_insight(
                f"Variable {metric_type.value.replace('_', ' ').title()}",
                f"{metric_type.value.replace('_', ' ').title()} shows high variability (std: {std_val:.1f}). "
                f"This may indicate inconsistent workload or cooling issues.",
                InsightLevel.INFO,
                metric_data, start_dt, end_dt, baseline_stats,
                recommendations=[
                    "Monitor for patterns in usage",
                    "Check for background processes causing spikes",
                    "Verify cooling system consistency"
                ]
            ))
        
        # Positive insights for good performance
        if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
            thresholds = self.thresholds.get(metric_type, {})
            if mean_val <= thresholds.get('optimal_max', 70):
                insights.append(self._create_threshold_insight(
                    f"Optimal {metric_type.value.replace('_', ' ').title()}",
                    f"Average {metric_type.value.replace('_', ' ')} is {mean_val:.1f}°C during the period. "
                    f"Your cooling system is working well.",
                    InsightLevel.SUCCESS,
                    metric_data, start_dt, end_dt, baseline_stats,
                    recommendations=[
                        "Maintain current cooling setup",
                        "Regular cleaning schedule is working",
                        "Continue monitoring for changes"
                    ]
                ))
        
        return insights
    
    def _create_threshold_insight(self, title: str, description: str, level: InsightLevel,
                                metric_data: TimeSeriesData, start_dt: datetime, end_dt: datetime,
                                baseline_stats: Dict[str, float], recommendations: List[str] = None) -> HardwareInsight:
        """Create a threshold-based insight"""
        return HardwareInsight(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            level=level,
            metric_type=metric_data.metric_type,
            component=metric_data.component,
            timestamp=datetime.now(),
            recommendations=recommendations or [],
            data=baseline_stats,
            events=[],
            period_start=start_dt,
            period_end=end_dt,
            anomaly_count=0,
            baseline_stats=baseline_stats
        )
    
    def _generate_cross_metric_insights(self, metrics_data: List[TimeSeriesData], 
                                      start_dt: datetime, end_dt: datetime) -> List[HardwareInsight]:
        """Generate insights based on relationships between different metrics"""
        insights = []
        
        # Find CPU and GPU temperature data
        cpu_temp_data = next((d for d in metrics_data if d.metric_type == MetricType.CPU_TEMP), None)
        gpu_temp_data = next((d for d in metrics_data if d.metric_type == MetricType.GPU_TEMP), None)
        cpu_usage_data = next((d for d in metrics_data if d.metric_type == MetricType.CPU_USAGE), None)
        
        if cpu_temp_data and gpu_temp_data:
            # Filter to exact period
            cpu_filtered = self._filter_data_to_period(cpu_temp_data, start_dt, end_dt)
            gpu_filtered = self._filter_data_to_period(gpu_temp_data, start_dt, end_dt)
            
            if cpu_filtered['values'] and gpu_filtered['values']:
                cpu_values = np.array(cpu_filtered['values'])
                gpu_values = np.array(gpu_filtered['values'])
                
                # Check if both are running hot
                if (np.mean(cpu_values) > 75 and np.mean(gpu_values) > 80):
                    insights.append(self._create_cross_metric_insight(
                        "High System Temperatures",
                        "Both CPU and GPU are running at elevated temperatures during the selected period. "
                        "This may indicate insufficient case airflow or cooling capacity.",
                        InsightLevel.WARNING,
                        [cpu_temp_data, gpu_temp_data], start_dt, end_dt,
                        recommendations=[
                            "Improve case airflow with additional fans",
                            "Check case ventilation and cable management",
                            "Consider upgrading to larger case with better airflow",
                            "Monitor ambient room temperature"
                        ]
                    ))
        
        if cpu_temp_data and cpu_usage_data:
            # Filter to exact period
            cpu_temp_filtered = self._filter_data_to_period(cpu_temp_data, start_dt, end_dt)
            cpu_usage_filtered = self._filter_data_to_period(cpu_usage_data, start_dt, end_dt)
            
            if cpu_temp_filtered['values'] and cpu_usage_filtered['values']:
                cpu_temp_values = np.array(cpu_temp_filtered['values'])
                cpu_usage_values = np.array(cpu_usage_filtered['values'])
                
                # Check for thermal throttling patterns
                high_usage_mask = cpu_usage_values > 80
                if np.any(high_usage_mask):
                    high_usage_temps = cpu_temp_values[high_usage_mask]
                    if np.mean(high_usage_temps) > 85:
                        insights.append(self._create_cross_metric_insight(
                            "Potential Thermal Throttling",
                            "CPU temperatures are very high during high usage periods in the selected range. "
                            "This may cause performance throttling.",
                            InsightLevel.WARNING,
                            [cpu_temp_data, cpu_usage_data], start_dt, end_dt,
                            recommendations=[
                                "Upgrade CPU cooler",
                                "Apply high-quality thermal paste",
                                "Check for proper cooler mounting",
                                "Consider undervolting if supported"
                            ]
                        ))
        
        return insights
    
    def _create_cross_metric_insight(self, title: str, description: str, level: InsightLevel,
                                   related_metrics: List[TimeSeriesData], 
                                   start_dt: datetime, end_dt: datetime,
                                   recommendations: List[str] = None) -> HardwareInsight:
        """Create a cross-metric insight"""
        return HardwareInsight(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            level=level,
            metric_type=related_metrics[0].metric_type,  # Use first metric type
            component="system",
            timestamp=datetime.now(),
            recommendations=recommendations or [],
            data={},
            events=[],
            period_start=start_dt,
            period_end=end_dt,
            anomaly_count=0,
            baseline_stats={}
        )
    
    def _analyze_trends(self, metrics_data: List[TimeSeriesData], 
                       start_dt: datetime, end_dt: datetime) -> List[HardwareInsight]:
        """Analyze trends in the data over time"""
        insights = []
        
        for metric_data in metrics_data:
            # Filter to exact period
            filtered_data = self._filter_data_to_period(metric_data, start_dt, end_dt)
            
            if len(filtered_data['values']) < 10:  # Need enough data points
                continue
            
            values = np.array(filtered_data['values'])
            
            # Calculate trend (simple linear regression)
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # Check for increasing trends in temperatures
            if metric_data.metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
                if slope > self.anomaly_config.trend_sensitivity:  # Increasing trend
                    insights.append(self._create_trend_insight(
                        f"Increasing {metric_data.metric_type.value.replace('_', ' ').title()} Trend",
                        f"{metric_data.metric_type.value.replace('_', ' ').title()} shows an increasing trend over the selected period. "
                        f"This may indicate deteriorating cooling performance.",
                        InsightLevel.WARNING,
                        metric_data, start_dt, end_dt, slope,
                        recommendations=[
                            "Clean dust from cooling components",
                            "Check thermal paste condition",
                            "Monitor fan speeds and noise",
                            "Consider preventive maintenance"
                        ]
                    ))
                
                elif slope < -self.anomaly_config.trend_sensitivity:  # Decreasing trend
                    insights.append(self._create_trend_insight(
                        f"Improving {metric_data.metric_type.value.replace('_', ' ').title()}",
                        f"{metric_data.metric_type.value.replace('_', ' ').title()} shows a decreasing trend over the selected period. "
                        f"Your cooling improvements are working well.",
                        InsightLevel.SUCCESS,
                        metric_data, start_dt, end_dt, slope,
                        recommendations=[
                            "Continue current maintenance routine",
                            "Document what changes led to improvement",
                            "Monitor for sustained improvement"
                        ]
                    ))
        
        return insights
    
    def _create_trend_insight(self, title: str, description: str, level: InsightLevel,
                            metric_data: TimeSeriesData, start_dt: datetime, end_dt: datetime,
                            slope: float, recommendations: List[str] = None) -> HardwareInsight:
        """Create a trend-based insight"""
        return HardwareInsight(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            level=level,
            metric_type=metric_data.metric_type,
            component=metric_data.component,
            timestamp=datetime.now(),
            recommendations=recommendations or [],
            data={'trend_slope': float(slope)},
            events=[],
            period_start=start_dt,
            period_end=end_dt,
            anomaly_count=0,
            baseline_stats={}
        )
    
    def _get_anomaly_recommendations(self, metric_type: MetricType, 
                                    anomalies: List[AnomalyEvent]) -> List[str]:
        """Get recommendations for anomaly events"""
        if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
            return [
                "Investigate the cause of temperature spikes",
                "Check for sudden workload changes",
                "Verify cooling system response",
                "Monitor for recurring patterns"
            ]
        elif metric_type in [MetricType.CPU_USAGE, MetricType.GPU_USAGE]:
            return [
                "Identify applications causing usage spikes",
                "Check for background processes",
                "Monitor system performance during anomalies",
                "Consider resource allocation optimization"
            ]
        else:
            return [
                "Investigate the cause of unusual values",
                "Check system stability during anomalies",
                "Monitor for patterns or correlations",
                "Verify sensor accuracy"
            ]
    
    def _get_cooling_recommendations(self, metric_type: MetricType) -> List[str]:
        """Get cooling-specific recommendations based on metric type"""
        if metric_type == MetricType.CPU_TEMP:
            return [
                "Clean CPU cooler and heatsink",
                "Reapply thermal paste",
                "Check CPU cooler mounting",
                "Improve case airflow",
                "Consider upgrading CPU cooler"
            ]
        elif metric_type == MetricType.GPU_TEMP:
            return [
                "Clean GPU heatsink and fans",
                "Check GPU fan speeds",
                "Improve case ventilation",
                "Consider aftermarket GPU cooler",
                "Monitor GPU power consumption"
            ]
        else:
            return [
                "Check system cooling",
                "Improve case airflow",
                "Clean dust from components",
                "Monitor ambient temperature"
            ]
    
    def get_health_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get overall system health summary for the selected period"""
        insights = self.analyze_period(start_date, end_date)
        
        # Count insights by level
        level_counts = {
            InsightLevel.CRITICAL: 0,
            InsightLevel.WARNING: 0,
            InsightLevel.INFO: 0,
            InsightLevel.SUCCESS: 0
        }
        
        total_anomalies = 0
        for insight in insights:
            level_counts[insight.level] += 1
            total_anomalies += insight.anomaly_count
        
        # Determine overall health
        if level_counts[InsightLevel.CRITICAL] > 0:
            overall_health = "critical"
        elif level_counts[InsightLevel.WARNING] > 0:
            overall_health = "warning"
        elif level_counts[InsightLevel.SUCCESS] > level_counts[InsightLevel.INFO]:
            overall_health = "good"
        else:
            overall_health = "normal"
        
        return {
            "overall_health": overall_health,
            "insight_counts": level_counts,
            "total_insights": len(insights),
            "total_anomalies": total_anomalies,
            "critical_issues": level_counts[InsightLevel.CRITICAL],
            "warnings": level_counts[InsightLevel.WARNING],
            "recommendations": len([i for i in insights if i.recommendations]),
            "period": {"start_date": start_date, "end_date": end_date}
        }
