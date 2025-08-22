# Open Hardware Monitor Dashboard - Setup Guide

## Overview

This dashboard provides comprehensive analysis of Open Hardware Monitor data with intelligent insights and interactive visualizations. It consists of a Python FastAPI backend and a React TypeScript frontend with advanced charting capabilities.

## ✨ Features

- 📊 **Interactive Time Series Plots**: Visualize CPU, GPU, and system metrics across different time periods
- 🎨 **Multiple Chart Types**: Line charts, pie charts, scatter plots, and doughnut charts
- 🧠 **Intelligent Insights**: AI-powered analysis of hardware health and performance with actionable recommendations
- 📈 **Real-time Monitoring**: Live data updates and historical trend analysis
- 🎯 **Customizable Dashboards**: Create personalized views for different metrics
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔍 **Advanced Filtering**: Filter by metric types, time ranges, and chart types
- 🚨 **Health Monitoring**: Real-time system health status with temperature thresholds
- 💾 **Memory Optimized**: Handles large datasets efficiently with chunked processing
- 🛡️ **Error Handling**: Comprehensive error handling with retry mechanisms and fallback options

## Prerequisites

- **Python 3.11+** (required for latest dependencies)
- **Node.js 16+** and npm
- **Open Hardware Monitor** (for data collection)
- **Windows 10/11** (primary development platform)

## 🚀 Quick Start

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
# Example: "E:/Downloads/openhardwaremonitor-v0.9.5/OpenHardwareMonitor"
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
   Time,CPU Core #1,CPU Core #2,...,GPU Core,GPU Memory,...
   08/20/2025 00:00:03,3.125,6.25,...,49,1905.00012,...
   ```

3. **File Naming**:
   - Files should be named: `OpenHardwareMonitorLog-YYYY-MM-DD.csv`
   - Example: `OpenHardwareMonitorLog-2025-08-20.csv`

### 5. Run the Application

#### Option A: Use Batch Files (Windows - Recommended)
```bash
# Start both frontend and backend
start.bat

# Start backend only
start-backend-only.bat

# Simple backend start (no virtual environment activation)
start-backend-simple.bat
```

#### Option B: Use PowerShell Script
```bash
# Right-click start-backend.ps1 → "Run with PowerShell"
```

#### Option C: Manual Start
```bash
# Backend
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Backend Configuration

Edit `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Data settings
    data_directory: str = "E:/Downloads/openhardwaremonitor-v0.9.5/OpenHardwareMonitor"
    
    # Hardware thresholds (in Celsius)
    cpu_temp_warning: float = 70.0
    cpu_temp_critical: float = 85.0
    gpu_temp_warning: float = 75.0
    gpu_temp_critical: float = 90.0
    
    # Memory optimization settings
    max_csv_size_mb: int = 100
    max_rows_per_file: int = 100000
    chunk_size: int = 10000
    
    # Time settings
    default_time_range_days: int = 7
    max_time_range_days: int = 365
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000"]
```

### Frontend Configuration

Edit `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const TIMEOUT = 60000; // 60 seconds for large datasets
```

## 🎯 Dashboard Features

### **Main Dashboard**
- **System Health Status**: Overall system health with color-coded indicators
- **Quick Metrics**: Real-time display of key hardware metrics
- **Recent Insights**: AI-powered analysis and recommendations
- **Performance Summary**: Statistical overview of system performance
- **Time Period Selection**: 7, 14, and 30-day options with fallback buttons

### **Metrics Page**
- **Chart Types**: Line, Pie, Scatter, Doughnut charts
- **Metric Filtering**: Select specific hardware components with checkboxes
- **Interactive Charts**: Hover tooltips, zoom, pan, and responsive design
- **Data Sampling**: Automatic optimization for large datasets
- **Chart Type Selection**: Radio buttons for different visualization styles
- **Performance Optimization**: Automatic data sampling and error boundaries

### **Insights Page**
- **Hardware Health Analysis**: Automatic detection of potential issues
- **Performance Recommendations**: Actionable advice for optimization
- **Threshold Monitoring**: Configurable alerts for temperature and usage
- **Cross-Metric Analysis**: Relationship analysis between different metrics
- **Filterable Insights**: By level, metric type, and date range

### **System Info Page**
- **Hardware Specifications**: CPU, GPU, memory details
- **Operating System Info**: OS version and system details
- **Data Summary**: Statistics about collected data
- **Memory Usage**: Detailed memory statistics and GPU memory info
- **Disk Usage**: Storage information and file counts

## 🔌 API Endpoints

### Metrics API
- `GET /api/v1/metrics/available-dates` - Get available data dates
- `GET /api/v1/metrics/time-series` - Get time series data with period filtering
- `GET /api/v1/metrics/statistics` - Get statistical analysis
- `GET /api/v1/metrics/system-info` - Get comprehensive system information
- `GET /api/v1/metrics/quick-overview` - Get quick overview
- `GET /api/v1/metrics/metric-types` - Get available metric types

