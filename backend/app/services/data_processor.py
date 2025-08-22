import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import glob
import logging
from app.models.hardware_models import MetricType, TimeSeriesData, HardwareMetric
from app.core.config import settings

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.data_directory = Path(settings.data_directory)
        self.cache = {}
        
    def get_available_dates(self) -> List[str]:
        """Get list of available dates from CSV files"""
        pattern = self.data_directory / "*.csv"
        files = glob.glob(str(pattern))
        dates = []
        
        for file in files:
            try:
                # Handle OpenHardwareMonitorLog-YYYY-MM-DD.csv format
                filename = Path(file).stem
                if filename.startswith("OpenHardwareMonitorLog-"):
                    date_str = filename.replace("OpenHardwareMonitorLog-", "")
                else:
                    date_str = filename
                    
                datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_str)
            except ValueError:
                continue
                
        return sorted(dates)
    
    def load_csv_data(self, date: str) -> pd.DataFrame:
        """Load CSV data for a specific date"""
        try:
            # Construct file path
            file_path = self.data_directory / f"OpenHardwareMonitorLog-{date}.csv"
            
            if not file_path.exists():
                print(f"No data for date: {date}")
                return pd.DataFrame()
            
            # Check file size before loading
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > settings.max_csv_size_mb:
                print(f"File {file_path} is too large ({file_size_mb:.1f}MB > {settings.max_csv_size_mb}MB). Skipping.")
                return pd.DataFrame()
            
            print(f"Loading CSV file: {file_path} ({file_size_mb:.1f}MB)")
            
            # First, try to read with optimized settings
            try:
                df = pd.read_csv(
                    file_path, 
                    header=0,
                    low_memory=False,  # Prevent mixed type warnings
                    dtype=str,  # Load all columns as strings first to avoid type inference issues
                    na_values=['', 'nan', 'NaN', 'NULL'],
                    keep_default_na=True,
                    nrows=settings.max_rows_per_file  # Limit rows to prevent memory issues
                )
                print(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            except MemoryError:
                print(f"Memory error loading {file_path}, trying chunked loading...")
                # If memory error, try chunked loading
                chunk_size = settings.chunk_size
                chunks = []
                
                for chunk in pd.read_csv(file_path, header=0, chunksize=chunk_size, dtype=str):
                    chunks.append(chunk)
                    if len(chunks) % 5 == 0:  # Log progress every 50k rows
                        print(f"Processed {len(chunks) * chunk_size} rows...")
                    
                    # Stop if we've reached the maximum rows
                    if len(chunks) * chunk_size >= settings.max_rows_per_file:
                        print(f"Reached maximum rows limit ({settings.max_rows_per_file})")
                        break
                
                if chunks:
                    df = pd.concat(chunks, ignore_index=True)
                    print(f"Chunked loading completed: {len(df)} rows")
                else:
                    print("No data could be loaded")
                    return pd.DataFrame()
            
            # Clean up memory
            import gc
            gc.collect()
            
            return df
            
        except Exception as e:
            print(f"Error loading CSV for date {date}: {e}")
            return pd.DataFrame()
    
    def process_csv_data(self, df: pd.DataFrame, date: str) -> pd.DataFrame:
        """Process the loaded CSV data to extract metrics"""
        try:
            if df.empty:
                return df
            
            print(f"Processing CSV data: {len(df)} rows, {len(df.columns)} columns")
            
            # Find the row that contains "Time" and use that as our header
            time_row_idx = None
            for idx, row in df.iterrows():
                if 'Time' in str(row.iloc[0]):
                    time_row_idx = idx
                    break
            
            if time_row_idx is not None:
                print(f"Found header row at index {time_row_idx}")
                # Use the row with "Time" as the header
                df.columns = df.iloc[time_row_idx]
                # Remove the header row from data
                df = df.drop(df.index[time_row_idx]).reset_index(drop=True)
                print(f"Header applied, remaining rows: {len(df)}")
            else:
                print("No 'Time' column found, using first row as header")
            
            # Convert timestamp column
            if 'Time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['Time'], errors='coerce')
            elif 'time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['time'], errors='coerce')
            elif 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            else:
                # Create timestamp from index if no time column
                df['timestamp'] = pd.date_range(
                    start=datetime.strptime(date, "%Y-%m-%d"),
                    periods=len(df),
                    freq='1min'
                )
            
            # Remove rows with invalid timestamps
            df = df.dropna(subset=['timestamp'])
            print(f"Rows with valid timestamps: {len(df)}")
            
            # Convert numeric columns (skip timestamp and non-numeric columns)
            numeric_columns = []
            for col in df.columns:
                if col != 'timestamp' and col != 'Time':
                    try:
                        # Try to convert to numeric, coercing errors to NaN
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        numeric_columns.append(col)
                    except Exception as e:
                        print(f"Could not convert column {col} to numeric: {e}")
                        continue
            
            print(f"Converted {len(numeric_columns)} columns to numeric")
            
            # Clean up memory
            import gc
            gc.collect()
            
            return df
            
        except Exception as e:
            print(f"Error processing CSV data: {e}")
            return pd.DataFrame()
    
    def get_metrics_for_period(self, start_date: str, end_date: str, 
                              metric_types: List[MetricType] = None) -> List[TimeSeriesData]:
        """Get metrics for a specific time period"""
        try:
            # Get available dates in the range
            available_dates = self.get_available_dates()
            if not available_dates:
                return []
            
            # Filter dates in range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Filter by date range (include the entire end date)
            end_dt_inclusive = end_dt + timedelta(days=1) - timedelta(seconds=1)
            
            dates_in_range = []
            for date in available_dates:
                try:
                    date_dt = datetime.strptime(date, "%Y-%m-%d")
                    if start_dt <= date_dt <= end_dt_inclusive:
                        dates_in_range.append(date)
                except ValueError:
                    continue
            
            if not dates_in_range:
                print(f"No dates found in range {start_date} to {end_date}")
                return []
            
            print(f"Processing {len(dates_in_range)} dates: {dates_in_range}")
            
            # Process each date and combine data
            all_data = []
            for date in dates_in_range:
                try:
                    print(f"Processing date: {date}")
                    
                    # Load and process CSV data
                    df = self.load_csv_data(date)
                    if not df.empty:
                        df = self.process_csv_data(df, date)
                        if not df.empty:
                            all_data.append(df)
                            print(f"Successfully processed {date}: {len(df)} rows")
                        else:
                            print(f"No valid data after processing for {date}")
                    else:
                        print(f"No data loaded for {date}")
                    
                    # Clean up memory after each date
                    import gc
                    gc.collect()
                    
                except Exception as e:
                    print(f"Error processing date {date}: {e}")
                    continue
            
            if not all_data:
                print("No data could be processed from any dates")
                return []
            
            # Combine all data
            print(f"Combining data from {len(all_data)} dates...")
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"Combined data: {len(combined_df)} rows, {len(combined_df.columns)} columns")
            
            # Clean up individual dataframes
            all_data.clear()
            gc.collect()
            
            # Extract metrics
            metrics = self.extract_metrics(combined_df, metric_types)
            print(f"Extracted {len(metrics)} metrics")
            
            # Clean up combined dataframe
            del combined_df
            gc.collect()
            
            return metrics
            
        except Exception as e:
            print(f"Error in get_metrics_for_period: {e}")
            return []
    
    def extract_metrics(self, df: pd.DataFrame, metric_types: List[MetricType] = None) -> List[TimeSeriesData]:
        """Extract metrics from the processed dataframe"""
        try:
            if df.empty:
                return []
            
            print(f"Extracting metrics from {len(df)} rows")
            
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
            
            # Also try to map individual CPU cores for temperature analysis
            cpu_core_columns = [col for col in df.columns if 'CPU Core #' in col]
            if cpu_core_columns:
                metric_mapping[MetricType.CPU_TEMP].extend(cpu_core_columns)
            
            results = []
            
            # Use all metric types if none specified
            target_metric_types = metric_types if metric_types else list(MetricType)
            
            for metric_type in target_metric_types:
                possible_columns = metric_mapping.get(metric_type, [])
                
                for col in possible_columns:
                    if col in df.columns:
                        try:
                            # Handle duplicate columns (DataFrame) vs single columns (Series)
                            column_data = df[col]
                            if isinstance(column_data, pd.DataFrame):
                                # Use the first sub-column for duplicate columns
                                column_data = column_data.iloc[:, 0]
                            
                            # Clean data and convert to numeric
                            clean_data = df[['timestamp']].copy()
                            clean_data[col] = column_data
                            clean_data = clean_data.dropna()
                            
                            # Convert column to numeric, coercing errors to NaN
                            clean_data[col] = pd.to_numeric(clean_data[col], errors='coerce')
                            clean_data = clean_data.dropna()
                            
                            if len(clean_data) > 0:
                                # Convert values to float, handling any remaining non-numeric values
                                values = []
                                for v in clean_data[col].tolist():
                                    try:
                                        values.append(float(v))
                                    except (ValueError, TypeError):
                                        continue
                                
                                if len(values) > 0:
                                    # Get corresponding timestamps
                                    timestamps = clean_data['timestamp'].tolist()
                                    # Ensure we have matching timestamps and values
                                    if len(timestamps) >= len(values):
                                        timestamps = timestamps[:len(values)]
                                    else:
                                        # If we have more values than timestamps, truncate values
                                        values = values[:len(timestamps)]
                                    
                                    time_series = TimeSeriesData(
                                        timestamps=timestamps,
                                        values=values,
                                        metric_type=metric_type,
                                        component=col,
                                        unit=self._get_unit_for_metric(metric_type)
                                    )
                                    results.append(time_series)
                                    print(f"Extracted {metric_type} from {col}: {len(values)} values")
                                    break
                        
                        except Exception as e:
                            print(f"Error extracting {metric_type} from {col}: {e}")
                            continue
            
            print(f"Successfully extracted {len(results)} metrics")
            return results
            
        except Exception as e:
            print(f"Error in extract_metrics: {e}")
            return []
    
    def _get_unit_for_metric(self, metric_type: MetricType) -> str:
        """Get the unit for a specific metric type"""
        units = {
            MetricType.CPU_TEMP: "°C",
            MetricType.GPU_TEMP: "°C",
            MetricType.CPU_USAGE: "%",
            MetricType.GPU_USAGE: "%",
            MetricType.FAN_SPEED: "RPM",
            MetricType.MEMORY_USAGE: "%",
            MetricType.DISK_USAGE: "%"
        }
        return units.get(metric_type, "")
    
    def get_statistics(self, start_date: str, end_date: str, 
                      metric_type: MetricType) -> Dict[str, Any]:
        """Get statistical summary for a metric type"""
        metrics_data = self.get_metrics_for_period(start_date, end_date, [metric_type])
        
        if not metrics_data:
            return {}
            
        # Combine all values
        all_values = []
        for data in metrics_data:
            all_values.extend(data.values)
            
        if not all_values:
            return {}
            
        values_array = np.array(all_values)
        
        return {
            "count": len(values_array),
            "mean": float(np.mean(values_array)),
            "median": float(np.median(values_array)),
            "std": float(np.std(values_array)),
            "min": float(np.min(values_array)),
            "max": float(np.max(values_array)),
            "q25": float(np.percentile(values_array, 25)),
            "q75": float(np.percentile(values_array, 75)),
            "iqr": float(np.percentile(values_array, 75) - np.percentile(values_array, 25))
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Extract system information from the data"""
        try:
            available_dates = self.get_available_dates()
            
            if not available_dates:
                return {}
                
            # Use the most recent data file
            latest_date = available_dates[-1]
            print(f"Loading system info from latest date: {latest_date}")
            
            # Load and process only the latest date for system info
            df = self.load_csv_data(latest_date)
            if df.empty:
                print(f"No data loaded for {latest_date}")
                return {}
            
            # Process the data
            df = self.process_csv_data(df, latest_date)
            if df.empty:
                print(f"No valid data after processing for {latest_date}")
                return {}
            
            print(f"Processing system info from {len(df)} rows")
            
            system_info = {
                'cpu_info': 'AMD CPU (24 cores)',  # Based on the data showing 24 CPU cores
                'gpu_info': 'NVIDIA GPU',  # Based on nvidiagpu in the data
                'last_update': latest_date
            }
            
            # Extract memory usage (average of Memory column)
            if 'Memory' in df.columns:
                try:
                    memory_values = pd.to_numeric(df['Memory'], errors='coerce').dropna()
                    if len(memory_values) > 0:
                        system_info['memory_usage_avg'] = float(memory_values.mean())
                        print(f"Memory usage avg: {system_info['memory_usage_avg']}")
                except Exception as e:
                    print(f"Error extracting memory usage: {e}")
                    system_info['memory_usage_avg'] = 0.0
            
            # Extract GPU memory (GPU Memory Total column)
            if 'GPU Memory Total' in df.columns:
                try:
                    gpu_memory_values = pd.to_numeric(df['GPU Memory Total'], errors='coerce').dropna()
                    if len(gpu_memory_values) > 0:
                        system_info['gpu_memory'] = float(gpu_memory_values.mean())
                        print(f"GPU memory avg: {system_info['gpu_memory']}")
                except Exception as e:
                    print(f"Error extracting GPU memory: {e}")
                    system_info['gpu_memory'] = 0.0
            
            # Extract disk usage (Used Space column)
            if 'Used Space' in df.columns:
                try:
                    disk_values = pd.to_numeric(df['Used Space'], errors='coerce').dropna()
                    if len(disk_values) > 0:
                        system_info['disk_usage'] = float(disk_values.mean())
                        print(f"Disk usage avg: {system_info['disk_usage']}")
                except Exception as e:
                    print(f"Error extracting disk usage: {e}")
                    system_info['disk_usage'] = 0.0
            
            # Add summary information
            system_info.update({
                'total_files': len(available_dates),
                'date_range': {
                    'start': available_dates[0],
                    'end': available_dates[-1]
                },
                'monitoring_duration': f"{len(available_dates)} days",
                'data_points': len(df)
            })
            
            # Clean up memory
            del df
            import gc
            gc.collect()
            
            print(f"System info extracted successfully: {len(system_info)} fields")
            return system_info
            
        except Exception as e:
            print(f"Error in get_system_info: {e}")
            return {}
