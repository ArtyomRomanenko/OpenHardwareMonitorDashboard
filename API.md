# API Documentation

This document provides comprehensive information about the Open Hardware Monitor Dashboard API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required for the API endpoints.

## Response Format

All API responses return JSON data with the following structure:

```json
{
  "data": {...},
  "message": "Success message",
  "status": "success"
}
```

Error responses follow this format:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

## Endpoints

### Dashboard API

#### Get Dashboard Overview

Retrieves a comprehensive dashboard overview for a specified time period.

```http
GET /dashboard/overview?days={days}
```

**Parameters:**
- `days` (integer, required): Number of days to analyze (1-30)

**Response:**
```json
{
  "system_info": {
    "cpu_model": "Intel Core i7-12700K",
    "gpu_model": "NVIDIA RTX 3080",
    "total_memory": "32 GB",
    "os_info": "Windows 11",
    "last_update": "2024-01-15T12:00:00",
    "total_files": 7,
    "date_range": "2024-01-15 to 2024-01-21",
    "monitoring_duration": "7 days",
    "data_points": 10080
  },
  "overview": {
    "metrics": {
      "cpu_temperature": {
        "average": 65.2,
        "maximum": 78.5,
        "minimum": 52.1,
        "unit": "°C"
      },
      "gpu_temperature": {
        "average": 72.8,
        "maximum": 85.3,
        "minimum": 58.9,
        "unit": "°C"
      }
    },
    "data_points": 10080
  },
  "health_summary": {
    "overall_health": "good",
    "insight_counts": {
      "critical": 0,
      "warning": 2,
      "info": 1,
      "success": 3
    },
    "total_insights": 6,
    "total_anomalies": 5
  },
  "recent_insights": {
    "insights": [
      {
        "id": "1",
        "title": "High CPU Temperature Detected",
        "description": "CPU temperature exceeded normal range",
        "level": "warning",
        "metric_type": "cpu_temperature",
        "component": "cpu",
        "timestamp": "2024-01-15T12:00:00",
        "recommendations": ["Check cooling system", "Monitor workload"]
      }
    ],
    "total_insights": 6
  },
  "period": {
    "start_date": "2024-01-15",
    "end_date": "2024-01-21",
    "days": 7
  }
}
```

#### Get Health Status

Retrieves detailed system health status for a specific date range.

```http
GET /dashboard/health-status?start_date={start_date}&end_date={end_date}
```

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format

**Response:**
```json
{
  "overall_health": "good",
  "cpu_health": {
    "status": "good",
    "temperature": "normal",
    "usage": "normal",
    "anomalies": 0
  },
  "gpu_health": {
    "status": "warning",
    "temperature": "elevated",
    "usage": "normal",
    "anomalies": 2
  },
  "system_health": {
    "status": "good",
    "memory": "normal",
    "storage": "normal",
    "anomalies": 0
  },
  "alerts": [
    {
      "level": "warning",
      "message": "GPU temperature above normal range",
      "timestamp": "2024-01-15T12:00:00"
    }
  ]
}
```

#### Get Performance Trends

Retrieves performance trends analysis for the specified period.

```http
GET /dashboard/trends?start_date={start_date}&end_date={end_date}
```

**Response:**
```json
{
  "trends": {
    "cpu_temperature": {
      "direction": "increasing",
      "strength": "moderate",
      "slope": 0.15,
      "trend_data": [...]
    },
    "gpu_temperature": {
      "direction": "stable",
      "strength": "weak",
      "slope": 0.02,
      "trend_data": [...]
    }
  },
  "period": {
    "start_date": "2024-01-15",
    "end_date": "2024-01-21"
  },
  "metrics_analyzed": ["cpu_temperature", "gpu_temperature"]
}
```

### Insights API

#### Analyze Period

Performs comprehensive analysis of hardware metrics for a specific period.

```http
GET /insights/analyze?start_date={start_date}&end_date={end_date}
```

**Response:**
```json
{
  "insights": [
    {
      "id": "1",
      "title": "CPU Temperature Anomaly",
      "description": "Detected 3 temperature spikes above normal range",
      "level": "warning",
      "metric_type": "cpu_temperature",
      "component": "cpu",
      "timestamp": "2024-01-15T12:00:00",
      "recommendations": ["Check cooling system", "Monitor workload"],
      "events": [
        {
          "timestamp": "2024-01-15T12:05:00",
          "value": 85.2,
          "severity": "moderate",
          "description": "Temperature spike detected",
          "expected_range": [45.0, 75.0]
        }
      ],
      "period_start": "2024-01-15T00:00:00",
      "period_end": "2024-01-21T23:59:59",
      "anomaly_count": 3,
      "baseline_stats": {
        "mean": 65.2,
        "median": 64.8,
        "std": 8.5,
        "min": 52.1,
        "max": 85.2,
        "q25": 58.3,
        "q75": 72.1,
        "iqr": 13.8
      }
    }
  ],
  "summary": {
    "total_insights": 6,
    "critical_insights": 0,
    "warning_insights": 2,
    "info_insights": 1,
    "success_insights": 3,
    "total_anomalies": 5
  }
}
```

