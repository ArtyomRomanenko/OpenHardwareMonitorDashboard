# Open Hardware Monitor Dashboard - Setup Guide

## Overview

This dashboard provides comprehensive analysis of Open Hardware Monitor data with intelligent insights and interactive visualizations. It consists of a Python FastAPI backend and a React TypeScript frontend.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Open Hardware Monitor (for data collection)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd OpenHardwareMonitorDashboard
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure data directory
# Edit backend/app/core/config.py and update data_directory path
# Default: "../data" (relative to backend directory)
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Configure API endpoint (optional)
# Edit frontend/src/services/api.ts if backend runs on different port
```

### 4. Data Configuration

1. **Open Hardware Monitor Setup**:
   - Download and install Open Hardware Monitor
   - Configure it to save CSV files daily
   - Set the output directory to match your `data_directory` configuration

2. **CSV File Format**:
   The application expects CSV files with the following structure:
   ```
   Time,CPU Temperature,GPU Temperature,CPU Usage,GPU Usage,Memory Usage,Fan Speed
   2024-01-15 00:00:00,45.2,52.1,12.5,8.3,45.2,1200
   ```

3. **File Naming**:
   - Files should be named by date: `YYYY-MM-DD.csv`
   - Example: `2024-01-15.csv`

### 5. Run the Application

#### Backend
```bash
cd backend
# Activate virtual environment if not already activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Configuration

### Backend Configuration

Edit `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Data settings
    data_directory: str = "../data"  # Path to CSV files
    
    # Hardware thresholds (in Celsius)
    cpu_temp_warning: float = 80.0
    cpu_temp_critical: float = 90.0
    gpu_temp_warning: float = 85.0
    gpu_temp_critical: float = 95.0
    
    # Time settings
    default_time_range_days: int = 7
    max_time_range_days: int = 365
```

### Frontend Configuration

Edit `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

## Features

### Dashboard Overview
- **System Health Status**: Overall system health with color-coded indicators
- **Quick Metrics**: Real-time display of key hardware metrics
- **Recent Insights**: AI-powered analysis and recommendations
- **Performance Summary**: Statistical overview of system performance

### Metrics Analysis
- **Time Series Visualization**: Interactive charts for different time periods
- **Statistical Analysis**: Mean, median, min/max, standard deviation
- **Trend Analysis**: Identify patterns and trends in hardware performance

### Intelligent Insights
- **Hardware Health Analysis**: Automatic detection of potential issues
- **Performance Recommendations**: Actionable advice for optimization
- **Threshold Monitoring**: Configurable alerts for temperature and usage
- **Cross-Metric Analysis**: Relationship analysis between different metrics

### System Information
- **Hardware Specifications**: CPU, GPU, memory details
- **Operating System Info**: OS version and system details
- **Data Summary**: Statistics about collected data

## API Endpoints

### Metrics API
- `GET /api/v1/metrics/available-dates` - Get available data dates
- `GET /api/v1/metrics/time-series` - Get time series data
- `GET /api/v1/metrics/statistics` - Get statistical analysis
- `GET /api/v1/metrics/system-info` - Get system information
- `GET /api/v1/metrics/quick-overview` - Get quick overview

### Insights API
- `GET /api/v1/insights/analyze` - Analyze data for insights
- `GET /api/v1/insights/health-summary` - Get health summary
- `GET /api/v1/insights/recent` - Get recent insights
- `GET /api/v1/insights/recommendations` - Get recommendations

### Dashboard API
- `GET /api/v1/dashboard/overview` - Get dashboard overview
- `GET /api/v1/dashboard/health-status` - Get health status
- `GET /api/v1/dashboard/trends` - Get trend analysis
- `GET /api/v1/dashboard/performance-summary` - Get performance summary

## Troubleshooting

### Common Issues

1. **No Data Displayed**:
   - Check if CSV files exist in the data directory
   - Verify file naming format (YYYY-MM-DD.csv)
   - Check CSV column headers match expected format

2. **Backend Connection Error**:
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend
   - Verify API_BASE_URL in frontend

3. **High Memory Usage**:
   - Large CSV files may cause memory issues
   - Consider data aggregation for long periods
   - Implement data archiving for old files

4. **Performance Issues**:
   - Limit time range for large datasets
   - Use data sampling for long periods
   - Consider database storage for large datasets

### Logs and Debugging

Backend logs are available in the console where uvicorn is running.
Frontend logs are available in the browser developer console.

## Development

### Adding New Metrics

1. **Backend**: Add new metric type in `backend/app/models/hardware_models.py`
2. **Data Processing**: Update column mapping in `backend/app/services/data_processor.py`
3. **Insights**: Add analysis logic in `backend/app/services/insights_engine.py`
4. **Frontend**: Add visualization components

### Customizing Insights

Edit `backend/app/services/insights_engine.py`:
- Modify threshold values
- Add new analysis patterns
- Customize recommendations

### Styling

The frontend uses Tailwind CSS. Customize styles in:
- `frontend/tailwind.config.js` - Theme configuration
- `frontend/src/index.css` - Global styles
- Component-specific classes

## Production Deployment

### Backend Deployment

1. **Docker** (Recommended):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Environment Variables**:
   ```bash
   export DATA_DIRECTORY=/path/to/csv/files
   export DEBUG=false
   export DATABASE_URL=postgresql://user:pass@localhost/db
   ```

### Frontend Deployment

1. **Build for Production**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve with Nginx**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/frontend/build;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Create an issue on GitHub
4. Check the logs for error details
