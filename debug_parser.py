#!/usr/bin/env python3
"""
Debug script to see what's happening with the data processing
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.data_processor import DataProcessor
from app.models.hardware_models import MetricType

def debug_data_parsing():
    """Debug the data processor step by step"""
    print("Debugging Open Hardware Monitor data parsing...")
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Get the most recent date
    dates = processor.get_available_dates()
    if not dates:
        print("No dates found!")
        return
    
    latest_date = dates[-1]
    print(f"Using date: {latest_date}")
    
    # Load the data
    try:
        df = processor.load_csv_data(latest_date)
        print(f"Loaded data with {len(df)} rows and {len(df.columns)} columns")
        
        # Check specific columns
        print("\nChecking specific columns:")
        columns_to_check = ['CPU Total', 'Memory', 'GPU Core', 'Used Space']
        
        for col in columns_to_check:
            if col in df.columns:
                print(f"Column '{col}' exists")
                # Check if it's a DataFrame (duplicate column) or Series
                column_data = df[col]
                if isinstance(column_data, pd.DataFrame):
                    print(f"  Column is a DataFrame with {len(column_data.columns)} sub-columns")
                    # Use the first sub-column
                    column_data = column_data.iloc[:, 0]
                    print(f"  Using first sub-column: {column_data.name}")
                
                # Show first few values
                values = column_data.head(5).tolist()
                print(f"  First 5 values: {values}")
                
                # Try to convert to numeric
                numeric_values = pd.to_numeric(column_data, errors='coerce')
                valid_count = numeric_values.notna().sum()
                print(f"  Valid numeric values: {valid_count}/{len(df)}")
                
                if valid_count > 0:
                    sample_values = numeric_values.dropna().head(3).tolist()
                    print(f"  Sample numeric values: {sample_values}")
            else:
                print(f"Column '{col}' NOT found")
        
        # Test the metrics extraction directly
        print("\nTesting metrics extraction:")
        try:
            # Test with specific metric types
            from app.models.hardware_models import MetricType
            
            print("Available metric types:")
            for metric_type in MetricType:
                print(f"  - {metric_type.value}")
            
            # Debug: Check what columns are actually in the DataFrame
            print(f"\nAll columns in DataFrame:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: '{col}'")
            
            # Debug: Test column access directly
            print(f"\nTesting column access directly:")
            test_columns = ['CPU Total', 'Memory', 'GPU Core', 'Used Space']
            for col in test_columns:
                if col in df.columns:
                    print(f"  Column '{col}' exists")
                    column_data = df[col]
                    if isinstance(column_data, pd.DataFrame):
                        print(f"    - Is DataFrame with {len(column_data.columns)} sub-columns")
                        print(f"    - Sub-columns: {list(column_data.columns)}")
                        # Test accessing first sub-column
                        first_sub_col = column_data.iloc[:, 0]
                        print(f"    - First sub-column name: '{first_sub_col.name}'")
                        print(f"    - First sub-column first 3 values: {first_sub_col.head(3).tolist()}")
                    else:
                        print(f"    - Is Series")
                        print(f"    - First 3 values: {column_data.head(3).tolist()}")
                else:
                    print(f"  Column '{col}' NOT found")
            
            # Test with specific metric types
            test_metrics = [MetricType.CPU_TEMP, MetricType.CPU_USAGE, MetricType.MEMORY_USAGE]
            print(f"\nTesting with specific metrics: {[m.value for m in test_metrics]}")
            
            metrics = processor.get_metrics_for_period(latest_date, latest_date, test_metrics)
            print(f"Found {len(metrics)} metrics")
            for metric in metrics:
                print(f"  - {metric.metric_type.value}: {len(metric.values)} values")
                
            # Test without specifying metric types
            print(f"\nTesting without specifying metric types:")
            all_metrics = processor.get_metrics_for_period(latest_date, latest_date)
            print(f"Found {len(all_metrics)} metrics")
            for metric in all_metrics:
                print(f"  - {metric.metric_type.value}: {len(metric.values)} values")
            
            # Test the data processing logic directly
            print(f"\nTesting data processing logic directly:")
            from app.models.hardware_models import MetricType
            
            # Simulate the data processing logic
            combined_df = df  # Use the loaded data as combined_df
            
            # Map metric types to column names (Open Hardware Monitor format)
            metric_mapping = {
                MetricType.CPU_TEMP: ['CPU Total'],  # CPU Total represents overall CPU load/temp
                MetricType.GPU_TEMP: ['GPU Core'],   # GPU Core temperature
                MetricType.CPU_USAGE: ['CPU Total'], # CPU Total usage percentage
                MetricType.GPU_USAGE: ['GPU Core'],  # GPU Core usage
                MetricType.FAN_SPEED: ['GPU Fan'],   # GPU Fan speed
                MetricType.MEMORY_USAGE: ['Memory'], # Memory usage percentage
                MetricType.DISK_USAGE: ['Used Space'] # Disk usage
            }
            
            print("Testing metric mapping:")
            for metric_type, columns in metric_mapping.items():
                print(f"  {metric_type.value}: {columns}")
                for col in columns:
                    if col in combined_df.columns:
                        print(f"    - Column '{col}' found in DataFrame")
                        column_data = combined_df[col]
                        if isinstance(column_data, pd.DataFrame):
                            print(f"      - Is DataFrame with {len(column_data.columns)} sub-columns")
                            # Use the first sub-column
                            column_data = column_data.iloc[:, 0]
                            print(f"      - Using first sub-column: '{column_data.name}'")
                        else:
                            print(f"      - Is Series: '{column_data.name}'")
                        
                        # Clean data and convert to numeric
                        clean_data = combined_df[['timestamp']].copy()
                        clean_data[col] = column_data
                        clean_data = clean_data.dropna()
                        
                        print(f"      - Clean data shape: {clean_data.shape}")
                        
                        # Convert column to numeric, coercing errors to NaN
                        clean_data[col] = pd.to_numeric(clean_data[col], errors='coerce')
                        clean_data = clean_data.dropna()
                        
                        print(f"      - After numeric conversion: {clean_data.shape}")
                        
                        if len(clean_data) > 0:
                            print(f"      - ✅ SUCCESS: Found {len(clean_data)} valid data points")
                            
                            # Test the final conversion step
                            try:
                                # Convert values to float, handling any remaining non-numeric values
                                values = []
                                for v in clean_data[col].tolist():
                                    try:
                                        values.append(float(v))
                                    except (ValueError, TypeError):
                                        continue
                                
                                print(f"      - Converted {len(values)} values to float")
                                
                                if len(values) > 0:
                                    # Get corresponding timestamps
                                    timestamps = clean_data['timestamp'].tolist()
                                    # Ensure we have matching timestamps and values
                                    if len(timestamps) >= len(values):
                                        timestamps = timestamps[:len(values)]
                                    else:
                                        # If we have more values than timestamps, truncate values
                                        values = values[:len(timestamps)]
                                    
                                    print(f"      - Final: {len(timestamps)} timestamps, {len(values)} values")
                                    
                                    # Test creating TimeSeriesData object
                                    from app.models.hardware_models import TimeSeriesData
                                    time_series = TimeSeriesData(
                                        timestamps=timestamps,
                                        values=values,
                                        metric_type=metric_type,
                                        component=col,
                                        unit="%" if "usage" in metric_type.value else "°C" if "temp" in metric_type.value else "RPM"
                                    )
                                    print(f"      - ✅ TimeSeriesData created successfully")
                                else:
                                    print(f"      - ❌ No valid float values after conversion")
                            except Exception as e:
                                print(f"      - ❌ Error in final conversion: {e}")
                        else:
                            print(f"      - ❌ FAILED: No valid data points after processing")
                    else:
                        print(f"    - Column '{col}' NOT found in DataFrame")
                
        except Exception as e:
            print(f"Error in metrics extraction: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_parsing()
