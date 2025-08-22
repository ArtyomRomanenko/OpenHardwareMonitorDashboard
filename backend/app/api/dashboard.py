from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.hardware_models import (
    MetricType, TimeRange, DashboardConfig, HealthStatus
)
from app.services.data_processor import DataProcessor
from app.services.insights_engine import InsightsEngine

router = APIRouter()
data_processor = DataProcessor()
insights_engine = InsightsEngine()

@router.get("/overview")
async def get_dashboard_overview(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=30)
):
    """Get comprehensive dashboard overview"""
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Get system info
        system_info = data_processor.get_system_info()
        
        # Get quick overview
        overview_response = await router.get("/quick-overview")(days=days)
        
        # Get health summary
        health_summary = insights_engine.get_health_summary(start_date_str, end_date_str)
        
        # Get recent insights
        insights_response = await router.get("/recent")(days=days)
        
        return {
            "system_info": system_info,
            "overview": overview_response,
            "health_summary": health_summary,
            "recent_insights": insights_response,
            "period": {"start_date": start_date_str, "end_date": end_date_str, "days": days}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard overview: {str(e)}")

@router.get("/health-status")
async def get_health_status(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get detailed health status for all components"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get health summary
        health_summary = insights_engine.get_health_summary(start_date, end_date)
        
        # Get insights for detailed analysis
        insights = insights_engine.analyze_period(start_date, end_date)
        
        # Categorize insights by component
        cpu_insights = [i for i in insights if i.metric_type in [MetricType.CPU_TEMP, MetricType.CPU_USAGE]]
        gpu_insights = [i for i in insights if i.metric_type in [MetricType.GPU_TEMP, MetricType.GPU_USAGE]]
        system_insights = [i for i in insights if i.metric_type in [MetricType.MEMORY_USAGE, MetricType.DISK_USAGE]]
        
        # Determine component health
        def get_component_health(component_insights):
            if any(i.level.value == "critical" for i in component_insights):
                return "critical"
            elif any(i.level.value == "warning" for i in component_insights):
                return "warning"
            elif any(i.level.value == "success" for i in component_insights):
                return "good"
            else:
                return "normal"
        
        cpu_health = get_component_health(cpu_insights)
        gpu_health = get_component_health(gpu_insights)
        system_health = get_component_health(system_insights)
        
        # Get critical alerts
        critical_alerts = [i for i in insights if i.level.value == "critical"]
        
        return HealthStatus(
            overall_health=health_summary["overall_health"],
            cpu_health=cpu_health,
            gpu_health=gpu_health,
            system_health=system_health,
            alerts=critical_alerts
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating health status: {str(e)}")

@router.get("/trends")
async def get_trends_analysis(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    metric_types: Optional[List[MetricType]] = Query(None, description="Specific metric types to analyze")
):
    """Get trend analysis for metrics"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get metrics data
        if not metric_types:
            metric_types = [MetricType.CPU_TEMP, MetricType.GPU_TEMP, MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]
        
        metrics_data = data_processor.get_metrics_for_period(start_date, end_date, metric_types)
        
        trends = {}
        for metric_data in metrics_data:
            if len(metric_data.values) < 5:  # Need enough data points
                continue
                
            values = metric_data.values
            x = list(range(len(values)))
            
            # Calculate trend (simple linear regression)
            import numpy as np
            slope = np.polyfit(x, values, 1)[0]
            
            # Determine trend direction
            if slope > 0.1:
                trend_direction = "increasing"
                trend_strength = "strong" if abs(slope) > 0.5 else "moderate"
            elif slope < -0.1:
                trend_direction = "decreasing"
                trend_strength = "strong" if abs(slope) > 0.5 else "moderate"
            else:
                trend_direction = "stable"
                trend_strength = "weak"
            
            trends[metric_data.metric_type.value] = {
                "direction": trend_direction,
                "strength": trend_strength,
                "slope": float(slope),
                "start_value": values[0],
                "end_value": values[-1],
                "change_percent": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0,
                "unit": metric_data.unit
            }
        
        return {
            "trends": trends,
            "period": {"start_date": start_date, "end_date": end_date},
            "metrics_analyzed": len(trends)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")

@router.get("/performance-summary")
async def get_performance_summary(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get performance summary with key metrics"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get key metrics
        key_metrics = [MetricType.CPU_TEMP, MetricType.GPU_TEMP, MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]
        metrics_data = data_processor.get_metrics_for_period(start_date, end_date, key_metrics)
        
        performance_summary = {}
        
        for metric_data in metrics_data:
            if not metric_data.values:
                continue
                
            values = metric_data.values
            metric_type = metric_data.metric_type
            
            # Calculate performance indicators
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            
            # Determine performance rating
            if metric_type in [MetricType.CPU_TEMP, MetricType.GPU_TEMP]:
                if avg_value <= 60:
                    rating = "excellent"
                elif avg_value <= 75:
                    rating = "good"
                elif avg_value <= 85:
                    rating = "fair"
                else:
                    rating = "poor"
            elif metric_type in [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]:
                if avg_value <= 50:
                    rating = "excellent"
                elif avg_value <= 75:
                    rating = "good"
                elif avg_value <= 90:
                    rating = "fair"
                else:
                    rating = "poor"
            else:
                rating = "normal"
            
            performance_summary[metric_type.value] = {
                "average": round(avg_value, 2),
                "maximum": round(max_value, 2),
                "minimum": round(min_value, 2),
                "rating": rating,
                "unit": metric_data.unit,
                "data_points": len(values)
            }
        
        return {
            "performance_summary": performance_summary,
            "period": {"start_date": start_date, "end_date": end_date},
            "overall_rating": _calculate_overall_rating(performance_summary)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance summary: {str(e)}")

def _calculate_overall_rating(performance_summary):
    """Calculate overall performance rating"""
    ratings = {
        "excellent": 4,
        "good": 3,
        "fair": 2,
        "poor": 1,
        "normal": 2.5
    }
    
    if not performance_summary:
        return "normal"
    
    total_score = 0
    count = 0
    
    for metric_data in performance_summary.values():
        total_score += ratings.get(metric_data["rating"], 2.5)
        count += 1
    
    avg_score = total_score / count if count > 0 else 2.5
    
    if avg_score >= 3.5:
        return "excellent"
    elif avg_score >= 2.5:
        return "good"
    elif avg_score >= 1.5:
        return "fair"
    else:
        return "poor"

@router.get("/config")
async def get_dashboard_config():
    """Get default dashboard configuration"""
    return DashboardConfig(
        time_range=TimeRange.WEEK,
        metrics=[MetricType.CPU_TEMP, MetricType.GPU_TEMP, MetricType.CPU_USAGE, MetricType.MEMORY_USAGE],
        components=["cpu", "gpu", "system"],
        refresh_interval=30
    )
