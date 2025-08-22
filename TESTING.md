# Testing Guide

This document provides comprehensive information about the testing framework for the Open Hardware Monitor Dashboard project.

## Test Status Overview

### Current Test Results
- **Insights Engine Tests**: 15 passed, 2 failed (88% success rate)
- **Data Processor Tests**: 8 passed, 7 failed (53% success rate)
- **API Endpoint Tests**: Ready for execution (requires backend fixes)
- **Frontend Tests**: Environment configured, tests ready

### Test Coverage Goals
- **Backend**: Target 90%+ coverage
- **Frontend**: Target 80%+ coverage
- **Integration**: End-to-end API testing
- **Performance**: Memory and load testing

## Test Structure

### Backend Tests (`backend/tests/`)

#### 1. Insights Engine Tests (`test_insights_engine.py`)
**Status**: ✅ Mostly Working (15/17 tests passing)

**Test Categories**:
- **Initialization**: Engine setup and configuration
- **Data Filtering**: Period-based data filtering
- **Anomaly Detection**: Z-score, IQR, and threshold methods
- **Data Processing**: Anomaly removal and baseline calculation
- **Insight Generation**: Various insight types and recommendations
- **Health Summary**: System health analysis

**Known Issues**:
- Threshold-based anomaly detection not working as expected
- Reliability warning system needs adjustment

**Key Tests**:
```python
def test_anomaly_detection_z_score(self, insights_engine)
def test_anomaly_detection_iqr(self, insights_engine)
def test_create_anomaly_insight(self, insights_engine)
def test_analyze_period_with_anomalies(self, insights_engine)
```

#### 2. Data Processor Tests (`test_data_processor.py`)
**Status**: ⚠️ Partially Working (8/15 tests passing)

**Test Categories**:
- **Initialization**: Processor setup and configuration
- **File Operations**: CSV loading and parsing
- **Data Processing**: CSV cleaning and transformation
- **Metric Extraction**: Hardware metric identification
- **Memory Management**: Large file handling and optimization

**Known Issues**:
- CSV loading tests failing due to path/mocking issues
- Metric extraction tests failing due to data structure mismatches
- Some tests expecting different method signatures

**Key Tests**:
```python
def test_get_available_dates(self, data_processor)
def test_process_csv_data(self, data_processor)
def test_extract_metrics(self, data_processor)
def test_memory_optimization_settings(self, data_processor)
```

#### 3. API Endpoint Tests (`test_api_endpoints.py`)
**Status**: 🔧 Ready for Execution (requires backend fixes)

**Test Categories**:
- **Dashboard API**: Overview, health status, trends
- **Insights API**: Analysis, health summary, filtering
- **Metrics API**: Data retrieval, system info
- **Error Handling**: Invalid requests and server errors

**Implementation Notes**:
- Uses `httpx.AsyncClient` for async testing
- Comprehensive mocking of dependencies
- Tests both success and failure scenarios

### Frontend Tests (`frontend/tests/`)

#### 1. Component Tests
**Status**: ✅ Environment Ready

**Test Categories**:
- **Page Components**: Dashboard, Metrics, Insights pages
- **Chart Components**: Chart rendering and interactions
- **Form Components**: Date selection and filtering
- **Utility Functions**: Data processing and formatting

**Testing Framework**:
- **React Testing Library**: Component rendering and user interactions
- **Jest**: Test runner and assertion library
- **TypeScript**: Type-safe testing

## Running Tests

### Backend Tests

#### Prerequisites
```bash
cd backend
python -m pip install -r test-requirements.txt
```

#### Basic Test Execution
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_insights_engine.py -v

# Run specific test method
python -m pytest tests/test_insights_engine.py::TestInsightsEngine::test_anomaly_detection_z_score -v
```

#### Coverage Reports
```bash
# Generate coverage report
python -m pytest tests/ --cov=app --cov-report=html

# View coverage in browser
# Open backend/htmlcov/index.html
```

#### Test Categories
```bash
# Run only unit tests
python -m pytest tests/ -m "unit"

# Run only integration tests
python -m pytest tests/ -m "integration"

# Run tests with specific markers
python -m pytest tests/ -m "slow or memory"
```

### Frontend Tests

#### Prerequisites
```bash
cd frontend
npm install
```

#### Test Execution
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm run test:coverage

# Run tests with specific pattern
npm test -- --testNamePattern="Dashboard"
```

## Test Data and Mocking

### Mock Data Strategy

#### 1. Hardware Metrics Mocking
```python
# Mock TimeSeriesData
mock_metric = Mock(
    timestamps=[datetime.now()],
    values=[65.0, 67.0, 69.0],
    metric_type=Mock(value='cpu_temperature'),
    component='cpu',
    unit='°C'
)
```

#### 2. CSV Data Mocking
```python
# Mock CSV DataFrame
mock_df = pd.DataFrame({
    'Time': ['08/20/2025 00:00:03', '08/20/2025 00:00:08'],
    'CPU Core #1': [3.125, 10.9375],
    'Memory': [43.7650833, 43.7798424],
    'GPU Core': [49, 47]
})
```

#### 3. API Response Mocking
```python
# Mock API responses
mock_response = Mock(
    status_code=200,
    json=lambda: {
        'insights': [...],
        'summary': {...}
    }
)
```

### Test Fixtures

