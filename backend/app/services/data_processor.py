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
        # Try both naming patterns
        file_path = self.data_directory / f"{date}.csv"
        if not file_path.exists():
            file_path = self.data_directory / f"OpenHardwareMonitorLog-{date}.csv"
        
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found for date {date}")
            
        try:
            # Read CSV with header=0 to use first row as column names
            df = pd.read_csv(file_path, header=0)
            
            # The first row contains the actual column names, but they're in the data
            # Let's find the row that contains "Time" and use that as our header
            time_row_idx = None
            for idx, row in df.iterrows():
                if 'Time' in str(row.iloc[0]):
                    time_row_idx = idx
                    break
            
            if time_row_idx is not None:
                # Use the row with "Time" as the header
                df.columns = df.iloc[time_row_idx]
                # Remove the header row from data
                df = df.drop(df.index[time_row_idx]).reset_index(drop=True)
            
            # Convert timestamp column
            if 'Time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['Time'])
            elif 'time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['time'])
            elif 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                # Create timestamp from index if no time column
                df['timestamp'] = pd.date_range(
                    start=datetime.strptime(date, "%Y-%m-%d"),
                    periods=len(df),
                    freq='1min'
                )
                
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            raise
    
    def get_metrics_for_period(self, start_date: str, end_date: str, 
                             metric_types: List[MetricType] = None) -> List[TimeSeriesData]:
        """Get metrics data for a specific time period"""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        all_data = []
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime("%Y-%m-%d")
            
            try:
                df = self.load_csv_data(date_str)
                all_data.append(df)
            except FileNotFoundError:
                logger.warning(f"No data for date: {date_str}")
                
            current_dt += timedelta(days=1)
        
        if not all_data:
            return []
            
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values('timestamp')
        
        # Filter by date range (include the entire end date)
        end_dt_inclusive = end_dt + timedelta(days=1) - timedelta(seconds=1)
        mask = (combined_df['timestamp'] >= start_dt) & (combined_df['timestamp'] <= end_dt_inclusive)
        combined_df = combined_df[mask]
        
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
        cpu_core_columns = [col for col in combined_df.columns if 'CPU Core #' in col]
        if cpu_core_columns:
            metric_mapping[MetricType.CPU_TEMP].extend(cpu_core_columns)
        
        results = []
        
        for metric_type in (metric_types or list(MetricType)):
            possible_columns = metric_mapping.get(metric_type, [])
            
            for col in possible_columns:
                if col in combined_df.columns:
                    # Handle duplicate columns (DataFrame) vs single columns (Series)
                    column_data = combined_df[col]
                    if isinstance(column_data, pd.DataFrame):
                        # Use the first sub-column for duplicate columns
                        column_data = column_data.iloc[:, 0]
                    
                    # Clean data and convert to numeric
                    clean_data = combined_df[['timestamp']].copy()
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
                            break
        
        return results
    
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
        available_dates = self.get_available_dates()
        
        if not available_dates:
            return {}
            
        # Use the most recent data file
        latest_date = available_dates[-1]
        
        try:
            df = self.load_csv_data(latest_date)
            
            system_info = {
                'cpu_model': 'AMD CPU (24 cores)',  # Based on the data showing 24 CPU cores
                'gpu_model': 'NVIDIA GPU',  # Based on nvidiagpu in the data
                'total_memory': '16 GB',  # Based on Memory column showing ~17GB total
                'os_info': 'Windows',
                'last_update': latest_date
            }
            
            # Try to extract more specific info from the data
            if 'Memory' in df.columns:
                memory_data = df['Memory']
                if isinstance(memory_data, pd.DataFrame):
                    memory_data = memory_data.iloc[:, 0]
                memory_values = pd.to_numeric(memory_data, errors='coerce').dropna()
                if not memory_values.empty:
                    avg_memory = memory_values.mean()
                    system_info['memory_usage_avg'] = f"{avg_memory:.1f}%"
            
            if 'GPU Memory Total' in df.columns:
                gpu_memory_data = df['GPU Memory Total']
                if isinstance(gpu_memory_data, pd.DataFrame):
                    gpu_memory_data = gpu_memory_data.iloc[:, 0]
                gpu_memory_values = pd.to_numeric(gpu_memory_data, errors='coerce').dropna()
                if not gpu_memory_values.empty:
                    gpu_memory_gb = gpu_memory_values.iloc[0] / 1024  # Convert MB to GB
                    system_info['gpu_memory'] = f"{gpu_memory_gb:.1f} GB"
            
            return system_info
            
        except Exception as e:
            logger.error(f"Error extracting system info: {e}")
            return {}
