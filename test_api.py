#!/usr/bin/env python3
"""
Test script to check if the data processor is working with the fixed configuration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.config import settings, get_data_directory
from backend.app.services.data_processor import DataProcessor

def test_api_functionality():
    """Test the API functionality directly"""
    print("Testing API functionality...")
    
    # Test configuration
    print(f"1. Configuration:")
    print(f"   Data directory setting: {settings.data_directory}")
    print(f"   Resolved data directory: {get_data_directory()}")
    print(f"   Directory exists: {get_data_directory().exists()}")
    
    # Test data processor
    print(f"\n2. Data Processor:")
    processor = DataProcessor()
    
    # Test available dates
    try:
        dates = processor.get_available_dates()
        print(f"   Available dates: {len(dates)} found")
        if dates:
            print(f"   Date range: {dates[0]} to {dates[-1]}")
            print(f"   First 5 dates: {dates[:5]}")
        else:
            print("   No dates found!")
    except Exception as e:
        print(f"   Error getting dates: {e}")
        return
    
    # Test system info
    try:
        system_info = processor.get_system_info()
        print(f"\n3. System Info:")
        for key, value in system_info.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"   Error getting system info: {e}")
    
    # Test metrics for latest date
    if dates:
        try:
            latest_date = dates[-1]
            print(f"\n4. Testing metrics for {latest_date}:")
            metrics = processor.get_metrics_for_period(latest_date, latest_date)
            print(f"   Found {len(metrics)} metrics:")
            for metric in metrics:
                print(f"   - {metric.metric_type.value}: {len(metric.values)} values")
        except Exception as e:
            print(f"   Error getting metrics: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_api_functionality()