#### Backend Fixtures
```python
@pytest.fixture
def data_processor():
    """Create a DataProcessor instance for testing"""
    with patch('app.services.data_processor.settings') as mock_settings:
        mock_settings.data_directory = "test_data"
        mock_settings.max_csv_size_mb = 100
        mock_settings.max_rows_per_file = 100000
        mock_settings.chunk_size = 10000
        processor = DataProcessor()
        return processor

@pytest.fixture
def insights_engine():
    """Create an InsightsEngine instance for testing"""
    return InsightsEngine()
```

#### Frontend Fixtures
```typescript
// Mock API responses
const mockApiResponse = {
  insights: [
    {
      id: '1',
      title: 'Test Insight',
      description: 'Test description',
      level: 'warning',
      metric_type: 'cpu_temperature'
    }
  ]
};

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve(mockApiResponse),
    ok: true
  })
);
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    memory: Memory-intensive tests
```

### Jest Configuration (`package.json`)
```json
{
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/src/setupTests.ts"],
    "moduleNameMapping": {
      "^@/(.*)$": "<rootDir>/src/$1"
    },
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.d.ts"
    ]
  }
}
```

## Debugging Tests

### Common Test Issues

#### 1. Import Errors
**Problem**: Module not found errors
**Solution**: Check import paths and sys.path modifications

#### 2. Mock Configuration Issues
**Problem**: Mocks not working as expected
**Solution**: Verify patch decorators and mock return values

#### 3. Async Test Issues
**Problem**: Async tests failing
**Solution**: Use proper async/await syntax and AsyncClient

#### 4. Data Type Mismatches
**Problem**: Type errors in tests
**Solution**: Ensure mock data matches expected types

### Debug Commands
```bash
# Run tests with maximum verbosity
python -m pytest tests/ -vvv -s

# Run single test with debugger
python -m pytest tests/test_file.py::test_method -s --pdb

# Check test collection
python -m pytest tests/ --collect-only

# Run tests with specific Python version
python3.11 -m pytest tests/
```

## Performance Testing

### Memory Testing
```python
# Test memory optimization
def test_memory_optimization_settings(self, data_processor):
    """Test memory optimization configuration"""
    assert hasattr(data_processor, 'data_directory')
    assert str(data_processor.data_directory) == "test_data"
```

### Large File Testing
```python
# Test large CSV handling
def test_large_file_handling(self, data_processor):
    """Test handling of large CSV files"""
    # Create 10k row CSV file
    large_csv_content = "Time,CPU,Memory\n"
    for i in range(10000):
        large_csv_content += f"08/20/2025 00:{i:02d}:00,{i % 100},{50 + i % 30}\n"
    
    # Test processing without crashes
    df = data_processor.load_csv_data('2024-01-15')
    assert df is not None
    assert len(df) > 0
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/test-requirements.txt
    
    - name: Run backend tests
      run: |
        cd backend
        python -m pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## Contributing to Tests

### Adding New Tests

#### 1. Test Naming Convention
```python
def test_feature_name_expected_behavior(self, fixture_name):
    """Test description of what is being tested"""
    # Arrange
    input_data = "test input"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == "expected output"
```

#### 2. Test Documentation
```python
def test_anomaly_detection_threshold(self, insights_engine):
    """Test threshold-based anomaly detection for temperatures
    
    This test verifies that the system correctly identifies
    temperature values above critical thresholds and classifies
    them as severe anomalies.
    """
```

#### 3. Test Data Setup
```python
def setUp(self):
    """Set up test data and fixtures"""
    self.test_data = [
        {'timestamp': '2024-01-15 12:00:00', 'value': 95.0},
        {'timestamp': '2024-01-15 12:01:00', 'value': 98.0},
        {'timestamp': '2024-01-15 12:02:00', 'value': 102.0}
    ]
```

### Test Maintenance

#### 1. Regular Updates
- Update tests when API changes
- Maintain mock data accuracy
- Keep test dependencies current

#### 2. Performance Monitoring
- Track test execution time
- Monitor memory usage
- Identify slow tests

#### 3. Coverage Tracking
- Maintain coverage targets
- Identify uncovered code paths
- Add tests for new features

## Troubleshooting

### Common Test Failures

#### 1. Backend Tests
```bash
# Import errors
ModuleNotFoundError: No module named 'app.main'
# Solution: Check sys.path and import statements

# Mock errors
TypeError: 'Mock' object is not callable
# Solution: Use proper mock configuration

# Async errors
RuntimeError: Event loop is closed
# Solution: Use proper async test setup
```

#### 2. Frontend Tests
```bash
# Component rendering errors
Error: Uncaught [Error: Element type is invalid]
# Solution: Check component imports and exports

# Mock API errors
TypeError: fetch is not a function
# Solution: Mock fetch properly in test setup

# TypeScript errors
TS2345: Argument of type 'X' is not assignable to parameter of type 'Y'
# Solution: Fix type definitions and mock data
```

### Getting Help

#### 1. Check Test Logs
```bash
# Backend test logs
python -m pytest tests/ -v -s

# Frontend test logs
npm test -- --verbose
```

#### 2. Debug Mode
```bash
# Backend debug
python -m pytest tests/ --pdb

# Frontend debug
npm test -- --runInBand --no-cache
```

#### 3. Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)

## Future Improvements

### Planned Enhancements
1. **End-to-End Testing**: Full application workflow testing
2. **Performance Testing**: Load and stress testing
3. **Visual Regression Testing**: UI component visual testing
4. **API Contract Testing**: OpenAPI specification validation
5. **Security Testing**: Vulnerability and penetration testing

### Test Infrastructure
1. **Test Database**: Dedicated test data management
2. **Test Containers**: Isolated testing environments
3. **Parallel Testing**: Faster test execution
4. **Test Reporting**: Enhanced coverage and performance reports
