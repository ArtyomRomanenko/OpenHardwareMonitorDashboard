from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.hardware_models import (
    MetricType, TimeRange, MetricsResponse, TimeSeriesData
)
from app.services.data_processor import DataProcessor

router = APIRouter()
data_processor = DataProcessor()

@router.get("/available-dates")
async def get_available_dates():
    """Get list of available dates with data"""
    try:
        dates = data_processor.get_available_dates()
        return {
            "dates": dates,
            "count": len(dates),
            "date_range": {
                "start": dates[0] if dates else None,
                "end": dates[-1] if dates else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving available dates: {str(e)}")

@router.get("/time-series")
async def get_time_series_data(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    metric_types: Optional[List[MetricType]] = Query(None, description="Specific metric types to retrieve")
):
    """Get time series data for specified period and metrics"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get data
        data = data_processor.get_metrics_for_period(start_date, end_date, metric_types)
        
        # Calculate total records
        total_records = sum(len(ts_data.values) for ts_data in data)
        
        return MetricsResponse(
            data=data,
            time_range=TimeRange.CUSTOM,
            total_records=total_records
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving time series data: {str(e)}")

@router.get("/statistics")
async def get_statistics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    metric_type: MetricType = Query(..., description="Metric type to analyze")
):
    """Get statistical summary for a specific metric type"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get statistics
        stats = data_processor.get_statistics(start_date, end_date, metric_type)
        
        if not stats:
            raise HTTPException(status_code=404, detail=f"No data found for {metric_type.value}")
        
        return {
            "metric_type": metric_type,
            "period": {"start_date": start_date, "end_date": end_date},
            "statistics": stats
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """Get system information extracted from the data"""
    try:
        system_info = data_processor.get_system_info()
        
        if not system_info:
            raise HTTPException(status_code=404, detail="No system information found")
        
        return system_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system info: {str(e)}")

@router.get("/quick-overview")
async def get_quick_overview(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=30)
):
    """Get a quick overview of recent hardware metrics"""
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Get data for key metrics
        key_metrics = [MetricType.CPU_TEMP, MetricType.GPU_TEMP, MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]
        data = data_processor.get_metrics_for_period(start_date_str, end_date_str, key_metrics)
        
        # Calculate quick stats
        overview = {}
        for metric_data in data:
            if metric_data.values:
                values = metric_data.values
                overview[metric_data.metric_type.value] = {
                    "current": values[-1] if values else None,
                    "average": sum(values) / len(values) if values else None,
                    "max": max(values) if values else None,
                    "min": min(values) if values else None,
                    "unit": metric_data.unit
                }
        
        return {
            "period": {"start_date": start_date_str, "end_date": end_date_str, "days": days},
            "metrics": overview,
            "data_points": sum(len(d.values) for d in data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quick overview: {str(e)}")

@router.get("/metric-types")
async def get_metric_types():
    """Get all available metric types"""
    return {
        "metric_types": [
            {
                "value": metric_type.value,
                "name": metric_type.value.replace("_", " ").title(),
                "unit": data_processor._get_unit_for_metric(metric_type)
            }
            for metric_type in MetricType
        ]
    }
