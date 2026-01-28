"""
Pytest configuration for core module.

Provides driver fixture, config fixture, and test failure handling.
All fixtures and hooks for the automation framework.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Page
from loguru import logger

from core.driver_factory import DriverFactory
from config.config_loader import ConfigLoader
from reporting.manager import ReportingManager


_REPORTS_RUN_DIR = None


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


@pytest.fixture(scope="session")
def config() -> dict:
    """Session-scoped fixture providing loaded configuration."""
    config_loader = ConfigLoader()
    configuration = config_loader.load_config("config")
    logger.info("Configuration loaded")
    return configuration


@pytest.fixture(scope="function")
def driver(request) -> Generator[Page, None, None]:
    """Function-scoped fixture providing fresh Playwright Page instance."""
    browser_name = _get_browser_from_marker(request)
    remote = _is_remote_execution(request)
    
    logger.info("=" * 70)
    logger.info(f"Setup: {request.node.name}")
    logger.info(f"Browser: {browser_name}, Remote: {remote}")
    
    factory = None
    page_instance = None
    
    try:
        factory = DriverFactory(browser_name=browser_name, remote=remote)
        page_instance = factory.get_driver()
        logger.info(f"✓ Driver ready: {request.node.name}")
        
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
        _handle_test_failure(request, page_instance)
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
        help="Browser profile to use (from browsers.yaml)"
    )
    parser.addoption(
        "--remote",
        action="store_true",
        default=False,
        help="Run tests on remote Selenium Grid/Moon"
    )


def _get_browser_from_marker(request) -> str:
    """Extract browser name from pytest marker."""
    marker = request.node.get_closest_marker("browser")
    if marker and marker.args:
        return marker.args[0]
    return None


def _is_remote_execution(request) -> bool:
    """Check if test has @pytest.mark.remote marker."""
    return request.node.get_closest_marker("remote") is not None


def _handle_test_failure(request, page_instance: Page) -> None:
    """Capture screenshot on test failure."""
    try:
        if not hasattr(request.node, 'rep_call') or not request.node.rep_call.failed:
            return
        
        _capture_failure_screenshot(request, page_instance)
    except Exception as e:
        logger.warning(f"Could not handle test failure: {e}")


def _capture_failure_screenshot(request, page_instance: Page) -> None:
    """Capture and attach screenshot on failure."""
    if not page_instance:
        logger.warning("Cannot capture screenshot: page instance not available")
        return
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name
        safe_name = "".join(
            c if c.isalnum() or c in ('-', '_') else '_'
            for c in test_name
        )
        
        screenshot_path = _REPORTS_RUN_DIR / f"{safe_name}_{timestamp}.png"
        page_instance.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"✓ Screenshot: {screenshot_path}")
        
        # Attach screenshot using ReportingManager
        if ReportingManager.is_initialized():
            ReportingManager.reporter().attach_screenshot(
                name=f"failure_{test_name}",
                path=str(screenshot_path)
            )
    
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
