"""
BasePage Module
Base page class with integrated LocatorUtility support.
All page objects should inherit from BasePage.
"""

from typing import List, Dict, Optional
from playwright.sync_api import Page
from loguru import logger

from core.locator_strategy import LocatorUtility
from config.config_loader import ConfigLoader


class BasePage:
    """
    Base page class providing common page operations with multi-locator support.
    
    Integrates LocatorUtility for robust element interaction.
    All page objects should inherit from this class.
    """
    
    def __init__(self, page: Page):
        """
        Initialize BasePage.
        
        Args:
            page: Playwright Page object from driver fixture
        """
        self.page = page
        self.config_loader = ConfigLoader()
        
        # Get timeout from config (in seconds), convert to milliseconds
        timeout_seconds = self.config_loader.get('element_timeout', default=5)
        self.timeout = timeout_seconds * 1000
        
        # Initialize locator utility
        self.locator_util = LocatorUtility(page=self.page, timeout=self.timeout)
        
        logger.debug(f"BasePage initialized with timeout: {timeout_seconds}s")
    
    def navigate_to(self, url: str) -> None:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
        """
        logger.info(f"Navigating to: {url}")
        self.page.goto(url)
        logger.debug(f"Navigation completed: {url}")
    
    def click(
        self,
        locators: List[Dict[str, str]],
        element_name: str = "Element"
    ) -> None:
        """
        Click element using multi-locator fallback.
        
        Args:
            locators: List of locator dictionaries
            element_name: Name of element for logging
            
        Usage:
            self.click(
                [{'type': 'xpath', 'value': '//button[@id="submit"]'},
                 {'type': 'css', 'value': '#submit'}],
                "Submit Button"
            )
        """
        self.locator_util.click_element(locators, element_name)
    
    def type(
        self,
        locators: List[Dict[str, str]],
        text: str,
        element_name: str = "Element",
        clear_first: bool = True
    ) -> None:
        """
        Type text into element using multi-locator fallback.
        
        Args:
            locators: List of locator dictionaries
            text: Text to type
            element_name: Name of element for logging
            clear_first: Whether to clear field before typing
            
        Usage:
            self.type(
                [{'type': 'css', 'value': '#email'}],
                "test@example.com",
                "Email Field"
            )
        """
        self.locator_util.type_text(locators, text, element_name, clear_first)
    
    def get_text(
        self,
        locators: List[Dict[str, str]],
        element_name: str = "Element"
    ) -> str:
        """
        Get text from element using multi-locator fallback.
        
        Args:
            locators: List of locator dictionaries
            element_name: Name of element for logging
            
        Returns:
            Text content of element
            
        Usage:
            text = self.get_text(
                [{'type': 'css', 'value': '.message'}],
                "Success Message"
            )
        """
        return self.locator_util.get_text(locators, element_name)
    
    def is_visible(
        self,
        locators: List[Dict[str, str]],
        element_name: str = "Element"
    ) -> bool:
        """
        Check if element is visible using multi-locator fallback.
        
        Args:
            locators: List of locator dictionaries
            element_name: Name of element for logging
            
        Returns:
            True if element is visible, False otherwise
        """
        return self.locator_util.is_visible(locators, element_name)
    
    def find_element(
        self,
        locators: List[Dict[str, str]],
        element_name: str = "Element"
    ):
        """
        Find element using multi-locator fallback.
        Returns Playwright Locator for custom operations.
        
        Args:
            locators: List of locator dictionaries
            element_name: Name of element for logging
            
        Returns:
            Playwright Locator object
        """
        return self.locator_util.find_element(locators, element_name)
    
    def get_title(self) -> str:
        """Get page title."""
        return self.page.title()
    
    def get_url(self) -> str:
        """Get current page URL."""
        return self.page.url
    
    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for page to load completely.
        
        Args:
            timeout: Timeout in milliseconds (None = use default)
        """
        timeout_ms = timeout or self.timeout
        self.page.wait_for_load_state('load', timeout=timeout_ms)
        logger.debug("Page load completed")
