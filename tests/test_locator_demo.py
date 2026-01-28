"""
Test demonstrating LocatorUtility multi-locator fallback mechanism.

Demonstrates proper Page Object pattern:
- Locators defined in Page Object (not in tests)
- Tests only call page methods
- Framework handles fallback automatically
- Logs show which locator succeeded
"""

import pytest
from core.base_test import BaseTest
from pages.automation_store_page import AutomationStorePage


class TestLocatorFallbackDemo(BaseTest):
    """
    Test suite demonstrating multi-locator fallback functionality.
    
    All locators are in AutomationStorePage - tests remain clean.
    
    Run with: pytest tests/test_locator_demo.py -v
    View logs to see fallback mechanism in action
    """
    
    def test_fallback_with_intentional_bad_locator(self, driver):
        """
        Demonstrates fallback from bad locator to good locator.
        
        Test flow:
        1. Navigate to test site
        2. Enter text in search field (page has 2 locators defined)
        3. First locator (intentionally wrong in page) fails
        4. Second locator succeeds
        5. Test completes successfully without knowing which locator worked
        
        Expected: Test passes, logs show locator fallback
        """
        page = AutomationStorePage(driver)
        page.navigate()
        
        # Test just calls page method - locators are in page object
        page.enter_search_text("Hair Care")
        
        # Verify text was entered
        assert page.get_search_input_value() == "Hair Care"
    
    def test_multiple_elements_with_fallback(self, driver):
        """
        Test multiple elements each using multi-locator strategy.
        
        Demonstrates:
        - Multiple elements on same page
        - Each element has fallback locators (defined in page)
        - Framework logs which locator succeeded for each element
        - Test code remains clean
        """
        page = AutomationStorePage(driver)
        page.navigate()
        
        # Test just calls page methods - all locator logic is hidden
        page.search_for_product("Skincare")
        
        # Verify navigation occurred
        assert "keyword=Skincare" in driver.url.lower() or "skincare" in driver.url.lower()
    
    def test_all_locators_fail_raises_exception(self, driver):
        """
        Test that exception is raised when ALL locators fail.
        
        Demonstrates:
        - All locators in page are invalid (intentionally)
        - Framework tries each one
        - After all attempts fail, exception is raised
        - Screenshot is captured on failure
        """
        page = AutomationStorePage(driver)
        page.navigate()
        
        # Expect exception when all locators fail
        # Locators are in page object, not here
        with pytest.raises(Exception) as exc_info:
            page.click_nonexistent_element()
        
        # Verify exception contains information about all failed attempts
        error_message = str(exc_info.value)
        assert "All" in error_message and "failed" in error_message
    
    def test_single_working_locator(self, driver):
        """
        Test with only one locator that works.
        
        Demonstrates:
        - Single locator in page (no fallback needed)
        - Standard successful case
        - Clean test code
        """
        page = AutomationStorePage(driver)
        page.navigate()
        
        # Test just checks visibility - locator is in page
        assert page.is_logo_visible()
    
    def test_page_object_pattern_clean_separation(self, driver):
        """
        Test demonstrating clean Page Object pattern.
        
        Shows:
        - Complete separation: tests have ZERO locator definitions
        - Page objects encapsulate ALL locator logic
        - Test code is simple, readable, and maintainable
        - Easy to update locators without touching tests
        """
        page = AutomationStorePage(driver)
        page.navigate_to_login()
        
        # Test code is clean - just calls methods
        # No locators visible here
        page.enter_email("test@example.com")
        
        # Verify interaction succeeded
        email_element = page.find_element(page.EMAIL_FIELD, "Email Field")
        assert email_element.input_value() == "test@example.com"
    
    def test_complete_user_flow(self, driver):
        """
        Test complete user flow using only page methods.
        
        Real-world example showing how tests should look:
        - No locators in test code
        - Clear, readable actions
        - All complexity hidden in page objects
        """
        page = AutomationStorePage(driver)
        
        # Navigate to site
        page.navigate()
        
        # Perform search
        page.enter_search_text("Makeup")
        page.click_search_button()
        
        # Verify results
        assert "keyword=Makeup" in driver.url.lower() or "makeup" in driver.url.lower()
