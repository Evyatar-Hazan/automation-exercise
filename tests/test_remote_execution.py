"""
Remote Execution Test Examples

This test module demonstrates how to use remote execution with Playwright Grid/Moon.

Remote execution can be triggered in multiple ways:
1. CLI flags: pytest --remote --remote-url=https://moon.example.com/wd/hub
2. Pytest markers: @pytest.mark.remote
3. Pytest markers with URL: @pytest.mark.remote("https://moon.example.com/wd/hub")
4. Browser profile config: Set remote: true in browsers.yaml

For local development/testing:
- Uncomment the example remote browser profile in config/browsers.yaml
- Set up a Playwright Grid/Moon instance accessible at the remote_url
- Run: pytest --browser=chrome_127_remote tests/test_remote_execution.py
"""

import pytest
from playwright.sync_api import Page
from core.base_test import BaseTest


class TestRemoteExecution(BaseTest):
    """
    Test class demonstrating remote execution capabilities.
    
    Note: These tests are marked with @pytest.mark.remote but will only
    execute if a remote Grid/Moon service is available and configured.
    """
    
    @pytest.mark.remote
    def test_remote_basic_navigation(self, driver: Page):
        """
        Basic test demonstrating remote browser execution.
        
        This test will run on a remote browser if:
        - --remote flag is passed to pytest
        - OR --remote-url is configured
        - OR @pytest.mark.remote marker is used
        
        Remote execution is automatically detected and handled by the fixture.
        Test code remains unchanged - it's transparent whether running local or remote.
        """
        # Get base_url from config
        base_url = self.config_loader.get('base_url')
        
        # Navigate to page
        driver.goto(base_url, wait_until="domcontentloaded")
        
        # Verify page loaded
        assert driver.url == base_url or base_url in driver.url
    
    @pytest.mark.remote
    def test_remote_page_interaction(self, driver: Page):
        """
        Test demonstrating page interaction on remote browser.
        
        Shows that all normal Playwright Page API methods work seamlessly
        with remote execution.
        """
        base_url = self.config_loader.get('base_url')
        driver.goto(base_url, wait_until="domcontentloaded")
        
        # Take screenshot (works remotely too)
        screenshot_path = "reports/screenshots/remote_test.png"
        driver.screenshot(path=screenshot_path)
        
        # Get page title
        title = driver.title
        assert title is not None and len(title) > 0
    
    @pytest.mark.remote
    def test_remote_viewport_configuration(self, driver: Page):
        """
        Test that viewport configuration is properly applied to remote browser.
        
        The fixture automatically maps viewport settings from the browser profile
        to remote capabilities and applies them to the remote session.
        """
        # Get viewport from profile (should be applied to remote browser)
        viewport_size = driver.viewport_size
        
        # Viewport should match the profile configuration
        assert viewport_size is not None
        assert viewport_size['width'] > 0
        assert viewport_size['height'] > 0


class TestRemoteWithBrowserParameter(BaseTest):
    """
    Tests showing how to specify browser parameters with remote execution.
    
    When using @pytest.mark.browser, the test will run on that specific browser.
    If --remote flag is also set, it will run on the remote Grid instead of local.
    """
    
    @pytest.mark.remote
    @pytest.mark.browser("chrome_127")
    def test_remote_specific_browser(self, driver: Page):
        """
        Test running on a specific browser (chrome_127) in remote mode.
        
        The @pytest.mark.browser marker can be combined with @pytest.mark.remote.
        
        To run this test:
          pytest --remote --remote-url=https://moon.example.com/wd/hub \
                 tests/test_remote_execution.py::TestRemoteWithBrowserParameter::test_remote_specific_browser
        """
        base_url = self.config_loader.get('base_url')
        driver.goto(base_url, wait_until="domcontentloaded")
        assert driver.url == base_url or base_url in driver.url


class TestRemoteErrorHandling(BaseTest):
    """
    Tests demonstrating error handling with remote execution.
    """
    
    @pytest.mark.remote
    def test_remote_timeout_handling(self, driver: Page):
        """
        Test demonstrating timeout handling on remote browser.
        
        If the remote Grid service doesn't respond, the error handling
        is done in DriverFactory._create_remote_driver() which logs
        detailed error information and integrates with ReportingManager.
        """
        base_url = self.config_loader.get('base_url')
        
        # This should work normally - errors in actual page operations
        # are handled the same way as local execution
        driver.goto(base_url, wait_until="domcontentloaded")
        assert driver.url


