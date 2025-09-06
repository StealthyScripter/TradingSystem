# Investment Portfolio API - Basic Tests

Simple test suite covering core functionality of the Investment Portfolio API.

## 📋 Overview

This test suite focuses on basic functionality:

- **Database operations** - Account and asset CRUD operations
- **API endpoints** - Core endpoints for portfolio management
- **Calculations** - Financial calculations and portfolio math
- **Services** - Basic portfolio service functionality

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
cd flexpesa-ai

# Install test dependencies
pip install -r tests/requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all basic tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py
pytest tests/test_api.py
pytest tests/test_calculations.py
pytest tests/test_services.py
```

### 3. Run Tests with Coverage

```bash
# Run with coverage report
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 📁 Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_database.py         # Database operations tests
├── test_api.py              # API endpoint tests
├── test_calculations.py     # Financial calculations tests
├── test_services.py         # Portfolio service tests
├── pytest.ini              # Pytest configuration
├── requirements-test.txt    # Test dependencies
└── README.md               # This file
```

## 🧪 Test Categories

### Database Tests (`test_database.py`)
- Account creation and management
- Asset creation and management
- Relationship testing (accounts ↔ assets)
- Basic CRUD operations
- Data integrity validation

### API Tests (`test_api.py`)
- Health check endpoints
- Account management endpoints
- Asset management endpoints
- Portfolio summary endpoints
- Basic error handling
- Simple workflow integration

### Calculation Tests (`test_calculations.py`)
- Asset value calculations (market value, cost basis, P&L)
- Account total value calculations
- Portfolio-level calculations
- Percentage calculations
- Edge cases (zero values, negative values, etc.)

### Service Tests (`test_services.py`)
- Portfolio service basic operations
- Account creation through service
- Asset addition through service
- Portfolio summary generation
- Service error handling
- Multi-user data isolation

## ⚙️ Configuration

### Environment Variables

Tests automatically set these environment variables:

```bash
TESTING=true
ENVIRONMENT=development
DEBUG=true
DISABLE_AUTH=true
DATABASE_URL=sqlite:///:memory:
```

### Test Database

Tests use an in-memory SQLite database that is:
- ✅ Fast and isolated
- ✅ Automatically cleaned up after each test
- ✅ No external dependencies
- ✅ Consistent across test runs

## 🔧 Running Specific Tests

### Run by Test File
```bash
pytest tests/test_database.py::TestDatabaseBasics::test_create_account
pytest tests/test_api.py::TestAccountEndpoints
pytest tests/test_calculations.py::TestAssetCalculations
```

### Run by Pattern
```bash
# Run all account-related tests
pytest -k "account"

# Run all calculation tests
pytest -k "calculation"

# Run all API tests
pytest -k "api"
```

### Run with Different Verbosity
```bash
# Minimal output
pytest -q

# Normal output
pytest

# Verbose output
pytest -v

# Very verbose output
pytest -vv
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Make sure you're in the correct directory
cd flexpesa-ai

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-test.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Database Issues
```bash
# Tests use in-memory database, but if you see database errors:
rm -f test_portfolio.db
pytest tests/test_database.py
```

#### Test Failures
```bash
# Run with more detail
pytest -vv --tb=long

# Run one test at a time to isolate issues
pytest tests/test_database.py::TestDatabaseBasics::test_create_account -v
```

#### Async Test Issues
```bash
# Make sure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

## 📊 Test Coverage

### View Coverage Report
```bash
# Generate coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML report
pytest --cov=app --cov-report=html
```

### Expected Coverage
- **Database Models**: 90%+
- **API Endpoints**: 80%+
- **Calculations**: 95%+
- **Services**: 85%+

## 🔄 Continuous Integration

These tests are designed to run in CI environments:

```yaml
# Example GitHub Actions
- name: Run Basic Tests
  run: |
    pip install -r requirements.txt
    pip install -r tests/requirements-test.txt
    pytest --cov=app
```

## 🚀 Next Steps

After basic tests are working:

1. **Add more test cases** for edge cases
2. **Add integration tests** for complete workflows
3. **Add performance tests** for response times
4. **Add mock market data** tests
5. **Add production health checks**

## 💡 Tips

- **Run tests frequently** during development
- **Write tests first** for new features (TDD)
- **Keep tests simple** and focused on one thing
- **Use descriptive test names** that explain what's being tested
- **Mock external dependencies** to make tests reliable
- **Test edge cases** like empty data, invalid input, etc.

---

## 🆘 Getting Help

If tests are failing:

1. Check the **error message** carefully
2. Run **individual tests** to isolate the problem
3. Check **prerequisites** (dependencies, environment)
4. Look at **test logs** for more details
5. Verify **database connectivity** and **API server** status

For more complex testing scenarios, refer to the full test documentation.