# Investment Portfolio API - Test Suite

A comprehensive test suite for the Investment Portfolio API that can run safely in both development and production environments to detect regressions, validate calculations, and ensure system health.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Production Testing](#production-testing)
- [Test Configuration](#test-configuration)
- [Coverage Reports](#coverage-reports)
- [Continuous Integration](#continuous-integration)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

This test suite includes:

- **1000+ tests** covering all API endpoints, services, and calculations
- **Production-safe tests** that can run without modifying data
- **Financial calculation validation** with known mathematical results
- **Performance benchmarks** to detect regressions
- **Integration tests** for complete workflows
- **Health checks** for system monitoring
- **Mock services** for reliable testing without external dependencies

### Key Features

✅ **Production Safe** - Tests can run in production without data modification
✅ **Comprehensive Coverage** - Tests API, database, services, and calculations
✅ **Performance Monitoring** - Detects performance regressions
✅ **Financial Accuracy** - Validates all portfolio calculations
✅ **CI/CD Ready** - Integrates with GitHub Actions, Jenkins, etc.
✅ **Detailed Reporting** - HTML reports with coverage metrics

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd flexpesa-ai

# Install test dependencies
pip install -r requirements-test.txt

# Or install specific test packages
pip install pytest pytest-asyncio pytest-cov requests-mock
```

### 2. Run Basic Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m "unit"           # Unit tests only
pytest -m "integration"    # Integration tests
pytest -m "production"     # Production-safe tests
```

### 3. View Results

```bash
# View coverage report
open htmlcov/index.html

# View test results
cat pytest-report.html
```

## 📁 Test Structure

```
flexpesa-ai/tests/
├── conftest.py                 # Test configuration and fixtures
├── test_api.py                # API endpoint tests
├── test_database.py           # Database operations tests
├── test_calculations.py       # Financial calculations tests
├── test_portfolio_service.py  # Portfolio service tests
├── test_market_data.py        # Market data service tests
├── test_production_health.py  # Production health checks
├── test_integration.py        # End-to-end integration tests
├── pytest.ini                # Pytest configuration
├── requirements-test.txt      # Test dependencies
└── README.md                  # This file
```

## 🏷️ Test Categories

Tests are organized into categories using pytest markers:

### Unit Tests (`-m unit`)
Fast, isolated tests for individual functions and classes:
```bash
pytest -m unit
```

### Integration Tests (`-m integration`)
Test interactions between components:
```bash
pytest -m integration
```

### Production Tests (`-m production`)
Safe to run in production for health monitoring:
```bash
pytest -m production
```

### Database Tests (`-m database`)
Tests requiring database access:
```bash
pytest -m database
```

### API Tests (`-m api`)
Tests for REST API endpoints:
```bash
pytest -m api
```

### Calculation Tests (`-m calculations`)
Tests for financial calculations and formulas:
```bash
pytest -m calculations
```

### Performance Tests (`-m performance`)
Performance benchmarks and load tests:
```bash
pytest -m performance
```

## 🏃‍♂️ Running Tests

### Development Environment

```bash
# Run all tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto

# Run with live logging
pytest -s --log-cli-level=INFO

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestPortfolioEndpoints::test_portfolio_summary
```

### Test Selection Examples

```bash
# Run fast tests only
pytest -m "unit and not slow"

# Run API tests excluding auth
pytest -m "api and not auth"

# Run database tests for PostgreSQL only
pytest -m "database" -k "postgresql"

# Run performance tests with benchmarking
pytest -m "performance" --benchmark-only
```

### Environment Variables

```bash
# Set test environment
export TESTING=true
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///./test_portfolio.db

# Production safe mode
export PRODUCTION_SAFE_MODE=true

# Run tests
pytest
```

## 🏭 Production Testing

### Safe Production Tests

The test suite includes production-safe tests that:
- ✅ Only read data, never modify
- ✅ Test system health and performance
- ✅ Validate calculations with existing data
- ✅ Check for regressions
- ❌ Never create, update, or delete data

```bash
# Run only production-safe tests
pytest -m production

# Run with production database
export DATABASE_URL=postgresql://user:pass@prod-host:5432/portfolio_db
export PRODUCTION_SAFE_MODE=true
pytest -m production

# Health check tests only
pytest tests/test_production_health.py::TestProductionHealth
```

### Production Health Checks

```bash
# Database connectivity and performance
pytest tests/test_production_health.py::TestProductionHealth::test_database_connectivity

# API endpoint availability
pytest tests/test_production_health.py::TestProductionHealth::test_api_endpoint_availability

# Data integrity validation
pytest tests/test_production_health.py::TestProductionDataIntegrity

# Performance regression detection
pytest tests/test_production_health.py::TestProductionPerformance
```

### Regression Detection

```bash
# Run regression detection tests
pytest tests/test_production_health.py::TestProductionRegressionDetection

# Check for performance regressions
pytest -m "production and performance"

# Validate financial calculations
pytest -m "production and calculations"
```

## ⚙️ Test Configuration

### Pytest Configuration (`pytest.ini`)

Key settings:
- Test discovery patterns
- Custom markers
- Coverage settings
- Logging configuration
- Timeout settings

### Environment Configuration

Create `.env.test` file:
```env
TESTING=true
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./test_portfolio.db
SECRET_KEY=test-secret-key
PRODUCTION_SAFE_MODE=false
```

### Database Configuration

Tests use isolated test databases:
- **SQLite** for unit tests (fast, isolated)
- **PostgreSQL** for integration tests (production-like)
- **Mock data** for external API tests

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# Generate XML report (for CI)
pytest --cov=app --cov-report=xml
```

### Coverage Targets

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **Critical Paths**: 100% coverage (calculations, API endpoints)

### Coverage Exclusions

```python
# pragma: no cover - for test-only code
# pragma: no cover - for error handling that can't be easily tested
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml -v

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pip install -r requirements-test.txt'
                sh 'pytest --cov=app --cov-report=xml --junit-xml=junit.xml'
            }
            post {
                always {
                    junit 'junit.xml'
                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: true,
                               keepAll: true, reportDir: 'htmlcov', reportFiles: 'index.html',
                               reportName: 'Coverage Report'])
                }
            }
        }
    }
}
```

## ✍️ Writing Tests

### Test Naming Convention

```python
# Good test names
def test_create_account_with_valid_data():
def test_calculate_portfolio_return_positive_gain():
def test_api_returns_401_when_unauthenticated():