#### Get Health Summary

Retrieves a comprehensive health summary for the specified period.

```http
GET /insights/health-summary?start_date={start_date}&end_date={end_date}
```

**Response:**
```json
{
  "overall_health": "good",
  "insight_counts": {
    "critical": 0,
    "warning": 2,
    "info": 1,
    "success": 3
  },
  "total_insights": 6,
  "total_anomalies": 5,
  "critical_issues": 0,
  "warnings": 2,
  "recommendations": 6,
  "period": {
    "start_date": "2024-01-15",
    "end_date": "2024-01-21"
  }
}
```

#### Get Insights by Metric

Retrieves insights filtered by a specific metric type.

```http
GET /insights/by-metric/{metric_type}?start_date={start_date}&end_date={end_date}
```

**Parameters:**
- `metric_type` (string, path): The metric type to filter by (e.g., "cpu_temperature")

**Response:**
```json
{
  "insights": [
    {
      "id": "1",
      "title": "CPU Temperature Anomaly",
      "description": "Detected temperature spikes",
      "level": "warning",
      "metric_type": "cpu_temperature",
      "component": "cpu",
      "timestamp": "2024-01-15T12:00:00",
      "recommendations": ["Check cooling system"],
      "events": [...],
      "period_start": "2024-01-15T00:00:00",
      "period_end": "2024-01-21T23:59:59",
      "anomaly_count": 3,
      "baseline_stats": {...}
    }
  ],
  "filter": {
    "metric_type": "cpu_temperature",
    "period": {
      "start_date": "2024-01-15",
      "end_date": "2024-01-21"
    }
  }
}
```

#### Get Insights by Level

Retrieves insights filtered by severity level.

```http
GET /insights/by-level/{level}?start_date={start_date}&end_date={end_date}
```

**Parameters:**
- `level` (string, path): The severity level to filter by (e.g., "warning")

**Response:**
```json
{
  "insights": [
    {
      "id": "1",
      "title": "CPU Temperature Anomaly",
      "description": "Detected temperature spikes",
      "level": "warning",
      "metric_type": "cpu_temperature",
      "component": "cpu",
      "timestamp": "2024-01-15T12:00:00",
      "recommendations": ["Check cooling system"],
      "events": [...],
      "period_start": "2024-01-15T00:00:00",
      "period_end": "2024-01-21T23:59:59",
      "anomaly_count": 3,
      "baseline_stats": {...}
    }
  ],
  "filter": {
    "level": "warning",
    "period": {
      "start_date": "2024-01-15",
      "end_date": "2024-01-21"
    }
  }
}
```

### Metrics API

#### Get Metrics for Period

Retrieves time series data for specified metrics and period.

```http
GET /metrics/period?start_date={start_date}&end_date={end_date}&metric_types={metric_types}
```

**Parameters:**
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `metric_types` (string, optional): Comma-separated list of metric types

**Response:**
```json
{
  "data": [
    {
      "timestamps": ["2024-01-15T00:00:00", "2024-01-15T00:01:00"],
      "values": [65.2, 66.8],
      "metric_type": "cpu_temperature",
      "component": "cpu",
      "unit": "°C"
    },
    {
      "timestamps": ["2024-01-15T00:00:00", "2024-01-15T00:01:00"],
      "values": [72.1, 73.5],
      "metric_type": "gpu_temperature",
      "component": "gpu",
      "unit": "°C"
    }
  ],
  "time_range": {
    "start_date": "2024-01-15",
    "end_date": "2024-01-21"
  },
  "total_records": 10080,
  "metrics_available": ["cpu_temperature", "gpu_temperature", "memory_usage"]
}
```

#### Get System Information

Retrieves comprehensive system information.

```http
GET /metrics/system-info
```

**Response:**
```json
{
  "cpu_model": "Intel Core i7-12700K",
  "gpu_model": "NVIDIA RTX 3080",
  "total_memory": "32 GB",
  "os_info": "Windows 11",
  "last_update": "2024-01-15T12:00:00",
  "total_files": 7,
  "date_range": "2024-01-15 to 2024-01-21",
  "monitoring_duration": "7 days",
  "data_points": 10080,
  "hardware_summary": {
    "cpu_cores": 12,
    "gpu_memory": "10 GB",
    "storage": "1 TB SSD"
  }
}
```

