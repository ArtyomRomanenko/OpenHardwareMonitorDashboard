from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.hardware_models import (
    MetricType, InsightLevel, InsightsResponse, HardwareInsight
)
from app.services.insights_engine import InsightsEngine

router = APIRouter()
insights_engine = InsightsEngine()

@router.get("/analyze")
async def analyze_period(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Analyze hardware data for a specific period and generate insights"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate insights
        insights = insights_engine.analyze_period(start_date, end_date)
        
        # Create summary
        summary = {
            "total_insights": len(insights),
            "critical_count": len([i for i in insights if i.level == InsightLevel.CRITICAL]),
            "warning_count": len([i for i in insights if i.level == InsightLevel.WARNING]),
            "info_count": len([i for i in insights if i.level == InsightLevel.INFO]),
            "success_count": len([i for i in insights if i.level == InsightLevel.SUCCESS]),
            "period": {"start_date": start_date, "end_date": end_date}
        }
        
        return InsightsResponse(
            insights=insights,
            summary=summary
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")

@router.get("/health-summary")
async def get_health_summary(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get overall system health summary for a period"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get health summary
        health_summary = insights_engine.get_health_summary(start_date, end_date)
        health_summary["period"] = {"start_date": start_date, "end_date": end_date}
        
        return health_summary
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating health summary: {str(e)}")

@router.get("/recent")
async def get_recent_insights(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=30)
):
    """Get insights for the recent period"""
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Generate insights
        insights = insights_engine.analyze_period(start_date_str, end_date_str)
        
        # Sort by level (critical first) and timestamp
        insights.sort(key=lambda x: (x.level.value, x.timestamp), reverse=True)
        
        # Limit to top 10 most important insights
        top_insights = insights[:10]
        
        return {
            "insights": top_insights,
            "period": {"start_date": start_date_str, "end_date": end_date_str, "days": days},
            "total_insights": len(insights),
            "showing": len(top_insights)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent insights: {str(e)}")

@router.get("/by-level")
async def get_insights_by_level(
    level: InsightLevel = Query(..., description="Insight level to filter by"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get insights filtered by level"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate insights
        all_insights = insights_engine.analyze_period(start_date, end_date)
        
        # Filter by level
        filtered_insights = [i for i in all_insights if i.level == level]
        
        return {
            "insights": filtered_insights,
            "level": level,
            "period": {"start_date": start_date, "end_date": end_date},
            "count": len(filtered_insights)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering insights: {str(e)}")

@router.get("/by-metric")
async def get_insights_by_metric(
    metric_type: MetricType = Query(..., description="Metric type to filter by"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get insights filtered by metric type"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate insights
        all_insights = insights_engine.analyze_period(start_date, end_date)
        
        # Filter by metric type
        filtered_insights = [i for i in all_insights if i.metric_type == metric_type]
        
        return {
            "insights": filtered_insights,
            "metric_type": metric_type,
            "period": {"start_date": start_date, "end_date": end_date},
            "count": len(filtered_insights)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering insights: {str(e)}")

@router.get("/recommendations")
async def get_recommendations(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get all recommendations from insights"""
    try:
        # Validate dates
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate insights
        insights = insights_engine.analyze_period(start_date, end_date)
        
        # Extract all recommendations
        all_recommendations = []
        for insight in insights:
            if insight.recommendations:
                for rec in insight.recommendations:
                    all_recommendations.append({
                        "recommendation": rec,
                        "insight_title": insight.title,
                        "insight_level": insight.level,
                        "metric_type": insight.metric_type,
                        "component": insight.component
                    })
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec["recommendation"] not in seen:
                unique_recommendations.append(rec)
                seen.add(rec["recommendation"])
        
        return {
            "recommendations": unique_recommendations,
            "period": {"start_date": start_date, "end_date": end_date},
            "total_recommendations": len(unique_recommendations),
            "insights_analyzed": len(insights)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recommendations: {str(e)}")
