"""
BaseTest Module

Base test class for all automation tests.
Tests inherit from BaseTest to get access to fixture support.
"""


class BaseTest:
    """
    Base test class for all automation tests.
    
    Provides:
    - Automatic driver setup via pytest fixtures (conftest.py)
    - Automatic screenshot on failure
    - No setup/teardown logic required in test classes
    
    Usage:
        class TestExample(BaseTest):
            def test_something(self, driver):
                driver.goto("https://example.com")
                assert driver.title() == "Example"
    """
    pass

