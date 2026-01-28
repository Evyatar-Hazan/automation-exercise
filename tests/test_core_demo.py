"""
Sample test demonstrating the usage of BaseTest and DriverFactory.

This is a demonstration test that shows how to use the core framework components.
Actual test cases should be implemented in separate test files.
"""

import pytest
from core.base_test import BaseTest
from config.config_loader import ConfigLoader  # Only for standalone functions


class TestCoreFramework(BaseTest):
    """
    Sample test class demonstrating the core framework functionality.
    
    All test classes should inherit from BaseTest and use the 'driver' fixture.
    """
    
    def test_driver_initialization(self, driver):
        """
        Test that driver is properly initialized and can navigate to a page.
        
        This test verifies:
        - Driver is created successfully
        - Page navigation works
        - Basic page operations are functional
        """
        # Get base_url from config.yaml (inherited from BaseTest)
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
    
    @pytest.mark.browser("firefox_latest")
    def test_with_firefox(self, driver):
        """
        Test using Firefox browser.
        
        Demonstrates how to use pytest markers to specify browser.
        """
        base_url = self.config_loader.get('base_url')
        
        driver.goto(base_url)
        assert "practice your automation skills" in driver.title()
    
    def test_page_elements(self, driver):
        """
        Test page element interactions.
        
        Demonstrates basic element operations.
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


class TestMultipleBrowsers(BaseTest):
    """
    Demonstrate testing with multiple browsers.
    """
    
    @pytest.mark.browser("chrome_127")
    def test_chrome(self, driver):
        """Test with Chrome browser."""
        base_url = self.config_loader.get('base_url')
        
        driver.goto(base_url)
        assert driver.title()
    
    @pytest.mark.browser("firefox_latest")
    def test_firefox(self, driver):
        """Test with Firefox browser."""
        base_url = self.config_loader.get('base_url')
        
        driver.goto(base_url)
        assert driver.title()


# Standalone test function (not in a class)
def test_standalone():
    """
    Standalone test function demonstrating fixture usage without class.
    
    Note: This test uses ConfigLoader directly since it's not in a class.
    """
    config_loader = ConfigLoader()
    base_url = config_loader.get('base_url')
    
    # Just verify we can load config
    assert base_url is not None
    assert "automationteststore" in base_url


# Parameterized test
@pytest.mark.parametrize("url,expected_title", [
    ("https://automationteststore.com/", "practice your automation skills"),
    ("https://www.iana.org/", "Internet Assigned Numbers Authority"),
])
def test_multiple_sites(url, expected_title):
    """
    Parameterized test demonstrating testing multiple sites.
    
    Args:
        url: URL to test
        expected_title: Expected page title
    """
    # This test uses ConfigLoader to get browser config for multi-site testing
    config_loader = ConfigLoader()
    factory = __import__('core.driver_factory', fromlist=['DriverFactory']).DriverFactory()
    driver = factory.get_driver()
    
    try:
        driver.goto(url)
        assert expected_title in driver.title()
    finally:
        factory.quit_driver()
