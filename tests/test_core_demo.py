"""
Sample test demonstrating the usage of BaseTest and the browser matrix.

This is a demonstration test that shows how to use the core framework components
with the dynamic browser matrix feature.

The browser matrix is defined in config/browsers.yaml and is automatically applied
to all tests. Each test function will run once per browser profile in the matrix.

Example test execution with browser matrix:
  test_driver_initialization[chrome_127]
  test_driver_initialization[chrome_latest]
  test_driver_initialization[firefox_latest]
  test_page_elements[chrome_127]
  test_page_elements[chrome_latest]
  test_page_elements[firefox_latest]

To run with a specific browser:
  pytest --browser=chrome_127
"""

import pytest
from core.base_test import BaseTest
from config.config_loader import ConfigLoader


class TestCoreFramework(BaseTest):
    """
    Sample test class demonstrating the core framework functionality.
    
    All test classes should inherit from BaseTest and use the 'driver' fixture.
    
    The browser matrix is automatically applied - each test will run on all
    browsers defined in browsers.yaml:matrix.
    """
    
    def test_driver_initialization(self, driver):
        """
        Test that driver is properly initialized and can navigate to a page.
        
        This test verifies:
        - Driver is created successfully
        - Page navigation works
        - Basic page operations are functional
        
        This test will run automatically on all browsers in the matrix.
        """
        # Get base_url from config.yaml
        base_url = self.config_loader.get('base_url')
        
        # Navigate using URL from config
        driver.goto(base_url)
        
        # Verify page loaded
        assert driver.url == base_url + "/"
        
        # Verify title
        assert "practice your automation skills" in driver.title()
        
        # Verify page content
        heading = driver.locator("h1").first
        assert heading.is_visible()
        assert "Featured" in heading.text_content() or "Latest" in heading.text_content()
    
    def test_page_elements(self, driver):
        """
        Test page element interactions.
        
        Demonstrates basic element operations.
        This test will run on all browsers in the matrix.
        """
        base_url = self.config_loader.get('base_url')
        
        driver.goto(base_url)
        
        # Find and verify paragraph
        paragraph = driver.locator("p")
        assert paragraph.count() > 0
        
        # Check link exists (use first() to avoid strict mode violation)
        link = driver.locator("a").first
        assert link.is_visible()
    
    @pytest.mark.skip(reason="Demo test - intentionally skipped")
    def test_intentionally_fails(self, driver):
        """
        This test is designed to fail to demonstrate screenshot capture.
        
        Uncomment the skip marker to see screenshot-on-failure in action.
        """
        driver.goto("https://example.com")
        
        # This will fail intentionally
        assert driver.title() == "This Will Fail"


# Standalone test function (not in a class)
def test_standalone():
    """
    Standalone test function demonstrating fixture usage without class.
    
    Note: This test does NOT use the driver fixture, so it won't be
    parametrized with the browser matrix. It just demonstrates that
    non-browser tests are unaffected.
    """
    config_loader = ConfigLoader()
    base_url = config_loader.get('base_url')
    
    # Just verify we can load config
    assert base_url is not None
    assert "automationteststore" in base_url


# Note on old patterns:
# 
# The old pattern of using @pytest.mark.browser("firefox_latest") is NO LONGER NEEDED.
# Instead, the browser matrix is automatically applied to all tests that request the
# 'driver' fixture.
#
# Old way (NO LONGER RECOMMENDED):
#   @pytest.mark.browser("firefox_latest")
#   def test_something(self, driver):
#       ...
#
# New way (AUTOMATIC):
#   def test_something(self, driver):
#       # Runs automatically on: chrome_127, chrome_latest, firefox_latest, ...
#       ...
#
# To override the matrix for a single run:
#   pytest --browser=chrome_127 tests/
