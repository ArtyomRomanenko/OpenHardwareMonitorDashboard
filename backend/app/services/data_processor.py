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
                date_str = Path(file).stem
                datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_str)
            except ValueError:
                continue
                
        return sorted(dates)
    
    def load_csv_data(self, date: str) -> pd.DataFrame:
        """Load CSV data for a specific date"""
        file_path = self.data_directory / f"{date}.csv"
        
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
            
        try:
            df = pd.read_csv(file_path)
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Convert timestamp column
            if 'time' in df.columns:
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
        
        # Filter by date range
        mask = (combined_df['timestamp'] >= start_dt) & (combined_df['timestamp'] <= end_dt)
        combined_df = combined_df[mask]
        
        # Map metric types to column names
        metric_mapping = {
            MetricType.CPU_TEMP: ['cpu_temperature', 'cpu_temp', 'cpu_temperature_°c'],
            MetricType.GPU_TEMP: ['gpu_temperature', 'gpu_temp', 'gpu_temperature_°c'],
            MetricType.CPU_USAGE: ['cpu_usage', 'cpu_usage_%'],
            MetricType.GPU_USAGE: ['gpu_usage', 'gpu_usage_%'],
            MetricType.FAN_SPEED: ['fan_speed', 'fan_speed_rpm'],
            MetricType.MEMORY_USAGE: ['memory_usage', 'ram_usage', 'memory_usage_%'],
            MetricType.DISK_USAGE: ['disk_usage', 'disk_usage_%']
        }
        
        results = []
        
        for metric_type in (metric_types or list(MetricType)):
            possible_columns = metric_mapping.get(metric_type, [])
            
            for col in possible_columns:
                if col in combined_df.columns:
                    # Clean data
                    clean_data = combined_df[['timestamp', col]].dropna()
                    
                    if len(clean_data) > 0:
                        time_series = TimeSeriesData(
                            timestamps=clean_data['timestamp'].tolist(),
                            values=clean_data[col].tolist(),
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
            
            system_info = {}
            
            # Look for system information columns
            info_columns = ['cpu_model', 'gpu_model', 'total_memory', 'os_info']
            
            for col in info_columns:
                if col in df.columns:
                    # Get the first non-null value
                    value = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                    system_info[col] = value
                    
            system_info['last_update'] = latest_date
            
            return system_info
            
        except Exception as e:
            logger.error(f"Error extracting system info: {e}")
            return {}