### Insights API
- `GET /api/v1/insights/analyze` - Analyze data for insights
- `GET /api/v1/insights/health-summary` - Get health summary
- `GET /api/v1/insights/recent` - Get recent insights
- `GET /api/v1/insights/by-level` - Get insights by severity level
- `GET /api/v1/insights/by-metric` - Get insights by metric type
- `GET /api/v1/insights/recommendations` - Get recommendations

### Dashboard API
- `GET /api/v1/dashboard/overview` - Get dashboard overview
- `GET /api/v1/dashboard/health-status` - Get health status
- `GET /api/v1/dashboard/trends` - Get trend analysis
- `GET /api/v1/dashboard/performance-summary` - Get performance summary
- `GET /api/v1/dashboard/config` - Get configuration information

## 🚨 Troubleshooting

### Common Issues

#### **Permission Denied Errors**
- **Problem**: `Error: [Errno 13] Permission denied: 'venv\Scripts\python.exe'`
- **Solution**: Use `start-backend-simple.bat` or `start-backend.ps1`
- **Alternative**: Run PowerShell as Administrator

#### **No Data Displayed**
- **Problem**: Dashboard shows no metrics
- **Solution**: 
  - Check data directory path in `config.py`
  - Ensure CSV files exist with correct naming format
  - Verify file permissions and accessibility

#### **Chart Rendering Errors**
- **Problem**: "Maximum call stack size exceeded"
- **Solution**: Large datasets are automatically sampled and optimized
- **Prevention**: Use smaller time ranges (7-14 days) for large datasets

#### **API Timeouts**
- **Problem**: "Request canceled after 10 seconds"
- **Solution**: 
  - Increased timeout to 60 seconds
  - Use smaller time ranges for large datasets
  - Enable metric type filtering to reduce data load

#### **Memory Issues**
- **Problem**: High memory usage with large datasets
- **Solution**: 
  - Automatic chunked loading (10,000 rows per chunk)
  - File size limits (100MB max per file)
  - Row limits (100,000 max per file)

### Performance Tips
- Use 7-14 day ranges for large datasets
- Enable metric type filtering to reduce chart complexity
- Charts automatically sample data for optimal performance
- Use the "Show All Types" button to reset filters

### Logs and Debugging

**Backend logs** are available in the console where uvicorn is running.
**Frontend logs** are available in the browser developer console.
**API errors** are logged with detailed error messages and troubleshooting tips.

## 🏗️ Development

### Adding New Metrics

1. **Backend**: Add new metric type in `backend/app/models/hardware_models.py`
2. **Data Processing**: Update column mapping in `backend/app/services/data_processor.py`
3. **Insights**: Add analysis logic in `backend/app/services/insights_engine.py`
4. **Frontend**: Add visualization components with proper error handling

### Customizing Insights

Edit `backend/app/services/insights_engine.py`:
- Modify threshold values for temperature warnings
- Add new analysis patterns for hardware health
- Customize recommendations based on your hardware
- Implement cross-metric correlation analysis

### Styling and UI

The frontend uses Tailwind CSS with custom animations:
- `frontend/tailwind.config.js` - Theme configuration and custom colors
- `frontend/src/index.css` - Global styles and custom animations
- Component-specific classes for responsive design
- Chart styling with consistent color schemes

### Memory Optimization

The backend includes several memory optimization features:
- **Chunked CSV Loading**: Processes large files in manageable chunks
- **File Size Limits**: Prevents loading extremely large files
- **Row Limits**: Caps the number of rows processed per file
- **Garbage Collection**: Explicit memory cleanup after processing

## 🚀 Production Deployment

### Backend Deployment

1. **Docker** (Recommended):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Environment Variables**:
   ```bash
   export DATA_DIRECTORY=/path/to/csv/files
   export DEBUG=false
   export MAX_CSV_SIZE_MB=100
   export MAX_ROWS_PER_FILE=100000
   export CHUNK_SIZE=10000
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
           proxy_read_timeout 60s;
       }
   }
   ```

## 🔄 Recent Updates

### **v1.2.0** - Enhanced Charts & Performance
- ✅ Added multiple chart types (Line, Pie, Scatter, Doughnut)
- ✅ Improved metric filtering and selection with checkboxes
- ✅ Memory optimization for large datasets with chunked processing
- ✅ Enhanced error handling with retry mechanisms and fallback options
- ✅ Fixed permission issues with startup scripts
- ✅ Added 14-day time range option
- ✅ Improved chart interactivity and responsiveness

### **v1.1.0** - Core Functionality
- ✅ Basic dashboard with time series visualization
- ✅ Hardware insights and health monitoring
- ✅ System information display
- ✅ API endpoints for data access
- ✅ Memory optimization features

### **v1.0.0** - Initial Release
- ✅ Open Hardware Monitor CSV parsing
- ✅ FastAPI backend with data processing
- ✅ React frontend with basic charts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Check browser console and backend logs for error details
4. Create an issue on GitHub with detailed error information
5. Use the retry and fallback options in the dashboard

## 🙏 Acknowledgments

- **Open Hardware Monitor** for the excellent hardware monitoring software
- **FastAPI** for the modern, fast web framework
- **React** and **Chart.js** for the interactive frontend experience
- **Pandas** and **NumPy** for powerful data processing capabilities
- **Tailwind CSS** for the beautiful, responsive design system
