"""
Pytest configuration file (conftest.py)

This file contains pytest configuration, fixtures, and hooks
that are shared across all tests in the framework.
"""

import pytest
from pathlib import Path
from loguru import logger

from core.base_test import BaseTest


# Configure pytest markers
def pytest_configure(config):
    """
    Register custom pytest markers.
    
    This allows us to use markers like @pytest.mark.browser("chrome_127")
    without warnings.
    """
    config.addinivalue_line(
        "markers", 
        "browser(name): specify browser profile for the test"
    )
    config.addinivalue_line(
        "markers", 
        "remote: run test on remote Selenium Grid/Moon"
    )


# Make BaseTest fixtures available globally
@pytest.fixture(scope="function")
def driver(request):
    """
    Global driver fixture that can be used by any test.
    
    This fixture delegates to BaseTest.driver to provide
    browser instances to tests.
    
    Usage:
        def test_example(driver):
            driver.goto("https://example.com")
    """
    base_test = BaseTest()
    # Use the BaseTest driver fixture
    yield from base_test.driver(request)


# Session-scoped setup and teardown
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Session-level setup that runs once before all tests.
    
    Use this for:
    - Creating necessary directories
    - Setting up logging
    - Loading global configuration
    """
    logger.info("=" * 80)
    logger.info("Starting Test Session")
    logger.info("=" * 80)
    
    # Ensure required directories exist
    directories = [
        "reports",
        "reports/screenshots",
        "reports/allure-results",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("Test environment setup completed")
    
    yield
    
    # Session teardown
    logger.info("=" * 80)
    logger.info("Test Session Completed")
    logger.info("=" * 80)


# Module-level setup and teardown
@pytest.fixture(scope="module", autouse=True)
def setup_test_module(request):
    """
    Module-level setup that runs once per test module.
    
    Args:
        request: Pytest request object
    """
    module_name = request.module.__name__
    logger.info(f"Starting test module: {module_name}")
    
    yield
    
    logger.info(f"Completed test module: {module_name}")


# Hook to capture test results for reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to make test result available to fixtures.
    
    This hook is essential for the screenshot-on-failure functionality
    in BaseTest.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# Command line options
def pytest_addoption(parser):
    """
    Add custom command line options to pytest.
    
    Example usage:
        pytest --browser=firefox_latest
        pytest --remote
    """
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser profile to use (from browsers.yaml)"
    )
    parser.addoption(
        "--remote",
        action="store_true",
        default=False,
        help="Run tests on remote Selenium Grid/Moon"
    )


@pytest.fixture(scope="session")
def browser_name(request):
    """
    Fixture to get browser name from command line.
    
    Usage:
        pytest --browser=firefox_latest
    """
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def is_remote(request):
    """
    Fixture to check if remote execution is requested.
    
    Usage:
        pytest --remote
    """
    return request.config.getoption("--remote")
