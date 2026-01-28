# Automation Exercise

A professional Python automation testing framework built with Playwright and pytest for enterprise-grade web application testing.

## Overview

This project provides a scalable and maintainable test automation framework designed for long-term use in production environments. It leverages modern tools and best practices to ensure reliable, fast, and comprehensive test coverage.

## Technology Stack

- **Python** 3.10+ (required)
- **Playwright** - Modern browser automation
- **pytest** - Testing framework
- **pytest-xdist** - Parallel test execution
- **Allure** - Advanced test reporting
- **Loguru** - Enhanced logging capabilities

## Project Structure

```
automation-exercise/
├── core/           # Core framework components
│   ├── driver_factory.py    # Playwright driver factory
│   ├── base_test.py          # Base test class with fixtures
│   ├── README.md             # Core layer documentation
│   └── __init__.py
├── tests/          # Test cases
│   └── test_core_demo.py     # Sample tests
├── pages/          # Page Object Model classes (to be implemented)
├── config/         # Configuration files
│   ├── config.yaml           # General framework settings
│   ├── browsers.yaml         # Browser profiles and capabilities
│   ├── reporting.yaml        # Reporting configuration
│   ├── config_loader.py      # Configuration loader class
│   ├── README.md             # Configuration documentation
│   └── __init__.py
├── utils/          # Helper utilities and common functions
├── reports/        # Test execution reports (auto-generated)
├── logs/           # Test execution logs (auto-generated)
├── conftest.py     # Pytest configuration and global fixtures
├── requirements.txt
├── pytest.ini
├── validate_config.py        # Configuration validation script
└── README.md
```

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd automation-exercise
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 4. Verify Installation

```bash
# Check pytest is installed
pytest --version

# Check Playwright is installed
playwright --version
```

## Running Tests

### Run Sample Demo Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core_demo.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_core_demo.py::TestCoreFramework::test_driver_initialization -v
```

### Run Tests with Specific Browser

```bash
# Using command line option
pytest --browser=firefox_latest

# Using pytest marker in code
pytest -k test_with_firefox
```

### Validate Configuration

```bash
# Verify all configuration files are valid
python validate_config.py
```

### Run Tests in Parallel

```bash
pytest -n auto
```

### Run Tests by Marker

```bash
# Run smoke tests only
pytest -m smoke

# Run regression tests only
pytest -m regression
```

## Configuration

The framework uses YAML-based configuration management for flexibility and maintainability.

### Configuration Files

- **[config/config.yaml](config/config.yaml)** - General framework settings
  - Base URL, timeouts, retries, browser dimensions, logging level
  
- **[config/browsers.yaml](config/browsers.yaml)** - Browser profiles
  - Chrome, Firefox, Edge, WebKit configurations
  - Browser capabilities for local and remote execution
  
- **[config/reporting.yaml](config/reporting.yaml)** - Reporting settings
  - Report types (Allure, HTML, JUnit)
  - Screenshot and video recording options
  - Performance metrics

### Using ConfigLoader

```python
from config.config_loader import ConfigLoader

# Initialize loader
loader = ConfigLoader()

# Get simple values
base_url = loader.get('base_url')  # from config.yaml
timeout = loader.get('default_timeout', default=10)

# Get nested values with dot notation
browser_name = loader.get('browsers.chrome_127.browserName', 'browsers')

# Get specific browser configuration
chrome_config = loader.get_browser_config('chrome_127')

# Get all values from a config file
all_config = loader.get_all('config')
```

### Using Core Layer (DriverFactory + BaseTest)

**Writing Tests:**
```python
from core.base_test import BaseTest
import pytest

class TestExample(BaseTest):
    """All test classes should inherit from BaseTest."""
    
    def test_homepage(self, driver):
        """
        The 'driver' fixture provides an isolated Playwright Page.
        Setup and teardown are handled automatically.
        """
        driver.goto("https://example.com")
        assert "Example" in driver.title()
    
    @pytest.mark.browser("firefox_latest")
    def test_with_firefox(self, driver):
        """Use markers to specify browser profile."""
        driver.goto("https://example.com")
        assert driver.url == "https://example.com/"
```

**Direct DriverFactory Usage (Advanced):**
```python
from core.driver_factory import DriverFactory

# Create factory
factory = DriverFactory(browser_name='chrome_127', remote=False)

# Get driver with retry
driver = factory.get_driver(max_retries=3)

# Use driver
driver.goto("https://example.com")

# Clean up
factory.quit_driver()
```

### Generate Allure Report

```bash
# Run tests with Allure results
pytest --alluredir=reports/allure-results

# Generate and open Allure report
allure serve reports/allure-results
```

## Development Guidelines

- Follow PEP 8 style guidelines
- Write descriptive test names
- Use appropriate pytest markers
- Keep test data separate from test logic
- Leverage YAML configuration for environment-specific settings
- Use ConfigLoader for all configuration access
- Inherit from BaseTest for all test classes
- Use the 'driver' fixture for browser access
- Let fixtures handle setup and teardown
- Write isolated, independent tests for parallel execution
- Document complex test scenarios

## Core Components

### DriverFactory
- Creates Playwright browser instances
- Supports local and remote execution
- Reads browser profiles from `config/browsers.yaml`
- Implements retry mechanism for reliability
- Provides isolated sessions per test
- Comprehensive logging and error handling

### BaseTest
- Base class for all test classes
- Provides `driver` fixture for tests
- Automatic setup and teardown
- Screenshot capture on test failure
- Support for parallel execution (pytest-xdist)
- Browser selection via pytest markers
- Proper resource cleanup

### Key Features
- **Isolation**: Each test gets its own browser instance
- **Configuration-driven**: All settings in YAML files
- **Retry mechanism**: Automatic retry on driver creation failure
- **Screenshot on failure**: Automatic screenshot when tests fail
- **Parallel execution**: Full support for pytest-xdist
- **Logging**: Comprehensive logging with loguru
- **Flexibility**: Easy to extend and customize

## Project Status

### ✅ Completed
- **STEP 0**: Project setup & environment
  - Project structure created
  - Dependencies configured (requirements.txt)
  - pytest.ini with markers and logging
  - Comprehensive .gitignore
  
- **STEP 1**: Configuration Layer
  - YAML-based configuration system
  - ConfigLoader class with caching and error handling
  - Three configuration files: config.yaml, browsers.yaml, reporting.yaml
  - Configuration validation script

- **STEP 2**: Core Layer (Driver Management)
  - DriverFactory class for Playwright browser management
  - BaseTest class with pytest fixtures
  - Support for local and remote execution
  - Retry mechanism for driver creation
  - Screenshot capture on test failure
  - Parallel execution support (pytest-xdist)
  - Isolated browser sessions per test
  - Sample demo tests

### 🔄 Next Steps

- **STEP 3**: Page Object Model implementation
- **STEP 4**: Test utilities and helpers
- **STEP 5**: Real-world test implementation
- **STEP 6**: CI/CD integration
- **STEP 7**: Advanced reporting and analytics

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
