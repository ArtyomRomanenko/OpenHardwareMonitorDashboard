from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MetricType(str, Enum):
    CPU_TEMP = "cpu_temperature"
    GPU_TEMP = "gpu_temperature"
    CPU_USAGE = "cpu_usage"
    GPU_USAGE = "gpu_usage"
    FAN_SPEED = "fan_speed"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"

class TimeRange(str, Enum):
    HOUR = "1h"
    DAY = "1d"
    WEEK = "7d"
    MONTH = "30d"
    CUSTOM = "custom"

class HardwareMetric(BaseModel):
    timestamp: datetime
    metric_type: MetricType
    value: float
    unit: str
    component: str

class TimeSeriesData(BaseModel):
    timestamps: List[datetime]
    values: List[float]
    metric_type: MetricType
    component: str
    unit: str

class InsightLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"

class AnomalyEvent(BaseModel):
    """Represents a specific anomaly event with timestamp and value"""
    timestamp: datetime
    value: float
    severity: str  # 'minor', 'moderate', 'severe'
    description: str
    expected_range: tuple[float, float]

class HardwareInsight(BaseModel):
    id: str
    title: str
    description: str
    level: InsightLevel
    metric_type: MetricType
    component: str
    timestamp: datetime
    recommendations: List[str] = []
    data: Dict[str, Any] = {}
    # New fields for enhanced insights
    events: List[AnomalyEvent] = []
    period_start: datetime
    period_end: datetime
    anomaly_count: int = 0
    baseline_stats: Dict[str, float] = {}

class DashboardConfig(BaseModel):
    time_range: TimeRange
    metrics: List[MetricType]
    components: List[str]
    refresh_interval: int = 30  # seconds

class MetricsResponse(BaseModel):
    data: List[TimeSeriesData]
    time_range: TimeRange
    total_records: int

class InsightsResponse(BaseModel):
    insights: List[HardwareInsight]
    summary: Dict[str, Any]

class SystemInfo(BaseModel):
    cpu_model: Optional[str] = None
    gpu_model: Optional[str] = None
    total_memory: Optional[float] = None
    os_info: Optional[str] = None
    last_update: datetime

class HealthStatus(BaseModel):
    overall_health: str
    cpu_health: str
    gpu_health: str
    system_health: str
    alerts: List[HardwareInsight] = []

class AnomalyDetectionConfig(BaseModel):
    """Configuration for anomaly detection algorithms"""
    z_score_threshold: float = 2.5  # Standard deviations for outlier detection
    iqr_multiplier: float = 1.5     # IQR multiplier for outlier detection
    min_data_points: int = 10       # Minimum points needed for analysis
    rolling_window_size: int = 20   # Window size for rolling statistics
    trend_sensitivity: float = 0.1  # Sensitivity for trend detection
