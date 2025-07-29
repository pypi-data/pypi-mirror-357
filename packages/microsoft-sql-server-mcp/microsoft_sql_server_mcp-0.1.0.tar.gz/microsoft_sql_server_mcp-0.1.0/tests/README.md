# MSSQL MCP Server Test Suite

This directory contains comprehensive tests to ensure the MSSQL MCP Server is production-ready.

## Test Structure

### Unit Tests

- **`test_config.py`**: Tests for configuration handling
  - Environment variable parsing
  - Connection string formatting
  - Azure SQL detection
  - LocalDB support
  - Windows Authentication
  - Input validation

- **`test_server.py`**: Basic server functionality tests
  - Server initialization
  - Tool listing
  - Basic error handling

### Security Tests

- **`test_security.py`**: Security and SQL injection prevention
  - SQL injection prevention in table names
  - Query result sanitization
  - Input validation
  - Resource access control
  - Permission testing

### Integration Tests

- **`test_integration.py`**: MCP protocol and end-to-end tests
  - Full MCP lifecycle testing
  - Concurrent request handling
  - Database integration scenarios
  - Transaction handling
  - Connection pooling
  - Edge cases (empty results, large datasets, special characters)

### Error Handling Tests

- **`test_error_handling.py`**: Resilience and recovery testing
  - Connection failures (timeout, auth, network)
  - Query errors (syntax, permissions, deadlocks)
  - Resource errors (invalid URIs, missing tables)
  - Recovery scenarios
  - Memory and resource cleanup

### Performance Tests

- **`test_performance.py`**: Performance and load testing
  - Query response time
  - Concurrent query performance
  - Large result set handling
  - Memory usage stability
  - Burst load handling
  - Sustained load testing
  - Scalability testing

## Running Tests

### Basic Test Run
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_security.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/mssql_mcp_server --cov-report=html
```

### Test Categories

Run specific categories of tests:

```bash
# Only unit tests
pytest tests/test_config.py tests/test_server.py

# Only security tests
pytest tests/test_security.py

# Only performance tests (may take longer)
pytest tests/test_performance.py

# Exclude slow tests
pytest -m "not slow"
```

### Integration Tests with Real Database

To run integration tests against a real SQL Server:

```bash
# Set up environment variables
export MSSQL_SERVER=localhost
export MSSQL_USER=sa
export MSSQL_PASSWORD=YourStrong@Passw0rd
export MSSQL_DATABASE=TestDB

# Run integration tests
pytest tests/test_integration.py
```

### Docker-based Testing

Run tests in a Docker environment:

```bash
# Start SQL Server container
docker-compose -f docker-compose.example.yml up -d sqlserver

# Run tests
docker-compose -f docker-compose.example.yml run --rm mssql-mcp-server pytest

# Clean up
docker-compose -f docker-compose.example.yml down
```

## Test Coverage Goals

- **Unit Tests**: >90% coverage of core functionality
- **Integration Tests**: All MCP protocol operations
- **Security Tests**: All user input paths
- **Error Tests**: All error conditions
- **Performance Tests**: Load and scalability validation

## Writing New Tests

When adding new features, ensure:

1. **Unit tests** for the feature logic
2. **Integration tests** for MCP protocol interaction
3. **Security tests** if handling user input
4. **Error tests** for failure scenarios
5. **Performance tests** if performance-critical

### Test Template

```python
import pytest
from unittest.mock import Mock, patch
from mssql_mcp_server.server import your_function

class TestYourFeature:
    """Test suite for your feature."""
    
    def test_normal_operation(self):
        """Test normal operation."""
        # Arrange
        mock_conn = Mock()
        
        # Act
        with patch('pymssql.connect', return_value=mock_conn):
            result = your_function()
        
        # Assert
        assert result is not None
    
    def test_error_handling(self):
        """Test error scenarios."""
        with pytest.raises(ExpectedException):
            your_function(invalid_input)
```

## CI/CD Integration

Tests are automatically run on:
- Every push to main/develop branches
- Every pull request
- Daily scheduled runs
- Manual workflow dispatch

See `.github/workflows/ci.yml` for the complete CI/CD pipeline.

## Performance Benchmarks

Expected performance metrics:
- Simple query response: <100ms
- 100 concurrent queries: <5s total
- 10,000 row result: <10s
- Memory growth over 100 operations: <50MB

## Security Testing

Security tests verify:
- SQL injection prevention
- Input validation
- Permission enforcement
- Safe error messages
- Resource access control

## Troubleshooting

Common test issues:

1. **Import errors**: Ensure package is installed with `pip install -e .`
2. **Database connection**: Check environment variables
3. **Permission errors**: Ensure test database user has necessary permissions
4. **Timeout errors**: Increase test timeouts for slower systems
5. **Memory errors**: Close connections properly in tests