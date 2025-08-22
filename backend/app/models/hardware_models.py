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