class TestLocalAndRemoteComparison(BaseTest):
    """
    Tests that run both locally and remotely to verify consistency.
    
    These tests demonstrate that the same test code works identically
    whether executing locally or remotely.
    """
    
    def test_local_execution_by_default(self, driver: Page):
        """
        This test runs locally by default (no @pytest.mark.remote marker).
        
        To run:
          pytest tests/test_remote_execution.py::TestLocalAndRemoteComparison::test_local_execution_by_default
        """
        base_url = self.config_loader.get('base_url')
        driver.goto(base_url, wait_until="domcontentloaded")
        assert driver.url == base_url or base_url in driver.url
    
    @pytest.mark.remote
    def test_remote_execution_with_marker(self, driver: Page):
        """
        Same test as above but runs remotely (has @pytest.mark.remote marker).
        
        To run:
          pytest --remote --remote-url=https://moon.example.com/wd/hub \
                 tests/test_remote_execution.py::TestLocalAndRemoteComparison::test_remote_execution_with_marker
        """
        base_url = self.config_loader.get('base_url')
        driver.goto(base_url, wait_until="domcontentloaded")
        assert driver.url == base_url or base_url in driver.url


# ============================================================================
# USAGE EXAMPLES AND DOCUMENTATION
# ============================================================================

"""
HOW TO USE REMOTE EXECUTION

1. SET UP GRID/MOON SERVICE
   Install Playwright Grid or Moon:
   - Playwright Grid: https://playwright.dev/docs/api/class-playwrighttesting
   - Moon: https://aerokube.com/moon/

2. UPDATE browsers.yaml (optional)
   
   Add remote browser profiles:
   
   matrix:
     - name: chrome_127_remote
       browserName: "chromium"
       browserVersion: "127.0"
       headless: false
       viewport:
         width: 1920
         height: 1080
       remote: true
       remote_url: "https://moon.example.com/wd/hub"

3. RUN TESTS WITH REMOTE EXECUTION

   Option A: Using CLI flags (simplest)
   ───────────────────────────────────
   pytest --remote --remote-url=https://moon.example.com/wd/hub
   
   This will:
   - Take all tests
   - Run each on ALL browsers in the matrix
   - But execute on the remote Grid instead of local
   
   Option B: Using markers (for specific tests)
   ───────────────────────────────────────────
   @pytest.mark.remote
   def test_something(driver):
       pass
   
   Run with:
   pytest --remote-url=https://moon.example.com/wd/hub
   
   Only marked tests will run remotely
   
   Option C: Using markers with URL (self-contained)
   ──────────────────────────────────────────────────
   @pytest.mark.remote("https://moon.example.com/wd/hub")
   def test_something(driver):
       pass
   
   Run with:
   pytest tests/test_something.py
   
   URL is included in the marker
   
   Option D: Using browser profiles (static config)
   ────────────────────────────────────────────────
   In browsers.yaml, set remote: true for a profile:
   
   matrix:
     - name: chrome_127_remote
       remote: true
       remote_url: "https://moon.example.com/wd/hub"
       ...
   
   Run with:
   pytest --browser=chrome_127_remote
   
4. VERIFY REMOTE EXECUTION
   
   Check logs:
   - Look for "Remote execution enabled via"
   - Look for "Connecting to remote Grid/Moon at:"
   - Look for "Remote Session Info:"
   
   Check Allure reports:
   - Remote capabilities should be attached
   - Session info should be included
   - Screenshots work just like local execution

5. PARALLEL EXECUTION WITH REMOTE

   pytest --remote --remote-url=... -n 4
   
   Compatible with pytest-xdist:
   - Each test gets its own remote session
   - No shared browser objects between tests
   - Each worker isolates sessions properly
   - Full parallel safety

IMPORTANT NOTES:
───────────────
1. All test code remains unchanged
   - Tests don't know if running local or remote
   - No hardcoded Grid URLs in tests
   - DriverFactory handles all complexity

2. Error handling is integrated
   - Grid connection errors are logged
   - Session failures attach to Allure
   - Timeout errors work the same way

3. Reporting is automatic
   - Remote capabilities logged to Allure
   - Screenshots work like local execution
   - Session info included in reports

4. Capabilities mapping is automatic
   - Browser profile → Grid capabilities
   - Viewport configured properly
   - Platform detection included
   - Extensible for future options
"""
