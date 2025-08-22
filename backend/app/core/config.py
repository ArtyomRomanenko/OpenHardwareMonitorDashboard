import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Open Hardware Monitor Dashboard"
    debug: bool = True
    
    # Data settings
    data_directory: str = "E:/Downloads/openhardwaremonitor-v0.9.5/OpenHardwareMonitor"
    csv_file_pattern: str = "*.csv"
    
    # Database settings
    database_url: str = "sqlite:///./hardware_monitor.db"
    
    # API settings
    api_prefix: str = "/api/v1"
    
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
    return Path(__file__).parent.parent.parent / settings.data_directory
