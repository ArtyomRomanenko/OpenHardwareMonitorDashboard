# Changelog

All notable changes to the Open Hardware Monitor Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive testing framework with pytest and React Testing Library
- Enhanced insights engine with anomaly detection (Z-score, IQR, threshold-based)
- Memory optimization features for large CSV file handling
- Smart data sampling for chart visualization
- Period-specific insights analysis
- Detailed anomaly event tracking with timestamps and severity
- Baseline statistics calculation (mean, median, std, quartiles)
- Cross-metric insights generation
- Trend analysis and detection
- Data reliability warnings for poor quality data

### Changed
- Reworked insights engine to display insights only for selected date ranges
- Updated data processor to handle Open Hardware Monitor CSV format
- Improved frontend chart rendering with multiple chart types
- Enhanced error handling and user feedback
- Optimized memory usage for large datasets

### Fixed
- CSV parsing issues with Open Hardware Monitor file format
- Frontend chart rendering errors and type compatibility issues
- Backend API endpoint structure and response formatting
- Memory allocation issues with large CSV files
- Date filtering and time range selection problems
- Chart data sampling and statistics calculation

## [0.2.0] - 2024-01-XX

### Added
- Interactive dashboard with real-time metrics display
- Multiple chart types (line charts, scatter plots, pie charts)
- Date range selection (7, 14, 30 days)
- System health monitoring and alerts
- Performance summary and trend analysis
- Hardware insights and recommendations

### Changed
- Migrated from basic CSV parsing to intelligent data processing
- Enhanced frontend with TypeScript and modern React patterns
- Improved backend architecture with FastAPI and Pydantic

### Fixed
- Initial setup and dependency installation issues
- Basic CSV loading and parsing functionality
- Frontend compilation and module resolution errors

## [0.1.0] - 2024-01-XX

### Added
- Initial project structure and setup
- Basic FastAPI backend with CSV loading
- React frontend with basic chart display
- Open Hardware Monitor CSV format support
- Basic hardware metrics visualization

## Development Notes

### Current Status
- **Backend**: Core functionality implemented, testing in progress
- **Frontend**: UI components complete, testing environment ready
- **Testing**: 88% backend test success rate, frontend tests configured
- **Documentation**: Comprehensive guides and API documentation

### Known Issues
- Some data processor tests failing due to mocking and path issues
- Threshold-based anomaly detection needs refinement
- Reliability warning system requires adjustment

### Next Steps
- Fix remaining failing tests
- Improve test coverage to 90%+
- Add end-to-end testing
- Implement performance testing
- Add visual regression testing

### Technical Debt
- Some tests need better mocking strategies
- Error handling could be more comprehensive
- Performance optimization for very large datasets
- Additional test categories (security, load testing)

---

## Version History

- **0.1.0**: Initial project setup and basic functionality
- **0.2.0**: Enhanced features and improved architecture
- **Unreleased**: Testing framework and advanced insights engine

## Contributing

When contributing to this project, please:

1. Update this changelog with your changes
2. Follow the existing format and style
3. Group changes under appropriate categories (Added, Changed, Fixed, etc.)
4. Include relevant issue numbers or pull request references
5. Use clear, descriptive language for all changes

## Release Process

1. **Development**: Features developed in feature branches
2. **Testing**: Comprehensive testing of all changes
3. **Documentation**: Update relevant documentation
4. **Changelog**: Update this changelog with new version
5. **Release**: Tag and release new version
6. **Deployment**: Deploy to production environment
