"""
Example Page Object demonstrating LocatorUtility usage.
"""

from core.base_page import BasePage


class ExamplePage(BasePage):
    """
    Example page demonstrating multi-locator element definitions.
    
    Usage in tests:
        page = ExamplePage(driver)
        page.click_search_button()
    """
    
    # Element locators with fallback strategies
    SEARCH_BUTTON = [
        {'type': 'xpath', 'value': '//button[@id="search-btn"]'},
        {'type': 'css', 'value': '#search-btn'},
        {'type': 'css', 'value': 'button.search-button'}
    ]
    
    EMAIL_INPUT = [
        {'type': 'xpath', 'value': '//input[@name="email"]'},
        {'type': 'css', 'value': 'input[name="email"]'},
        {'type': 'css', 'value': '#email-field'}
    ]
    
    LOGIN_BUTTON = [
        {'type': 'xpath', 'value': '//button[text()="Login"]'},
        {'type': 'css', 'value': 'button#login'},
        {'type': 'text', 'value': 'Login'}
    ]
    
    SUCCESS_MESSAGE = [
        {'type': 'css', 'value': '.alert-success'},
        {'type': 'xpath', 'value': '//div[@class="success-message"]'}
    ]
    
    def click_search_button(self) -> None:
        """Click search button using multi-locator fallback."""
        self.click(self.SEARCH_BUTTON, "Search Button")
    
    def enter_email(self, email: str) -> None:
        """Enter email address using multi-locator fallback."""
        self.type(self.EMAIL_INPUT, email, "Email Input")
    
    def click_login(self) -> None:
        """Click login button using multi-locator fallback."""
        self.click(self.LOGIN_BUTTON, "Login Button")
    
    def get_success_message(self) -> str:
        """Get success message text using multi-locator fallback."""
        return self.get_text(self.SUCCESS_MESSAGE, "Success Message")
    
    def is_login_button_visible(self) -> bool:
        """Check if login button is visible."""
        return self.is_visible(self.LOGIN_BUTTON, "Login Button")
