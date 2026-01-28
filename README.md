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
├── utils/          # Helper utilities and common functions
├── reports/        # Test execution reports (auto-generated)
├── logs/           # Test execution logs (auto-generated)
├── requirements.txt
├── pytest.ini
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
- Document complex test scenarios

## Next Steps

- Implement page object models
- Add test cases
- Configure test data management
- Set up CI/CD integration
- Implement custom utilities and helpers

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
