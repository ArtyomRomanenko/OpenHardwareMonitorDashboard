# Changelog

All notable changes to the Open Hardware Monitor Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced error handling with retry mechanisms
- Fallback options for different time ranges
- Improved loading feedback and progress indicators

## [1.2.0] - 2025-01-XX

### Added
- **Multiple Chart Types**: Line, Pie, Scatter, and Doughnut charts
- **Advanced Metric Filtering**: Checkbox-based metric type selection
- **Chart Type Selection**: Radio buttons for choosing visualization styles
- **14-Day Time Range**: Additional time period option
- **Data Sampling**: Automatic optimization for large datasets
- **Error Boundaries**: Crash protection for chart rendering
- **Performance Optimization**: Memory-efficient data processing

### Changed
- **Metrics Page**: Completely redesigned with multiple chart types
- **Chart Interactivity**: Enhanced hover tooltips, zoom, and pan
- **Error Handling**: Comprehensive error messages with troubleshooting tips
- **Loading States**: Better feedback for long-running requests
- **API Timeout**: Increased from 10s to 60s for large datasets

### Fixed
- **Permission Issues**: Fixed startup script permission errors
- **Chart Rendering**: Resolved "Maximum call stack size exceeded" errors
- **Data Filtering**: Metric type selection now properly affects chart display
- **System Info**: Dedicated page for system information display
- **Memory Optimization**: Improved handling of large CSV files

### Removed
- **System Info Block**: Removed from Metrics tab (moved to dedicated page)
- **Old Chart Types**: Replaced with enhanced Chart.js implementations

## [1.1.0] - 2025-01-XX

### Added
- **Basic Dashboard**: Main overview with system health status
- **Time Series Visualization**: Interactive charts for different periods
- **Hardware Insights**: AI-powered analysis and recommendations
- **System Information**: Hardware specifications and data summary
- **API Endpoints**: Complete REST API for data access
- **Memory Optimization**: Chunked CSV loading and file size limits

### Changed
- **Data Processing**: Improved CSV parsing for Open Hardware Monitor format
- **Error Handling**: Better error messages and user feedback
- **Performance**: Optimized for large datasets

### Fixed
- **CSV Parsing**: Corrected header detection and column mapping
- **Date Filtering**: Fixed time range selection logic
- **Data Loading**: Resolved issues with large file processing

## [1.0.0] - 2025-01-XX

### Added
- **Initial Release**: Basic Open Hardware Monitor dashboard
- **FastAPI Backend**: Python backend with data processing
- **React Frontend**: TypeScript frontend with basic charts
- **CSV Parsing**: Support for Open Hardware Monitor log files
- **Basic Charts**: Simple time series visualization
- **Project Structure**: Organized backend and frontend architecture

## Technical Details

### Backend Changes
- **Data Processor**: Enhanced CSV loading with memory optimization
- **Insights Engine**: Improved hardware health analysis
- **API Routes**: Added comprehensive endpoints for all features
- **Configuration**: Enhanced settings with memory optimization options

### Frontend Changes
- **Chart.js Integration**: Full Chart.js and React-Chartjs-2 implementation
- **Component Architecture**: Modular, reusable components
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

### Performance Improvements
- **Memory Management**: Chunked loading, file size limits, row limits
- **Data Sampling**: Automatic optimization for large datasets
- **API Optimization**: Increased timeouts and better error handling
- **Chart Rendering**: Optimized for performance and stability

## Migration Guide

### From v1.1.0 to v1.2.0
- No breaking changes in API
- Enhanced chart functionality with new chart types
- Improved error handling and user experience
- Better performance for large datasets

### From v1.0.0 to v1.1.0
- Updated data directory configuration format
- Enhanced CSV parsing for Open Hardware Monitor format
- Improved memory management and performance

## Known Issues

### v1.2.0
- None currently known

### v1.1.0
- ~~Permission issues with startup scripts~~ (Fixed in v1.2.0)
- ~~Chart rendering errors with large datasets~~ (Fixed in v1.2.0)

## Future Plans

### v1.3.0 (Planned)
- Real-time data streaming
- Advanced analytics and machine learning insights
- Export functionality for reports
- Mobile app support

### v1.4.0 (Planned)
- Multi-user support with authentication
- Database backend for historical data
- Advanced alerting system
- API rate limiting and security improvements
