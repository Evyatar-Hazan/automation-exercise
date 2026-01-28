"""
BaseTest Module
Provides base test class with setup/teardown functionality and fixtures.
All test classes should inherit from BaseTest.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytest
from playwright.sync_api import Page
from loguru import logger

from core.driver_factory import DriverFactory
from config.config_loader import ConfigLoader


class BaseTest:
    """
    Base test class for all automation tests.
    
    Provides:
    - Automatic driver setup and teardown via pytest fixtures
    - Screenshot capture on test failure
    - Proper resource cleanup
    - Isolated browser sessions per test
    - Support for parallel execution with pytest-xdist
    - Configuration-driven timeouts and settings
    
    Usage:
        class TestExample(BaseTest):
            def test_something(self, driver):
                driver.goto("https://example.com")
                assert driver.title() == "Example"
    """
    
    # Class-level configuration
    config_loader = ConfigLoader()
    
    @pytest.fixture(scope="function", autouse=False)
    def driver(self, request) -> Page:
        """
        Pytest fixture that provides an isolated Playwright Page instance.
        
        This fixture:
        - Creates a new driver instance before each test
        - Applies default timeouts from configuration
        - Ensures proper cleanup after test execution
        - Captures screenshots on test failure
        - Supports parallel execution (each test gets its own driver)
        
        Args:
            request: Pytest request object for accessing test information
            
        Yields:
            Playwright Page instance ready for test execution
            
        Example:
            def test_example(self, driver):
                driver.goto("https://example.com")
        """
        # Get browser name from pytest marker or use default
        browser_name = self._get_browser_name(request)
        remote = self._is_remote_execution(request)
        
        logger.info("=" * 70)
        logger.info(f"Setting up test: {request.node.name}")
        logger.info(f"Browser: {browser_name}, Remote: {remote}")
        logger.info("=" * 70)
        
        # Create driver factory
        factory = None
        driver_instance = None
        
        try:
            # Initialize factory and create driver
            factory = DriverFactory(browser_name=browser_name, remote=remote)
            driver_instance = factory.get_driver()
            
            logger.info(f"✓ Driver setup completed for test: {request.node.name}")
            
            # Store factory in request for cleanup
            request.node._driver_factory = factory
            request.node._driver_instance = driver_instance
            
            # Yield driver to test
            yield driver_instance
            
        except Exception as e:
            logger.error(f"✗ Driver setup failed: {e}")
            # Attempt cleanup even if setup failed
            if factory:
                try:
                    factory.quit_driver()
                except Exception as cleanup_error:
                    logger.error(f"Cleanup after setup failure failed: {cleanup_error}")
            raise
        
        finally:
            # Teardown logic
            self._teardown_driver(request, factory, driver_instance)
    
    def _get_browser_name(self, request) -> Optional[str]:
        """
        Extract browser name from pytest marker or return None for default.
        
        Args:
            request: Pytest request object
            
        Returns:
            Browser name or None
            
        Example:
            @pytest.mark.browser("firefox_latest")
            def test_example(self, driver):
                pass
        """
        marker = request.node.get_closest_marker("browser")
        if marker:
            return marker.args[0] if marker.args else None
        return None
    
    def _is_remote_execution(self, request) -> bool:
        """
        Check if test should run on remote grid.
        
        Args:
            request: Pytest request object
            
        Returns:
            True if remote execution is requested
            
        Example:
            @pytest.mark.remote
            def test_example(self, driver):
                pass
        """
        return request.node.get_closest_marker("remote") is not None
    
    def _teardown_driver(
        self,
        request,
        factory: Optional[DriverFactory],
        driver_instance: Optional[Page]
    ) -> None:
        """
        Teardown driver after test execution.
        
        Args:
            request: Pytest request object
            factory: DriverFactory instance
            driver_instance: Page instance
        """
        logger.info("=" * 70)
        logger.info(f"Tearing down test: {request.node.name}")
        
        try:
            # Check if test failed and capture screenshot
            if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
                self._capture_screenshot_on_failure(
                    request,
                    driver_instance
                )
        except Exception as e:
            logger.warning(f"Could not check test status for screenshot: {e}")
        
        # Quit driver
        if factory:
            try:
                factory.quit_driver()
                logger.info(f"✓ Driver teardown completed for test: {request.node.name}")
            except Exception as e:
                logger.error(f"✗ Error during driver teardown: {e}")
        
        logger.info("=" * 70)
    
    def _capture_screenshot_on_failure(
        self,
        request,
        driver_instance: Optional[Page]
    ) -> None:
        """
        Capture screenshot when test fails.
        
        Args:
            request: Pytest request object
            driver_instance: Page instance
        """
        if not driver_instance:
            logger.warning("Cannot capture screenshot: driver not available")
            return
        
        # Check if screenshots are enabled
        config = self.config_loader.get_all('config')
        if not config.get('screenshot_on_failure', True):
            logger.debug("Screenshot on failure is disabled in config")
            return
        
        try:
            # Create screenshots directory
            screenshot_dir = Path(config.get('screenshot_path', 'reports/screenshots'))
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate screenshot filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = request.node.name
            # Sanitize test name for filename
            safe_test_name = "".join(
                c if c.isalnum() or c in ('-', '_') else '_' 
                for c in test_name
            )
            screenshot_path = screenshot_dir / f"{safe_test_name}_{timestamp}.png"
            
            # Capture screenshot
            driver_instance.screenshot(path=str(screenshot_path), full_page=True)
            
            logger.info(f"✓ Screenshot captured: {screenshot_path}")
            
            # Attach to Allure report if available
            try:
                import allure
                with open(screenshot_path, 'rb') as image_file:
                    allure.attach(
                        image_file.read(),
                        name=f"failure_{test_name}",
                        attachment_type=allure.attachment_type.PNG
                    )
                logger.debug("Screenshot attached to Allure report")
            except ImportError:
                logger.debug("Allure not available, screenshot saved to file only")
            
        except Exception as e:
            logger.error(f"✗ Failed to capture screenshot: {e}")
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """
        Pytest hook to capture test execution status.
        
        This hook allows us to check if a test failed so we can
        capture screenshots in the teardown phase.
        """
        # Execute all other hooks to obtain the report object
        outcome = yield
        rep = outcome.get_result()
        
        # Store test result on the test item for access in fixtures
        setattr(item, f"rep_{rep.when}", rep)


# Pytest configuration hook for BaseTest
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to make test result available to fixtures.
    
    This is required for the screenshot-on-failure functionality.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


class BaseTestClass(BaseTest):
    """
    Alternative base class using pytest's class-based approach.
    
    This class is useful when you want to organize tests in classes
    and share setup logic across multiple test methods.
    
    Usage:
        class TestSuite(BaseTestClass):
            def test_example_1(self, driver):
                driver.goto("https://example.com")
                
            def test_example_2(self, driver):
                driver.goto("https://example.com")
    """
    
    # Inherit all functionality from BaseTest
    pass


def get_driver_fixture():
    """
    Returns the driver fixture for use in tests.
    
    This function can be used to access the driver fixture
    programmatically if needed.
    
    Returns:
        The driver fixture function
    """
    return BaseTest().driver
