"""
AutomationStore Page Object
Page object for automationteststore.com demonstrating multi-locator strategy.
"""

from core.base_page import BasePage


class AutomationStorePage(BasePage):
    """
    Page object for Automation Test Store.
    Demonstrates multi-locator fallback with intentional failures for demo purposes.
    """
    
    # Search input with fallback locators
    # First locator intentionally wrong to demonstrate fallback
    SEARCH_INPUT = [
        {'type': 'xpath', 'value': '//input[@id="WRONG_ID_DEMO"]'},
        {'type': 'css', 'value': '#filter_keyword'}
    ]
    
    # Search button with fallback
    SEARCH_BUTTON = [
        {'type': 'xpath', 'value': '//button[@class="WRONG_CLASS_DEMO"]'},
        {'type': 'css', 'value': '.button-in-search'}
    ]
    
    # Logo element (all working locators for positive test)
    LOGO = [
        {'type': 'css', 'value': '.logo'}
    ]
    
    # Intentionally all wrong locators for failure demo
    NONEXISTENT_ELEMENT = [
        {'type': 'xpath', 'value': '//button[@id="nonexistent_1"]'},
        {'type': 'css', 'value': '#nonexistent_2'},
        {'type': 'css', 'value': '.nonexistent_3'}
    ]
    
    # Account dropdown with fallback
    ACCOUNT_DROPDOWN = [
        {'type': 'xpath', 'value': '//a[@id="WRONG_ACCOUNT"]'},
        {'type': 'css', 'value': 'ul.nav.topcart a[data-id="menu_account"]'}
    ]
    
    # Email field (for page object pattern demo)
    EMAIL_FIELD = [
        {'type': 'xpath', 'value': '//input[@name="email"]'},
        {'type': 'css', 'value': '#loginFrm_loginname'}
    ]
    
    def navigate(self) -> None:
        """Navigate to Automation Store homepage."""
        self.navigate_to("https://automationteststore.com")
    
    def enter_search_text(self, text: str) -> None:
        """
        Enter text in search field using fallback locators.
        First locator fails, second succeeds.
        """
        self.type(self.SEARCH_INPUT, text, "Search Input")
    
    def click_search_button(self) -> None:
        """
        Click search button using fallback locators.
        First locator fails, second succeeds.
        """
        self.click(self.SEARCH_BUTTON, "Search Button")
    
    def is_logo_visible(self) -> bool:
        """Check if logo is visible (working locator)."""
        return self.is_visible(self.LOGO, "Logo")
    
    def click_nonexistent_element(self) -> None:
        """
        Attempt to click nonexistent element (all locators fail).
        Used for demonstrating exception when all locators fail.
        """
        self.click(self.NONEXISTENT_ELEMENT, "Nonexistent Element")
    
    def search_for_product(self, product_name: str) -> None:
        """
        Complete search flow: enter text and click search.
        Demonstrates multi-element interaction with fallback.
        """
        self.enter_search_text(product_name)
        self.click_search_button()
    
    def navigate_to_login(self) -> None:
        """Navigate to login page."""
        self.navigate_to("https://automationteststore.com/index.php?rt=account/login")
    
    def enter_email(self, email: str) -> None:
        """Enter email in login form."""
        self.type(self.EMAIL_FIELD, email, "Email Field")
    
    def get_search_input_value(self) -> str:
        """Get current value from search input."""
        element = self.find_element(self.SEARCH_INPUT, "Search Input")
        return element.input_value()
