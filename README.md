# OpenHardwareMonitorDashboard

A comprehensive dashboard for analyzing Open Hardware Monitor data with intelligent insights and interactive visualizations.

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

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + Uvicorn
- **Data Processing**: Pandas + NumPy + Scikit-learn
- **Charts**: Chart.js + React-Chartjs-2
- **Database**: SQLite (built-in)
- **Styling**: Tailwind CSS + Custom CSS animations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Open Hardware Monitor installed and generating CSV files

### 1. Clone and Setup
```bash
git clone <repository-url>
cd OpenHardwareMonitorDashboard
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Configure Data Source
Update `backend/app/core/config.py` with your Open Hardware Monitor data directory:
```python
data_directory = "E:/Downloads/openhardwaremonitor-v0.9.5/OpenHardwareMonitor"
```

### 5. Start the Application

#### Option A: Use Batch Files (Windows)
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

### 6. Access Dashboard
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📊 Data Format

The application expects CSV files from Open Hardware Monitor with the following structure:
- **File Naming**: `OpenHardwareMonitorLog-YYYY-MM-DD.csv`
- **Format**: Comma-separated values with hardware metrics
- **Columns**: Timestamp, CPU cores, GPU metrics, Memory, Disk usage, etc.
- **Example Structure**:
  ```
  Time,CPU Core #1,CPU Core #2,...,GPU Core,GPU Memory,...
  08/20/2025 00:00:03,3.125,6.25,...,49,1905.00012,...
  ```

## 🎯 Dashboard Features

### **Main Dashboard**
- System health overview with color-coded status indicators
- Key metrics summary (CPU, GPU, Memory, Disk)
- Recent insights and recommendations
- Time period selection (7, 14, 30 days)

### **Metrics Page**
- **Chart Types**: Line, Pie, Scatter, Doughnut
- **Metric Filtering**: Select specific hardware components
- **Interactive Charts**: Hover tooltips, zoom, pan
- **Data Sampling**: Automatic optimization for large datasets
- **Responsive Design**: Adapts to different screen sizes

### **Insights Page**
- Hardware health analysis with severity levels
- Performance recommendations
- Trend analysis and anomaly detection
- Filterable insights by metric type and date range

### **System Info Page**
- Detailed hardware specifications
- Memory usage statistics
- GPU information and memory details
- Disk usage and file counts

## 🔧 Configuration

### Backend Settings (`backend/app/core/config.py`)
```python
# Data directory path
data_directory = "E:/Downloads/openhardwaremonitor-v0.9.5/OpenHardwareMonitor"

# Hardware temperature thresholds
cpu_temp_warning = 70.0
cpu_temp_critical = 85.0
gpu_temp_warning = 75.0
gpu_temp_critical = 90.0

# Memory optimization
max_csv_size_mb = 100
max_rows_per_file = 100000
chunk_size = 10000
```

### Frontend Settings
- API timeout: 60 seconds
- Chart rendering optimizations
- Error retry mechanisms

## 🏗️ Project Structure

```
OpenHardwareMonitorDashboard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints (dashboard, metrics, insights)
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # Pydantic data models
│   │   └── services/       # Data processing and insights engine
│   ├── requirements.txt    # Python dependencies
│   ├── main.py            # FastAPI application entry point
│   └── venv/              # Virtual environment
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/          # Main page components
│   │   ├── services/       # API communication layer
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   └── public/             # Static assets
├── data/                   # CSV data files directory
├── start.bat               # Start both services (Windows)
├── start-backend-only.bat  # Start backend only (Windows)
├── start-backend-simple.bat # Simple backend start (Windows)
├── start-backend.ps1       # PowerShell backend start
└── README.md               # This file
```

## 🚨 Troubleshooting

### Common Issues

#### **Permission Denied Errors**
- **Problem**: `Error: [Errno 13] Permission denied: 'venv\Scripts\python.exe'`
- **Solution**: Use `start-backend-simple.bat` or `start-backend.ps1`

#### **No Data Displayed**
- **Problem**: Dashboard shows no metrics
- **Solution**: Check data directory path in `config.py` and ensure CSV files exist

#### **Chart Rendering Errors**
- **Problem**: "Maximum call stack size exceeded"
- **Solution**: Large datasets are automatically sampled and optimized

#### **API Timeouts**
- **Problem**: "Request canceled after 10 seconds"
- **Solution**: Increased to 60 seconds, use smaller time ranges for large datasets

### Performance Tips
- Use 7-14 day ranges for large datasets
- Enable metric type filtering to reduce chart complexity
- Charts automatically sample data for optimal performance

## 🔄 Recent Updates

### **v1.2.0** - Enhanced Charts & Performance
- ✅ Added multiple chart types (Line, Pie, Scatter, Doughnut)
- ✅ Improved metric filtering and selection
- ✅ Memory optimization for large datasets
- ✅ Enhanced error handling and user feedback
- ✅ Fixed permission issues with startup scripts

### **v1.1.0** - Core Functionality
- ✅ Basic dashboard with time series visualization
- ✅ Hardware insights and health monitoring
- ✅ System information display
- ✅ API endpoints for data access

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open Hardware Monitor** for the excellent hardware monitoring software
- **FastAPI** for the modern, fast web framework
- **React** and **Chart.js** for the interactive frontend experience
- **Pandas** and **NumPy** for powerful data processing capabilities