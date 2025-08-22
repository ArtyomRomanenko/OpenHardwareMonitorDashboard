#!/usr/bin/env python3
"""
Test script to verify Open Hardware Monitor data parsing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.data_processor import DataProcessor
from app.models.hardware_models import MetricType

def test_data_parsing():
    """Test the data processor with actual Open Hardware Monitor data"""
    print("Testing Open Hardware Monitor data parsing...")
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Test available dates
    print("\n1. Available dates:")
    try:
        dates = processor.get_available_dates()
        print(f"Found {len(dates)} date(s): {dates}")
    except Exception as e:
        print(f"Error getting available dates: {e}")
        return
    
    if not dates:
        print("No dates found. Check if CSV files exist in the data directory.")
        return
    
    # Test loading data for the most recent date
    latest_date = dates[-1]
    print(f"\n2. Loading data for {latest_date}:")
    
    try:
        df = processor.load_csv_data(latest_date)
        print(f"Successfully loaded data with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head())
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Test metrics extraction
    print(f"\n3. Extracting metrics for {latest_date}:")
    try:
        metrics = processor.get_metrics_for_period(latest_date, latest_date)
        print(f"Found {len(metrics)} metric types:")
        
        for metric in metrics:
            print(f"  - {metric.metric_type.value}: {len(metric.values)} values, unit: {metric.unit}")
            if metric.values:
                print(f"    Range: {min(metric.values):.2f} - {max(metric.values):.2f}")
    except Exception as e:
        print(f"Error extracting metrics: {e}")
        return
    
    # Test system info
    print(f"\n4. System information:")
    try:
        system_info = processor.get_system_info()
        print(f"System info: {system_info}")
    except Exception as e:
        print(f"Error getting system info: {e}")
        return
    
    print("\n✅ Data parsing test completed successfully!")

if __name__ == "__main__":
    test_data_parsing()
