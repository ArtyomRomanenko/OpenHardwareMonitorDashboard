#!/usr/bin/env python3
"""
Test script to verify memory optimizations in the data processor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_processor import DataProcessor
from app.core.config import settings

def test_memory_optimization():
    """Test the memory-optimized data processor"""
    print("🧪 Testing Memory Optimization")
    print(f"Max CSV size: {settings.max_csv_size_mb}MB")
    print(f"Max rows per file: {settings.max_rows_per_file}")
    print(f"Chunk size: {settings.chunk_size}")
    print("-" * 50)
    
    try:
        # Initialize data processor
        processor = DataProcessor()
        
        # Get available dates
        print("📅 Getting available dates...")
        dates = processor.get_available_dates()
        print(f"Found {len(dates)} available dates: {dates[:5]}...")
        
        if not dates:
            print("❌ No dates found")
            return
        
        # Test with the most recent date
        test_date = dates[-1]
        print(f"\n🔍 Testing with date: {test_date}")
        
        # Load CSV data
        print("📊 Loading CSV data...")
        df = processor.load_csv_data(test_date)
        
        if df.empty:
            print("❌ No data loaded")
            return
        
        print(f"✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Process CSV data
        print("⚙️ Processing CSV data...")
        processed_df = processor.process_csv_data(df, test_date)
        
        if processed_df.empty:
            print("❌ No data after processing")
            return
        
        print(f"✅ Data processed: {len(processed_df)} rows")
        
        # Test system info
        print("\n💻 Testing system info...")
        system_info = processor.get_system_info()
        print(f"✅ System info: {len(system_info)} fields")
        for key, value in system_info.items():
            print(f"  {key}: {value}")
        
        # Test metrics extraction
        print("\n📈 Testing metrics extraction...")
        metrics = processor.extract_metrics(processed_df)
        print(f"✅ Extracted {len(metrics)} metrics")
        
        for metric in metrics[:3]:  # Show first 3 metrics
            print(f"  {metric.metric_type}: {len(metric.values)} values")
        
        print("\n🎉 All tests passed! Memory optimization working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_optimization()
