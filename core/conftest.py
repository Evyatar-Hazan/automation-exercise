"""
Pytest configuration for core module.

Provides driver fixture, config fixture, and test failure handling.
All fixtures and hooks for the automation framework.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional, Dict, Any, List

import pytest
from playwright.sync_api import Page
from loguru import logger

from core.driver_factory import DriverFactory
from config.config_loader import ConfigLoader
from reporting.manager import ReportingManager


_REPORTS_RUN_DIR = None
_BROWSER_MATRIX = None


def pytest_configure(config):
    """Register markers and create timestamped reports directory."""
    global _REPORTS_RUN_DIR
    
    config.addinivalue_line(
        "markers", 
        "browser(name): specify browser profile for the test"
    )
    config.addinivalue_line(
        "markers", 
        "remote: run test on remote Selenium Grid/Moon"
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_base = Path(__file__).parent.parent / "reports"
    _REPORTS_RUN_DIR = reports_base / f"{timestamp}"
    _REPORTS_RUN_DIR.mkdir(parents=True, exist_ok=True)
    
    allure_dir = _REPORTS_RUN_DIR / "allure-results"
    allure_dir.mkdir(parents=True, exist_ok=True)
    
    config.option.allure_report_dir = str(allure_dir)
    
    # Initialize ReportingManager
    try:
        config_loader = ConfigLoader()
        configuration = config_loader.load_config("config")
        reporter_type = configuration.get("reporter", "allure")
        ReportingManager.init(reporter_type)
    except Exception as e:
        logger.warning(f"Failed to initialize ReportingManager: {e}. Falling back to Allure.")
        ReportingManager.init("allure")
    
    logger.info(f"Reports directory: {_REPORTS_RUN_DIR}")


def pytest_generate_tests(metafunc):
    """
    Dynamically parametrize tests with browser matrix at collection time.
    
    This hook is called during test collection and allows us to:
    - Load the browser matrix from browsers.yaml
    - Parametrize any test that uses the 'browser_profile' fixture
    - Generate test variations like: test_login[chrome_127], test_login[firefox_latest]
    
    The parametrization happens at collection time (before test execution),
    enabling proper parallel execution with pytest-xdist.
    """
    global _BROWSER_MATRIX
    
    # Only parametrize if the test function uses the 'browser_profile' fixture
    if 'browser_profile' not in metafunc.fixturenames:
        return
    
    # Load browser matrix once and cache it
    if _BROWSER_MATRIX is None:
        try:
            config_loader = ConfigLoader()
            _BROWSER_MATRIX = config_loader.get_browser_matrix()
            logger.info(
                f"Loaded browser matrix with {len(_BROWSER_MATRIX)} profiles: "
                f"{[p.get('name', 'unknown') for p in _BROWSER_MATRIX]}"
            )
        except Exception as e:
            logger.error(f"Failed to load browser matrix: {e}")
            raise
    
    # Check for CLI override
    browser_override = metafunc.config.getoption("--browser", default=None)
    
    if browser_override:
        # Filter matrix to only the specified browser
        filtered_matrix = [
            p for p in _BROWSER_MATRIX
            if p.get('name') == browser_override
        ]
        
        if not filtered_matrix:
            available = ", ".join(p.get('name', 'unknown') for p in _BROWSER_MATRIX)
            raise ValueError(
                f"Browser '{browser_override}' not found in matrix. "
                f"Available: {available}"
            )
        
        matrix_to_use = filtered_matrix
        logger.info(f"Using CLI override: --browser={browser_override}")
    else:
        matrix_to_use = _BROWSER_MATRIX
    
    # Parametrize the test with each browser profile in the matrix
    # The parameter IDs will be the browser profile names (e.g., 'chrome_127', 'firefox_latest')
    profile_ids = [p.get('name', f"profile_{i}") for i, p in enumerate(matrix_to_use)]
    
    metafunc.parametrize(
        'browser_profile',
        matrix_to_use,
        ids=profile_ids,
        scope='function'
    )
    
    logger.debug(
        f"Parametrized {metafunc.function.__name__} with "
        f"{len(matrix_to_use)} browser profiles"
    )


@pytest.fixture(scope="session")
def config() -> dict:
    """Session-scoped fixture providing loaded configuration."""
    config_loader = ConfigLoader()
    configuration = config_loader.load_config("config")
    logger.info("Configuration loaded")
    return configuration


@pytest.fixture(scope="function")
def browser_profile(request) -> Dict[str, Any]:
    """
    Function-scoped fixture providing the current browser profile dictionary.
    
    This fixture is injected by pytest_generate_tests during collection time.
    Each test receives one browser profile from the matrix.
    
    Note: This fixture is automatically parametrized by pytest_generate_tests,
    so you don't need to use @pytest.mark.parametrize manually.
    """
    # The parametrize in pytest_generate_tests will pass the profile as a fixture value
    if hasattr(request, 'param'):
        return request.param
    
    # Fallback: if not parametrized, return a minimal default profile
    # This should not normally happen if pytest_generate_tests is working correctly
    logger.warning("browser_profile not parametrized, using default")
    return {
        'name': 'default',
        'browserName': 'chromium',
        'browserVersion': 'latest',
        'headless': False
    }


@pytest.fixture(scope="function")
def driver(browser_profile: Dict[str, Any]) -> Generator[Page, None, None]:
    """
    Function-scoped fixture providing fresh Playwright Page instance.
    
    This fixture:
    - Receives a browser_profile from pytest_generate_tests parametrization
    - Creates a new isolated browser session for each test
    - Handles cleanup and failure screenshot capture
    - Ensures no browser state is shared between tests
    """
    logger.info("=" * 70)
    logger.info(f"Setup: {browser_profile.get('name', 'unknown')}")
    
    factory = None
    page_instance = None
    
    try:
        # Create driver with the current browser profile
        factory = DriverFactory(browser_profile=browser_profile, remote=False)
        page_instance = factory.get_driver()
        logger.info(f"✓ Driver ready: {browser_profile.get('name', 'unknown')}")
        
        yield page_instance
        
    except Exception as e:
        logger.error(f"✗ Driver setup failed: {e}")
        if factory:
            try:
                factory.quit_driver()
            except Exception:
                pass
        raise
    
    finally:
        _handle_test_failure(browser_profile, page_instance)
        if factory:
            try:
                factory.quit_driver()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
        logger.info("=" * 70)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Session-level setup and teardown."""
    logger.info("=" * 80)
    logger.info("Test Session Started")
    logger.info("=" * 80)
    
    for directory in ["reports", "reports/screenshots", "reports/allure-results", "logs"]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    yield
    
    logger.info("=" * 80)
    logger.info("Test Session Completed")
    logger.info("=" * 80)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook to capture test execution result."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Browser profile to use (from browsers.yaml matrix). "
             "If not specified, all matrix profiles are used."
    )
    parser.addoption(
        "--remote",
        action="store_true",
        default=False,
        help="Run tests on remote Selenium Grid/Moon (not yet implemented)"
    )


def _handle_test_failure(browser_profile: Dict[str, Any], page_instance: Page) -> None:
    """Capture screenshot on test failure."""
    try:
        # This function is called in the finally block, but we need request context
        # The actual failure check happens in _capture_failure_screenshot
        # For now, we'll try to capture based on page state
        if page_instance:
            _capture_failure_screenshot(browser_profile, page_instance)
    except Exception as e:
        logger.warning(f"Could not handle test failure: {e}")


def _capture_failure_screenshot(
    browser_profile: Dict[str, Any],
    page_instance: Page
) -> None:
    """
    Capture and attach screenshot on failure.
    
    Note: This is called opportunistically in the finally block.
    A more robust approach would integrate with pytest hooks to check actual failure status.
    """
    if not page_instance:
        logger.warning("Cannot capture screenshot: page instance not available")
        return
    
    # In a production setup, you would check request.node.rep_call.failed here
    # For now, this is a placeholder that can be integrated with proper failure detection

