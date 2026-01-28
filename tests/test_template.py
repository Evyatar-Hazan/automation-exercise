"""
Test Template

This is a template for creating new test classes following the project structure.

Features:
- Inherits from BaseTest for automatic driver and config management
- Browser matrix automatically applied (runs on all browsers in config/browsers.yaml)
- Organized test class structure
- Uses loguru for logging
- Includes type hints
- Ready for data-driven testing patterns

Usage:
1. Copy this template
2. Replace 'TemplateTest' with your test class name
3. Rename test methods to match your test scenarios
4. Add your test logic
5. Run: pytest tests/test_template.py -v
6. Or with specific browser: pytest tests/test_template.py --browser=chrome_127 -v

Test execution will automatically run on all browsers defined in the matrix.
"""

import pytest
from typing import Dict, Any
from loguru import logger

from core.base_test import BaseTest


class TestTemplate(BaseTest):
    """
    Template test class for new tests.
    
    All test classes should:
    - Inherit from BaseTest
    - Use the 'driver' fixture for browser automation
    - Include descriptive docstrings for each test
    - Use self.config_loader to access configuration
    
    The browser matrix is automatically applied at the fixture level.
    Each test method will run once per browser profile in browsers.yaml.
    
    Example test IDs generated:
        test_template_first[chrome_127]
        test_template_first[firefox_latest]
        ... (one for each browser in the matrix)
    """
    
    def test_template_first(self, driver):
        """
        Template: First test method.
        
        Replace this with your actual test logic.
        
        Args:
            driver: Playwright page fixture for browser automation
        
        The driver fixture automatically handles:
        - Browser initialization based on matrix
        - Screenshot capture on failure
        - Driver cleanup after test
        """
        pass
    
    def test_template_second(self, driver):
        """
        Template: Second test method.
        
        Replace this with your actual test logic.
        
        Args:
            driver: Playwright page fixture for browser automation
        """
        pass
    
    def test_template_with_config(self, driver):
        """
        Template: Test using configuration.
        
        Shows how to access configuration values from config.yaml
        and browsers.yaml.
        
        Args:
            driver: Playwright page fixture for browser automation
        """
        # Access base_url from config.yaml
        base_url = self.config_loader.get('base_url')
        
        # Navigate to the application
        # driver.goto(base_url)
        
        # Your test logic here
        pass
    
    @pytest.mark.parametrize(
        "test_data",
        [
            # Add your test data here
            # Example: {"username": "user1", "password": "pass1", "expected": "success"}
        ],
        ids=lambda d: f"{d.get('id', 'test_case')}"  # Custom test ID
    )
    def test_template_parametrized(self, driver, test_data: Dict[str, Any]):
        """
        Template: Parametrized test for data-driven testing.
        
        Demonstrates how to run the same test with multiple datasets.
        
        Args:
            driver: Playwright page fixture for browser automation
            test_data: Dictionary containing test parameters
        
        Example test IDs generated:
            test_template_parametrized[test_case_1]
            test_template_parametrized[test_case_2]
            ... (one for each item in parametrize)
        """
        pass
    
    def test_template_with_logging(self, driver):
        """
        Template: Test with logging.
        
        Shows how to use loguru for logging within tests.
        
        Args:
            driver: Playwright page fixture for browser automation
        """
        logger.info("Starting test execution")
        
        # Your test logic here
        
        logger.info("Test execution completed")
