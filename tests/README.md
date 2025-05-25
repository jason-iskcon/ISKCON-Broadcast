# ISKCON-Broadcast Testing Framework

## Overview

This testing framework provides comprehensive test coverage for the ISKCON-Broadcast camera plugin system, following the same high-quality standards as ISKCON-Translate. The framework is organized into three main categories: unit tests, system integration tests, and performance tests.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── pytest.ini              # Pytest settings and markers
├── test_data/              # Test configuration files
│   ├── test_config.yaml
│   └── test_orchestration.yaml
├── unit/                   # Unit tests (22 total)
│   ├── test_camera_interface.py
│   ├── test_camera_registry.py
│   └── test_mock_camera.py
├── sys/                    # System integration tests (10 total)
│   └── test_camera_integration.py
└── perf/                   # Performance tests (10 total)
    └── test_camera_performance.py
```

## Current Test Status

**Total Tests: 63**
- ✅ **22 Passing** (35%)
- ❌ **41 Failing** (65%)

### Passing Tests by Category

#### Unit Tests (9/31 passing)
- ✅ Camera interface abstract class validation
- ✅ Camera registry plugin system
- ✅ Camera registration and factory patterns
- ✅ Mock camera basic functionality

#### System Integration Tests (7/10 passing)
- ✅ Multiple camera creation and management
- ✅ YAML configuration loading
- ✅ Camera switching and mode changes
- ✅ Concurrent camera operations
- ✅ Performance under load
- ✅ Configuration validation
- ✅ Long-running stability

#### Performance Tests (0/10 passing)
- ❌ All performance tests need API updates

## Test Categories and Markers

### Pytest Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - System integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.camera` - Camera-related tests
- `@pytest.mark.orchestration` - Orchestration tests
- `@pytest.mark.display` - Display-related tests

### Running Tests

```bash
# Run all tests
Scripts\python.exe -m pytest tests/ -v

# Run by category
Scripts\python.exe -m pytest tests/unit/ -v          # Unit tests only
Scripts\python.exe -m pytest tests/sys/ -v           # Integration tests only
Scripts\python.exe -m pytest tests/perf/ -v          # Performance tests only

# Run by marker
Scripts\python.exe -m pytest -m unit -v              # Unit tests
Scripts\python.exe -m pytest -m integration -v       # Integration tests
Scripts\python.exe -m pytest -m performance -v       # Performance tests
Scripts\python.exe -m pytest -m "not slow" -v        # Exclude slow tests

# Run specific test
Scripts\python.exe -m pytest tests/unit/test_camera_registry.py::TestCameraRegistry::test_camera_plugin_decorator -v
```

## Key Features

### Comprehensive Fixtures
- **Camera Configurations**: Mock, IP camera, and multi-camera setups
- **Clean Registry**: Ensures isolated test environment
- **Mock Dependencies**: CV2, pygame, threading mocks
- **Performance Timing**: Built-in performance measurement
- **Log Capture**: Captures and validates log messages
- **Test Data**: YAML configuration files for testing

### Test Coverage Areas

#### Unit Tests
- **Camera Interface**: Abstract base class validation
- **Camera Registry**: Plugin registration and factory patterns
- **Mock Camera**: Frame generation, PTZ commands, threading

#### System Integration Tests
- **Multi-Camera Management**: Creating and coordinating multiple cameras
- **Configuration Loading**: YAML-based configuration parsing
- **Error Recovery**: Handling camera failures gracefully
- **Concurrent Operations**: Thread-safe camera operations
- **Plugin Hot Reload**: Dynamic camera type registration

#### Performance Tests
- **Throughput**: Frame capture rates and processing speed
- **Latency**: Frame request response times
- **Memory Usage**: Memory consumption and leak detection
- **CPU Usage**: Resource utilization monitoring
- **Scalability**: Performance with increasing camera counts
- **Stability**: Long-term operation reliability

## Known Issues and Next Steps

### Issues to Fix
1. **API Mismatch**: Performance tests need to use correct `CameraRegistry.create_camera(type, id, config)` signature
2. **Interface Mismatch**: Tests expect different abstract methods than actual implementation
3. **Mock Camera Features**: Some tests expect features not yet implemented in MockCamera
4. **PTZ Commands**: Tests expect individual PTZ methods, but implementation uses `send_ptz_command()`

### Immediate Next Steps
1. Update performance tests to use correct API
2. Align test expectations with actual camera interface
3. Update mock camera tests to match implementation
4. Fix registry state isolation between tests

### Future Enhancements
1. Add orchestration system tests
2. Add display mode integration tests
3. Add hardware camera simulation tests
4. Add network failure simulation tests
5. Add configuration validation tests

## Dependencies

```
pytest>=7.0.0
pytest-mock
psutil
opencv-python
requests
PyYAML
numpy
pygame
urllib3
```

## Test Philosophy

This testing framework follows the same principles as ISKCON-Translate:

1. **Comprehensive Coverage**: Tests cover unit, integration, and performance aspects
2. **Isolated Tests**: Each test runs in isolation with clean state
3. **Realistic Scenarios**: Tests simulate real-world usage patterns
4. **Performance Monitoring**: Built-in performance measurement and validation
5. **Clear Documentation**: Well-documented test cases and expected behaviors
6. **Maintainable Code**: Clean, readable test code with good fixtures

## Contributing

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/sys/`
3. Place performance tests in `tests/perf/`
4. Use appropriate pytest markers
5. Add fixtures to `conftest.py` if reusable
6. Update this README with new test descriptions

## Example Test Run

```bash
$ Scripts\python.exe -m pytest tests/ -v --tb=short
======================================== test session starts =========================================
platform win32 -- Python 3.13.3, pytest-8.3.5, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\Jason\OneDrive\Documents\Workspace\ISKCON-Broadcast
configfile: pytest.ini
plugins: mock-3.14.0
collected 63 items

tests/sys/test_camera_integration.py::TestCameraSystemIntegration::test_multiple_camera_creation_and_management PASSED [ 17%]
tests/sys/test_camera_integration.py::TestCameraSystemIntegration::test_camera_configuration_loading_from_yaml PASSED [ 19%]
tests/unit/test_camera_interface.py::TestCameraInterface::test_camera_interface_is_abstract PASSED [ 33%]
tests/unit/test_camera_registry.py::TestCameraRegistry::test_camera_plugin_decorator PASSED [ 52%]
...

41 failed, 22 passed in 4.72s
```

This testing framework provides a solid foundation for ensuring the reliability and performance of the ISKCON-Broadcast camera plugin system. 