# Test class naming
class TestPortfolioCalculations:
class TestAPIEndpoints:
class TestDatabaseOperations:
```

### Test Structure

```python
def test_example():
    # Arrange - Set up test data
    user_id = "test_user"
    account_data = {"name": "Test Account", "type": "brokerage"}

    # Act - Execute the code being tested
    result = portfolio_service.create_account(account_data, user_id)

    # Assert - Verify the results
    assert result.name == "Test Account"
    assert result.clerk_user_id == user_id
```

### Using Fixtures

```python
def test_with_portfolio_data(sample_portfolio_data):
    """Test using the sample_portfolio_data fixture"""
    account = sample_portfolio_data["account"]
    assets = sample_portfolio_data["assets"]

    assert len(assets) == 3
    assert account.name == "Test Portfolio"
```

### Mocking External Services

```python
def test_with_mock_market_data(mock_market_data_service):
    """Test using mock market data service"""
    mock_market_data_service.get_current_prices.return_value = {
        "AAPL": 150.0
    }

    # Test code that uses market data service
```

### Production-Safe Tests

```python
@pytest.mark.production
def test_production_safe_calculation():
    """This test only reads data, never modifies"""
    # Only use existing data
    # Only perform read operations
    # Only validate calculations
    pass
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operations"""
    result = await async_service.get_data()
    assert result is not None
```

## 🛠️ Troubleshooting

### Common Issues

#### Tests Fail with Database Errors

```bash
# Check database connection
pytest tests/test_database.py::TestDatabaseConnection::test_database_connection

# Reset test database
rm test_portfolio.db
pytest tests/test_database.py::TestDatabaseConnection::test_create_tables
```

#### Import Errors

```bash
# Check if all dependencies are installed
pip install -r requirements-test.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Slow Test Performance

```bash
# Run tests in parallel
pip install pytest-xdist
pytest -n auto

# Profile slow tests
pytest --durations=10
```

#### Mock Issues

```bash
# Clear mock state between tests
pytest --tb=short -v

# Debug mock calls
pytest -s --log-cli-level=DEBUG
```

### Test Database Issues

```bash
# PostgreSQL connection issues
export DATABASE_URL=postgresql://portfolio_user:portfolio_password@localhost:5432/test_portfolio_db

# SQLite permission issues
chmod 664 test_portfolio.db
```

### Coverage Issues

```bash
# Generate detailed coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Exclude test files from coverage
pytest --cov=app --cov-config=.coveragerc
```

## 📈 Performance Benchmarking

### Benchmark Tests

```bash
# Run performance benchmarks
pytest -m performance --benchmark-only

# Compare benchmarks
pytest --benchmark-compare

# Save benchmark results
pytest --benchmark-save=baseline
```

### Memory Testing

```bash
# Test for memory leaks
pytest -m "performance" --memprof

# Monitor memory usage
pytest tests/test_integration.py::TestLongRunningIntegration::test_memory_leak_detection
```

## 🔍 Debugging Tests

### Debug Mode

```bash
# Run with debugger
pytest --pdb

# Run with verbose output
pytest -vvv -s

# Run with logging
pytest --log-cli-level=DEBUG
```

### Test Isolation

```bash
# Run single test
pytest tests/test_api.py::TestPortfolioEndpoints::test_portfolio_summary -v

# Run with fresh database
pytest --create-db
```

## 📊 Test Metrics

### Key Metrics to Monitor

- **Test Coverage**: Aim for 85%+ overall
- **Test Execution Time**: < 5 minutes for full suite
- **Failure Rate**: < 1% for production tests
- **Performance Benchmarks**: Within 10% of baseline

### Reporting

```bash
# Generate comprehensive report
pytest --html=report.html --self-contained-html

# JSON report for automation
pytest --json-report --json-report-file=report.json

# JUnit XML for CI integration
pytest --junit-xml=junit.xml
```

## 🚀 Best Practices

### Test Organization

1. **Group related tests** in classes
2. **Use descriptive test names** that explain what's being tested
3. **Keep tests isolated** - no dependencies between tests
4. **Mock external services** for reliable testing
5. **Test edge cases** and error conditions

### Performance

1. **Use fixtures** for common test data
2. **Run tests in parallel** when possible
3. **Mock expensive operations** (API calls, file I/O)
4. **Use appropriate test marks** to control execution

### Maintenance

1. **Keep tests updated** with code changes
2. **Remove obsolete tests** when features are removed
3. **Refactor test code** to reduce duplication
4. **Document complex test scenarios**

## 📞 Support

### Getting Help

- **Check test output** for specific error messages
- **Review test logs** in `pytest.log`
- **Check database connectivity** with health tests
- **Verify environment variables** are set correctly

### Contributing

1. **Add tests** for new features
2. **Update tests** when changing existing functionality
3. **Follow naming conventions** for consistency
4. **Add appropriate test markers**
5. **Update documentation** when needed

---

## 🎯 Summary

This comprehensive test suite provides:

- ✅ **Confidence** in code quality and correctness
- ✅ **Protection** against regressions
- ✅ **Documentation** of expected behavior
- ✅ **Performance** monitoring and benchmarks
- ✅ **Production** health monitoring

**Run tests frequently**, especially before deploying to production, to ensure system reliability and catch issues early.

For questions or issues with the test suite, check the troubleshooting section or review individual test files for specific testing scenarios.