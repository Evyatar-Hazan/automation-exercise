"""
BaseTest Module

Base test class for all automation tests.
Tests inherit from BaseTest to get access to fixture support.
"""

from config.config_loader import ConfigLoader


class BaseTest:
    """
    Base test class for all automation tests.
    
    Provides:
    - Automatic driver setup via pytest fixtures (conftest.py)
    - Automatic screenshot on failure
    - Configuration access via config_loader property
    - No setup/teardown logic required in test classes
    
    The browser matrix is automatically applied at the fixture level.
    Tests that request the 'driver' fixture will automatically run
    for each browser in the matrix defined in browsers.yaml.
    
    Usage:
        class TestExample(BaseTest):
            def test_something(self, driver):
                driver.goto("https://example.com")
                base_url = self.config_loader.get('base_url')
                assert driver.title() == "Example"
        
        # This test will run once per browser in the matrix:
        # test_something[chrome_127]
        # test_something[firefox_latest]
        # ... (one for each profile in browsers.yaml matrix)
    """
    
    @property
    def config_loader(self) -> ConfigLoader:
        """Lazy-load ConfigLoader instance for test methods."""
        if not hasattr(self, '_config_loader'):
            self._config_loader = ConfigLoader()
        return self._config_loader

