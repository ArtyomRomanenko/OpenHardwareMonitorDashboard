# FYI: This is a Cursor written project
# Open Hardware Monitor Dashboard

An interactive dashboard for visualizing PC hardware metrics from Open Hardware Monitor CSV data, providing intelligent insights and trend analysis over various time periods.

## Features

### 📊 **Dashboard Overview**
- **Quick Metrics**: Real-time system performance summary
- **Performance Summary**: Historical data analysis with key statistics
- **Recent Insights**: Latest hardware health recommendations
- **System Health**: Overall system status and alerts

### 📈 **Metrics Visualization**
- **Interactive Charts**: Line charts, scatter plots, and pie charts
- **Smart Sampling**: Efficient handling of large datasets (up to 500 data points)
- **Multiple Chart Types**: Support for various visualization styles
- **Date Range Selection**: Flexible time period analysis (7, 14, 30 days)
- **Dark/Light Mode**: Toggle between themes with automatic preference saving

### 🧠 **Intelligent Insights Engine**
- **Anomaly Detection**: Z-score, IQR, and threshold-based detection
- **Period-Specific Analysis**: Insights only for selected date ranges
- **Event Tracking**: Detailed anomaly events with timestamps and severity
- **Baseline Statistics**: Mean, median, standard deviation, quartiles
- **Hardware Recommendations**: Actionable advice based on data analysis

### 💾 **Data Processing**
- **Memory Optimization**: Chunked loading and garbage collection
- **Large File Support**: Handles CSV files up to 100MB
- **Smart Parsing**: Dynamic header detection and duplicate column handling
- **Efficient Storage**: Optimized data structures and caching

## Tech Stack

### Backend
- **Python 3.11+**: Core runtime
- **FastAPI**: Modern, fast web framework
- **Pandas & NumPy**: Data processing and analysis
- **SciPy**: Statistical analysis and anomaly detection
- **Pydantic**: Data validation and serialization
- **SQLite**: Lightweight data storage

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Interactive data visualization
- **React Router**: Client-side routing

### Testing
- **Pytest**: Backend testing framework
- **React Testing Library**: Frontend component testing
- **Coverage Reports**: Comprehensive test coverage
- **Mock Testing**: Isolated unit testing

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm
- Open Hardware Monitor installed and generating CSV logs

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OpenHardwareMonitorDashboard
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Data Preparation**
   - Place Open Hardware Monitor CSV files in the `data/` directory
   - Files should follow the format: `OpenHardwareMonitorLog-YYYY-MM-DD.csv`

5. **Start the Application**
   ```bash
   # Option 1: Use the start script (recommended)
   ./start.bat

   # Option 2: Manual start
   # Terminal 1 - Backend
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

6. **Access the Dashboard**
   - Open http://localhost:3000 in your browser
   - The backend API will be available at http://localhost:8000

## Data Format

Open Hardware Monitor generates CSV files with the following structure:
```
Time,CPU Core #1,CPU Core #2,Memory,GPU Core,GPU Memory
08/20/2025 00:00:03,3.125,6.25,43.7650833,49,1704.13281
08/20/2025 00:00:08,10.9375,9.375,43.7798424,47,1722.94531
```

The system automatically:
- Detects and parses timestamps
- Converts numeric values
- Maps hardware components
- Handles duplicate columns
- Processes large datasets efficiently

## Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
python -m pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Test Coverage
- **Data Processor**: 100% success rate (15/15 tests passing)
- **Insights Engine**: Comprehensive anomaly detection testing
- **API Endpoints**: Full endpoint testing with async support
- **Frontend Components**: React component testing with theme support

## Project Structure

```
OpenHardwareMonitorDashboard/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI endpoints
│   │   ├── core/          # Configuration and settings
│   │   ├── models/        # Pydantic data models
│   │   └── services/      # Business logic services
│   ├── tests/             # Backend test suite
│   ├── requirements.txt   # Python dependencies
│   └── main.py           # FastAPI application entry
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   └── types/         # TypeScript type definitions
│   ├── tests/             # Frontend test suite
│   └── package.json       # Node.js dependencies
├── data/                  # CSV data files
└── docs/                  # Documentation
```

## Configuration

### Backend Settings
- **Data Directory**: Path to CSV files
- **Memory Limits**: Configurable file size and row limits
- **Chunk Size**: Memory-efficient data loading
- **Hardware Thresholds**: Customizable alert levels

### Frontend Settings
- **API Timeout**: 60-second request timeout
- **Chart Sampling**: Smart data point reduction
- **Theme**: Dark/light mode support with automatic preference saving

## API Endpoints

### Dashboard
- `GET /dashboard/overview?days={days}` - Dashboard overview
- `GET /dashboard/health-status` - System health status
- `GET /dashboard/trends` - Performance trends
- `GET /dashboard/performance-summary` - Performance summary

### Insights
- `GET /insights/analyze` - Period analysis
- `GET /insights/health-summary` - Health summary
- `GET /insights/by-metric/{metric}` - Insights by metric
- `GET /insights/by-level/{level}` - Insights by severity

### Metrics
- `GET /metrics/period` - Time series data
- `GET /metrics/system-info` - System information
- `GET /metrics/available-dates` - Available data dates

## Performance Features

### Memory Optimization
- **Chunked Loading**: Processes large files in manageable chunks
- **Garbage Collection**: Automatic memory cleanup
- **Data Sampling**: Intelligent data point reduction for charts
- **Efficient Storage**: Optimized data structures

### Large Dataset Handling
- **File Size Limits**: Configurable maximum file sizes
- **Row Limits**: Prevents memory overflow
- **Progress Logging**: Real-time processing feedback
- **Error Recovery**: Graceful handling of corrupted data

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: Ensure all tests pass
5. **Submit a pull request** with detailed description

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Write comprehensive tests for new features
- Update documentation for API changes
- Maintain test coverage above 80%

## Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version (3.11+ required)
- Install dependencies: `python -m pip install -r requirements.txt`
- If you encounter permission issues, run `cleanup-venv.bat` to remove corrupted virtual environments

**Frontend compilation errors**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Verify TypeScript configuration

**No data displayed**
- Check CSV file format and location
- Verify file naming convention: `OpenHardwareMonitorLog-YYYY-MM-DD.csv`
- Check backend logs for parsing errors
- Ensure data directory path is correctly configured in `backend/app/core/config.py`

**Memory issues with large files**
- Reduce `max_csv_size_mb` in settings
- Enable chunked loading
- Monitor system memory usage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Open Hardware Monitor**: For providing the data collection software
- **FastAPI**: For the excellent web framework
- **React**: For the powerful frontend framework
- **Chart.js**: For the beautiful data visualizations