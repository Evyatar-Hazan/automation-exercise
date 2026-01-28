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
├── tests/          # Test cases (to be implemented)
├── pages/          # Page Object Model classes (to be implemented)
├── config/         # Configuration files
│   ├── config.yaml          # General framework settings
│   ├── browsers.yaml        # Browser profiles and capabilities
│   ├── reporting.yaml       # Reporting configuration
│   ├── config_loader.py     # Configuration loader class
│   └── __init__.py
├── utils/          # Helper utilities and common functions
├── reports/        # Test execution reports (auto-generated)
├── logs/           # Test execution logs (auto-generated)
├── requirements.txt
├── pytest.ini
├── validate_config.py       # Configuration validation script
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

### Run All Tests

```bash
pytest
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
- Document complex test scenarios

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

### 🔄 Next Steps

- **STEP 2**: Driver/Browser management layer
- **STEP 3**: Page Object Model implementation
- **STEP 4**: Test utilities and helpers
- **STEP 5**: Test implementation
- **STEP 6**: CI/CD integration

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
