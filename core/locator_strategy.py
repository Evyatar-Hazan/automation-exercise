"""
LocatorUtility Module
Provides multi-locator fallback mechanism for element identification.
"""

from typing import List, Dict, Any, Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from loguru import logger


class LocatorUtility:
    """
    Utility class for handling multiple locators per element with fallback mechanism.
    
    Attempts locators sequentially until one succeeds.
    Logs each attempt for debugging.
    Raises exception only if all locators fail.
    """
    
    def __init__(self, page: Page, timeout: int = 5000):
        """
        Initialize LocatorUtility.
        
        Args:
            page: Playwright Page object
            timeout: Default timeout in milliseconds for element operations
        """
        self.page = page
        self.timeout = timeout
    
    def find_element(
        self,
        locators: List[Dict[str, str]],
        element_name: str = "Element"
    ) -> Locator:
        """
        Find element using multiple locator strategies with fallback.
        
        Args:
            locators: List of locator dictionaries, each with 'type' and 'value'
                     Example: [{'type': 'xpath', 'value': '//button[@id="btn"]'},
                              {'type': 'css', 'value': '#btn'}]
            element_name: Name of element for logging purposes
        
        Returns:
            Playwright Locator object if found
            
        Raises:
            Exception: If all locators fail
            
        Usage:
            locators = [
                {'type': 'xpath', 'value': '//button[@id="submit"]'},
                {'type': 'css', 'value': '#submit'}
            ]
            element = locator_util.find_element(locators, "Submit Button")
        """
        if not locators:
            raise ValueError(f"{element_name}: No locators provided")
        
        errors = []
        
        for idx, locator_dict in enumerate(locators, start=1):
            locator_type = locator_dict.get('type', '').lower()
            locator_value = locator_dict.get('value', '')
            
            if not locator_value:
                logger.warning(f"{element_name} [Locator {idx}]: Empty locator value, skipping")
                continue
            
            try:
                logger.debug(
                    f"{element_name} [Locator {idx}/{len(locators)}]: "
                    f"Attempting {locator_type.upper()}: {locator_value}"
                )
                
                # Get locator based on type
                if locator_type == 'xpath':
                    locator = self.page.locator(f"xpath={locator_value}")
                elif locator_type == 'css':
                    locator = self.page.locator(locator_value)
                elif locator_type == 'id':
                    locator = self.page.locator(f"#{locator_value}")
                elif locator_type == 'text':
                    locator = self.page.get_by_text(locator_value)
                elif locator_type == 'role':
                    locator = self.page.get_by_role(locator_value)
                else:
                    logger.warning(f"{element_name} [Locator {idx}]: Unknown type '{locator_type}', skipping")
                    continue
                
                # Verify element exists and is visible
                locator.wait_for(state='visible', timeout=self.timeout)
                
                logger.info(
                    f"{element_name} [Locator {idx}/{len(locators)}]: ✓ SUCCESS with "
                    f"{locator_type.upper()}: {locator_value}"
                )
                return locator
                
            except PlaywrightTimeoutError as e:
                error_msg = f"{locator_type.upper()}: {locator_value} - Element not visible within timeout"
                logger.debug(f"{element_name} [Locator {idx}/{len(locators)}]: ✗ FAILED - {error_msg}")
                errors.append(error_msg)
            except Exception as e:
                error_msg = f"{locator_type.upper()}: {locator_value} - {str(e)}"
                logger.debug(f"{element_name} [Locator {idx}/{len(locators)}]: ✗ FAILED - {error_msg}")
                errors.append(error_msg)
        
        # All locators failed
        error_summary = f"{element_name}: All {len(locators)} locator(s) failed:\n"
        for idx, error in enumerate(errors, start=1):
            error_summary += f"  {idx}. {error}\n"
        
        logger.error(error_summary.strip())
        raise Exception(error_summary.strip())
    
    def click_element(
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
            locators = [{'type': 'xpath', 'value': '//button'}]
            locator_util.click_element(locators, "Submit Button")
        """
        element = self.find_element(locators, element_name)
        logger.debug(f"{element_name}: Clicking element")
        element.click()
        logger.info(f"{element_name}: ✓ Clicked successfully")
    
    def type_text(
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
            locators = [{'type': 'css', 'value': '#email'}]
            locator_util.type_text(locators, "test@example.com", "Email Field")
        """
        element = self.find_element(locators, element_name)
        logger.debug(f"{element_name}: Typing text: '{text}'")
        
        if clear_first:
            element.clear()
        
        element.fill(text)
        logger.info(f"{element_name}: ✓ Text entered successfully")
    
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
            text = locator_util.get_text([{'type': 'css', 'value': '.message'}])
        """
        element = self.find_element(locators, element_name)
        text = element.inner_text()
        logger.debug(f"{element_name}: Retrieved text: '{text}'")
        return text
    
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
        try:
            element = self.find_element(locators, element_name)
            return element.is_visible()
        except Exception:
            return False
