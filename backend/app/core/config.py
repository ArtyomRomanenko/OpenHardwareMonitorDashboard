import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """Application settings"""
    
    # Data directory path
    data_directory: str = "E:/Downloads/openhardwaremonitor-v0.9.5/OpenHardwareMonitor"
    
    # CSV processing limits
    max_csv_size_mb: int = 100  # Maximum CSV file size in MB
    max_rows_per_file: int = 100000  # Maximum rows to process per CSV file
    chunk_size: int = 10000  # Number of rows to process at once
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Hardware thresholds (in Celsius)
    cpu_temp_warning: float = 80.0
    cpu_temp_critical: float = 90.0
    gpu_temp_warning: float = 85.0
    gpu_temp_critical: float = 95.0
    
    # Time settings
    default_time_range_days: int = 7
    max_time_range_days: int = 365
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure data directory exists
def ensure_data_directory():
    data_path = Path(settings.data_directory)
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path

# Get absolute path to data directory
def get_data_directory() -> Path:
    data_path = Path(settings.data_directory)
    if data_path.is_absolute():
        return data_path
    else:
        return Path(__file__).parent.parent.parent / settings.data_directory
