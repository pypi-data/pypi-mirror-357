# Test Configuration for Flask-BunnyStream

## Running Tests

To run the comprehensive test suite for FlaskBaseEvent:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=flask_bunnystream --cov-report=term-missing

# Run specific test file
pytest tests/test_events.py -v

# Run specific test
pytest tests/test_events.py::TestFlaskBaseEvent::test_get_client_data_chrome_browser -v
```

## Test Coverage

The test suite provides 100% code coverage for the FlaskBaseEvent class, testing:

- ✅ Initialization with and without Flask extension
- ✅ Client IP extraction from various headers
- ✅ User agent parsing for different browsers
- ✅ Mobile device detection
- ✅ Error handling and edge cases
- ✅ Metadata setting and integration
- ✅ Full workflow integration tests

## Test Structure

The tests are organized in `tests/test_events.py` with comprehensive coverage of:

1. **Inheritance Testing**: Verifies proper inheritance from BaseEvent
2. **Initialization Testing**: Tests both success and failure scenarios
3. **IP Address Extraction**: Various header configurations and edge cases
4. **User Agent Parsing**: Different browsers, mobile devices, and edge cases
5. **Error Handling**: Runtime errors and malformed data
6. **Integration Testing**: Complete workflow from initialization to metadata setting

All tests use proper mocking to isolate functionality and avoid external dependencies.
