import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid
from app.models.hardware_models import (
    HardwareInsight, InsightLevel, MetricType, TimeSeriesData
)
from app.core.config import settings
from app.services.data_processor import DataProcessor

class InsightsEngine:
    def __init__(self):
        self.data_processor = DataProcessor()
        
        # Hardware thresholds and benchmarks
        self.thresholds = {
            MetricType.CPU_TEMP: {
                'warning': settings.cpu_temp_warning,
                'critical': settings.cpu_temp_critical,
                'optimal_max': 70.0
            },
            MetricType.GPU_TEMP: {
                'warning': settings.gpu_temp_warning,
                'critical': settings.gpu_temp_critical,
                'optimal_max': 75.0
            },
            MetricType.CPU_USAGE: {
                'warning': 90.0,
                'critical': 95.0,
                'optimal_max': 80.0
            },
            MetricType.GPU_USAGE: {
                'warning': 95.0,
                'critical': 98.0,
                'optimal_max': 85.0
            },
            MetricType.MEMORY_USAGE: {
                'warning': 85.0,
                'critical': 95.0,
                'optimal_max': 75.0
            },
            MetricType.DISK_USAGE: {
                'warning': 85.0,
                'critical': 95.0,
                'optimal_max': 80.0
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
        
        # Get all metrics for the period
        metrics_data = self.data_processor.get_metrics_for_period(start_date, end_date)
        
        if not metrics_data:
            return insights
        
        # Analyze each metric type
        for metric_data in metrics_data:
            metric_insights = self._analyze_metric(metric_data, start_date, end_date)
            insights.extend(metric_insights)
        
        # Generate cross-metric insights
        cross_insights = self._generate_cross_metric_insights(metrics_data)
        insights.extend(cross_insights)
        
        # Generate trend insights
        trend_insights = self._analyze_trends(metrics_data, start_date, end_date)
        insights.extend(trend_insights)
        
        return insights
    
    def _analyze_metric(self, metric_data: TimeSeriesData, 
                       start_date: str, end_date: str) -> List[HardwareInsight]:
        """Analyze a specific metric and generate insights"""
        insights = []
        values = np.array(metric_data.values)
        
        if len(values) == 0:
            return insights
        
        metric_type = metric_data.metric_type
        thresholds = self.thresholds.get(metric_type, {})
        
        # Calculate statistics
        mean_val = np.mean(values)
        max_val = np.max(values)
        min_val = np.min(values)
        std_val = np.std(values)
        
        # Check for critical temperatures
        if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
            if max_val >= thresholds.get('critical', 100):
                insights.append(self._create_insight(
                    f"Critical {metric_type.value.replace('_', ' ').title()}",
                    f"Maximum {metric_type.value.replace('_', ' ')} reached {max_val:.1f}°C, which is critically high. "
                    f"Immediate action required to prevent hardware damage.",
                    InsightLevel.CRITICAL,
                    metric_type,
                    metric_data.component,
                    recommendations=[
                        "Shutdown intensive applications immediately",
                        "Check cooling system functionality",
                        "Clean dust from heatsinks and fans",
                        "Consider hardware replacement if issue persists"
                    ]
                ))
            
            elif max_val >= thresholds.get('warning', 80):
                insights.append(self._create_insight(
                    f"High {metric_type.value.replace('_', ' ').title()}",
                    f"Maximum {metric_type.value.replace('_', ' ')} reached {max_val:.1f}°C, which is above recommended levels. "
                    f"Monitor closely and consider cooling improvements.",
                    InsightLevel.WARNING,
                    metric_type,
                    metric_data.component,
                    recommendations=self._get_cooling_recommendations(metric_type)
                ))
        
        # Check for usage patterns
        if metric_type in [MetricType.CPU_USAGE, MetricType.GPU_USAGE, MetricType.MEMORY_USAGE]:
            if mean_val >= thresholds.get('warning', 90):
                insights.append(self._create_insight(
                    f"High {metric_type.value.replace('_', ' ').title()}",
                    f"Average {metric_type.value.replace('_', ' ')} is {mean_val:.1f}%, indicating high system load. "
                    f"Consider optimizing applications or upgrading hardware.",
                    InsightLevel.WARNING,
                    metric_type,
                    metric_data.component,
                    recommendations=[
                        "Identify resource-intensive applications",
                        "Close unnecessary background processes",
                        "Consider hardware upgrade if usage is consistently high"
                    ]
                ))
        
        # Check for unusual patterns
        if std_val > mean_val * 0.3:  # High variability
            insights.append(self._create_insight(
                f"Variable {metric_type.value.replace('_', ' ').title()}",
                f"{metric_type.value.replace('_', ' ').title()} shows high variability (std: {std_val:.1f}). "
                f"This may indicate inconsistent workload or cooling issues.",
                InsightLevel.INFO,
                metric_type,
                metric_data.component,
                recommendations=[
                    "Monitor for patterns in usage",
                    "Check for background processes causing spikes",
                    "Verify cooling system consistency"
                ]
            ))
        
        # Positive insights for good performance
        if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
            if mean_val <= thresholds.get('optimal_max', 70):
                insights.append(self._create_insight(
                    f"Optimal {metric_type.value.replace('_', ' ').title()}",
                    f"Average {metric_type.value.replace('_', ' ')} is {mean_val:.1f}°C, which is within optimal range. "
                    f"Your cooling system is working well.",
                    InsightLevel.SUCCESS,
                    metric_type,
                    metric_data.component,
                    recommendations=[
                        "Maintain current cooling setup",
                        "Regular cleaning schedule is working",
                        "Continue monitoring for changes"
                    ]
                ))
        
        return insights
    
    def _generate_cross_metric_insights(self, metrics_data: List[TimeSeriesData]) -> List[HardwareInsight]:
        """Generate insights based on relationships between different metrics"""
        insights = []
        
        # Find CPU and GPU temperature data
        cpu_temp_data = next((d for d in metrics_data if d.metric_type == MetricType.CPU_TEMP), None)
        gpu_temp_data = next((d for d in metrics_data if d.metric_type == MetricType.GPU_TEMP), None)
        cpu_usage_data = next((d for d in metrics_data if d.metric_type == MetricType.CPU_USAGE), None)
        
        if cpu_temp_data and gpu_temp_data:
            cpu_values = np.array(cpu_temp_data.values)
            gpu_values = np.array(gpu_temp_data.values)
            
            # Check if both are running hot
            if (np.mean(cpu_values) > 75 and np.mean(gpu_values) > 80):
                insights.append(self._create_insight(
                    "High System Temperatures",
                    "Both CPU and GPU are running at elevated temperatures. "
                    "This may indicate insufficient case airflow or cooling capacity.",
                    InsightLevel.WARNING,
                    MetricType.CPU_TEMP,
                    "system",
                    recommendations=[
                        "Improve case airflow with additional fans",
                        "Check case ventilation and cable management",
                        "Consider upgrading to larger case with better airflow",
                        "Monitor ambient room temperature"
                    ]
                ))
        
        if cpu_temp_data and cpu_usage_data:
            cpu_temp_values = np.array(cpu_temp_data.values)
            cpu_usage_values = np.array(cpu_usage_data.values)
            
            # Check for thermal throttling patterns
            high_usage_mask = cpu_usage_values > 80
            if np.any(high_usage_mask):
                high_usage_temps = cpu_temp_values[high_usage_mask]
                if np.mean(high_usage_temps) > 85:
                    insights.append(self._create_insight(
                        "Potential Thermal Throttling",
                        "CPU temperatures are very high during high usage periods. "
                        "This may cause performance throttling.",
                        InsightLevel.WARNING,
                        MetricType.CPU_TEMP,
                        "cpu",
                        recommendations=[
                            "Upgrade CPU cooler",
                            "Apply high-quality thermal paste",
                            "Check for proper cooler mounting",
                            "Consider undervolting if supported"
                        ]
                    ))
        
        return insights
    
    def _analyze_trends(self, metrics_data: List[TimeSeriesData], 
                       start_date: str, end_date: str) -> List[HardwareInsight]:
        """Analyze trends in the data over time"""
        insights = []
        
        for metric_data in metrics_data:
            if len(metric_data.values) < 10:  # Need enough data points
                continue
            
            values = np.array(metric_data.values)
            
            # Calculate trend (simple linear regression)
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # Check for increasing trends in temperatures
            if metric_data.metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
                if slope > 0.1:  # Increasing trend
                    insights.append(self._create_insight(
                        f"Increasing {metric_data.metric_type.value.replace('_', ' ').title()} Trend",
                        f"{metric_data.metric_type.value.replace('_', ' ').title()} shows an increasing trend over time. "
                        f"This may indicate deteriorating cooling performance.",
                        InsightLevel.WARNING,
                        metric_data.metric_type,
                        metric_data.component,
                        recommendations=[
                            "Clean dust from cooling components",
                            "Check thermal paste condition",
                            "Monitor fan speeds and noise",
                            "Consider preventive maintenance"
                        ]
                    ))
            
            # Check for decreasing trends (good)
            elif metric_data.metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
                if slope < -0.1:  # Decreasing trend
                    insights.append(self._create_insight(
                        f"Improving {metric_data.metric_type.value.replace('_', ' ').title()}",
                        f"{metric_data.metric_type.value.replace('_', ' ').title()} shows a decreasing trend over time. "
                        f"Your cooling improvements are working well.",
                        InsightLevel.SUCCESS,
                        metric_data.metric_type,
                        metric_data.component,
                        recommendations=[
                            "Continue current maintenance routine",
                            "Document what changes led to improvement",
                            "Monitor for sustained improvement"
                        ]
                    ))
        
        return insights
    
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
    
    def _create_insight(self, title: str, description: str, level: InsightLevel,
                       metric_type: MetricType, component: str, 
                       recommendations: List[str] = None) -> HardwareInsight:
        """Create a hardware insight object"""
        return HardwareInsight(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            level=level,
            metric_type=metric_type,
            component=component,
            timestamp=datetime.now(),
            recommendations=recommendations or [],
            data={}
        )
    
    def get_health_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get overall system health summary"""
        insights = self.analyze_period(start_date, end_date)
        
        # Count insights by level
        level_counts = {
            InsightLevel.CRITICAL: 0,
            InsightLevel.WARNING: 0,
            InsightLevel.INFO: 0,
            InsightLevel.SUCCESS: 0
        }
        
        for insight in insights:
            level_counts[insight.level] += 1
        
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
            "critical_issues": level_counts[InsightLevel.CRITICAL],
            "warnings": level_counts[InsightLevel.WARNING],
            "recommendations": len([i for i in insights if i.recommendations])
        }
