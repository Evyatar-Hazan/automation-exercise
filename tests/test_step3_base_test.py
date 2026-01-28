"""
Example test demonstrating STEP 3: BaseTest + pytest fixtures.

Clean test pattern:
- Inherit from BaseTest
- Request driver fixture
- No setup/teardown logic
- No config loading
- No driver creation
"""

from core.base_test import BaseTest
from pages.automation_store_page import AutomationStorePage


class TestCleanPattern(BaseTest):
    """Tests using clean fixture-driven pattern."""
    
    def test_search_with_fallback(self, driver):
        """Test with automatic driver setup and teardown."""
        page = AutomationStorePage(driver)
        page.navigate()
        page.enter_search_text("Hair Care")
        
        assert page.get_search_input_value() == "Hair Care"
    
    def test_complete_search_flow(self, driver):
        """Test complete user flow."""
        page = AutomationStorePage(driver)
        page.navigate()
        page.search_for_product("Skincare")
        
        assert "keyword=Skincare" in driver.url.lower() or "skincare" in driver.url.lower()
    
    def test_logo_visibility(self, driver):
        """Test element visibility check."""
        page = AutomationStorePage(driver)
        page.navigate()
        
        assert page.is_logo_visible()
    
    def test_multi_element_interaction(self, driver):
        """Test interaction with multiple elements."""
        page = AutomationStorePage(driver)
        page.navigate()
        
        page.enter_search_text("Makeup")
        assert page.get_search_input_value() == "Makeup"
        
        page.click_search_button()
        assert "keyword=Makeup" in driver.url.lower() or "makeup" in driver.url.lower()