#### Get Available Dates

Retrieves list of available data dates.

```http
GET /metrics/available-dates
```

**Response:**
```json
{
  "dates": [
    "2024-01-15",
    "2024-01-16",
    "2024-01-17",
    "2024-01-18",
    "2024-01-19",
    "2024-01-20",
    "2024-01-21"
  ],
  "total_dates": 7,
  "date_range": {
    "earliest": "2024-01-15",
    "latest": "2024-01-21"
  },
  "data_summary": {
    "total_files": 7,
    "total_size_mb": 45.2,
    "average_file_size_mb": 6.46
  }
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters or request format
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server-side errors

### Common Error Responses

#### Invalid Date Format
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD format.",
  "status_code": 400
}
```

#### Date Range Error
```json
{
  "detail": "Start date must be before end date.",
  "status_code": 400
}
```

#### No Data Found
```json
{
  "detail": "No data found for the specified period.",
  "status_code": 404
}
```

#### Internal Server Error
```json
{
  "detail": "Error processing request. Please try again later.",
  "status_code": 500
}
```

## Rate Limiting

Currently, no rate limiting is implemented. However, it's recommended to:

- Limit requests to reasonable frequencies
- Implement proper error handling and retry logic
- Cache responses when appropriate

## Data Formats

### Date Format
All dates should be provided in ISO 8601 format: `YYYY-MM-DD`

### Time Format
Timestamps are returned in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

### Metric Types
Available metric types include:
- `cpu_temperature`: CPU temperature readings
- `gpu_temperature`: GPU temperature readings
- `cpu_usage`: CPU utilization percentage
- `gpu_usage`: GPU utilization percentage
- `memory_usage`: Memory utilization percentage
- `fan_speed`: Fan speed readings
- `power_consumption`: Power consumption readings

## Examples

### Python Client Example

```python
import requests
import json

base_url = "http://localhost:8000"

# Get dashboard overview for last 7 days
response = requests.get(f"{base_url}/dashboard/overview?days=7")
dashboard_data = response.json()

# Analyze insights for specific period
insights_response = requests.get(
    f"{base_url}/insights/analyze",
    params={
        "start_date": "2024-01-15",
        "end_date": "2024-01-21"
    }
)
insights_data = insights_response.json()

# Get metrics for specific period
metrics_response = requests.get(
    f"{base_url}/metrics/period",
    params={
        "start_date": "2024-01-15",
        "end_date": "2024-01-21",
        "metric_types": "cpu_temperature,gpu_temperature"
    }
)
metrics_data = metrics_response.json()
```

### JavaScript Client Example

```javascript
const baseUrl = 'http://localhost:8000';

// Get dashboard overview
async function getDashboardOverview(days) {
    try {
        const response = await fetch(`${baseUrl}/dashboard/overview?days=${days}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching dashboard:', error);
        throw error;
    }
}

// Analyze insights for period
async function analyzeInsights(startDate, endDate) {
    try {
        const response = await fetch(
            `${baseUrl}/insights/analyze?start_date=${startDate}&end_date=${endDate}`
        );
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error analyzing insights:', error);
        throw error;
    }
}

// Get metrics for period
async function getMetrics(startDate, endDate, metricTypes) {
    try {
        const params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate,
            metric_types: metricTypes
        });
        
        const response = await fetch(`${baseUrl}/metrics/period?${params}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching metrics:', error);
        throw error;
    }
}
```

## Support

For API support and questions:

1. Check the error responses for specific error details
2. Verify parameter formats and requirements
3. Review the request/response examples
4. Check the backend logs for detailed error information
5. Create an issue with detailed error information and request details

## Recent Improvements

### Version 0.3.0 (2025-08-23)
- **Enhanced Data Processing**: Improved CSV parsing with duplicate column handling
- **Memory Optimization**: Better handling of large datasets with chunked loading
- **Anomaly Detection**: Advanced Z-score, IQR, and threshold-based detection
- **Period-Specific Analysis**: Insights generated only for selected date ranges
- **Event Tracking**: Detailed anomaly events with timestamps and severity levels
- **Baseline Statistics**: Comprehensive statistical analysis (mean, median, std, quartiles)

### Performance Enhancements
- **Smart Sampling**: Efficient data point reduction for chart visualization
- **Garbage Collection**: Automatic memory cleanup during processing
- **Error Recovery**: Graceful handling of corrupted or malformed data
- **Progress Logging**: Real-time processing feedback for large files

## Versioning

The API follows semantic versioning. The current version is v1.0.0.

Future versions will maintain backward compatibility where possible, with deprecated endpoints clearly marked in the documentation.
