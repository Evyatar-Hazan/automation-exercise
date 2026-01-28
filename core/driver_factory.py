"""
DriverFactory Module
Responsible for creating and managing Playwright browser instances.
Supports both local and remote execution with retry mechanisms.
"""

import time
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from loguru import logger

from config.config_loader import ConfigLoader


class DriverFactory:
    """
    Factory class for creating and managing Playwright browser instances.
    
    This class handles:
    - Local browser execution
    - Remote execution via Selenium Grid / Moon
    - Browser configuration from YAML files
    - Retry mechanism for driver creation
    - Isolated browser sessions per test
    """
    
    def __init__(self, browser_name: Optional[str] = None, remote: bool = False):
        """
        Initialize the DriverFactory.
        
        Args:
            browser_name: Name of browser profile from browsers.yaml 
                         (e.g., 'chrome_127', 'firefox_latest').
                         If None, uses default browser from config.
            remote: Whether to use remote execution (Grid/Moon)
        """
        self.config_loader = ConfigLoader()
        self.browser_name = browser_name or self.config_loader.get_default_browser()
        self.remote = remote
        
        # Load configurations
        self.browser_config = self._load_browser_config()
        self.framework_config = self.config_loader.get_all('config')
        
        # Playwright objects
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        logger.info(
            f"DriverFactory initialized - Browser: {self.browser_name}, "
            f"Remote: {self.remote}"
        )
    
    def _load_browser_config(self) -> Dict[str, Any]:
        """
        Load browser configuration from browsers.yaml.
        
        Returns:
            Dictionary containing browser configuration
            
        Raises:
            ValueError: If browser profile is not found
        """
        try:
            config = self.config_loader.get_browser_config(self.browser_name)
            logger.debug(f"Loaded configuration for browser: {self.browser_name}")
            return config
        except ValueError as e:
            logger.error(f"Failed to load browser config: {e}")
            raise
    
    def _get_browser_type_name(self) -> str:
        """
        Get the Playwright browser type name from config.
        
        Returns:
            Browser type name (chromium, firefox, webkit)
        """
        browser_name = self.browser_config.get('browserName', 'chromium')
        
        # Map browser names to Playwright browser types
        browser_type_map = {
            'chromium': 'chromium',
            'chrome': 'chromium',
            'msedge': 'chromium',
            'edge': 'chromium',
            'firefox': 'firefox',
            'webkit': 'webkit',
            'safari': 'webkit'
        }
        
        playwright_browser = browser_type_map.get(browser_name.lower(), 'chromium')
        logger.debug(f"Mapped {browser_name} to Playwright type: {playwright_browser}")
        return playwright_browser
    
    def _get_launch_options(self) -> Dict[str, Any]:
        """
        Build launch options for browser from configuration.
        
        Returns:
            Dictionary of browser launch options
        """
        options = {}
        
        # Headless mode
        headless = self.browser_config.get(
            'headless',
            self.framework_config.get('headless', False)
        )
        options['headless'] = headless
        
        # Browser arguments
        args = self.browser_config.get('args', [])
        if args:
            options['args'] = args
        
        # Slow motion for debugging (if needed)
        slow_mo = self.framework_config.get('slow_motion', 0)
        if slow_mo > 0:
            options['slow_mo'] = slow_mo
        
        # Channel for chromium-based browsers
        browser_type_name = self._get_browser_type_name()
        if browser_type_name == 'chromium':
            browser_name = self.browser_config.get('browserName', '').lower()
            if browser_name in ['chrome', 'msedge', 'edge']:
                options['channel'] = browser_name if browser_name != 'edge' else 'msedge'
        
        logger.debug(f"Launch options prepared: {options}")
        return options
    
    def _get_context_options(self) -> Dict[str, Any]:
        """
        Build context options from configuration.
        
        Returns:
            Dictionary of browser context options
        """
        options = {}
        
        # Viewport size
        viewport = self.browser_config.get('viewport')
        if viewport:
            options['viewport'] = {
                'width': viewport.get('width', 1920),
                'height': viewport.get('height', 1080)
            }
        else:
            # Default viewport from framework config
            options['viewport'] = {
                'width': self.framework_config.get('browser_width', 1920),
                'height': self.framework_config.get('browser_height', 1080)
            }
        
        # User agent (optional)
        user_agent = self.framework_config.get('user_agent')
        if user_agent:
            options['user_agent'] = user_agent
        
        # Locale
        locale = self.framework_config.get('locale', 'en-US')
        options['locale'] = locale
        
        # Timezone
        timezone = self.framework_config.get('timezone')
        if timezone:
            options['timezone_id'] = timezone
        
        # Accept downloads
        options['accept_downloads'] = True
        
        # Permissions
        permissions = self.framework_config.get('permissions', [])
        if permissions:
            options['permissions'] = permissions
        
        logger.debug(f"Context options prepared: {options}")
        return options
    
    def _create_local_driver(self) -> Page:
        """
        Create a local browser instance.
        
        Returns:
            Playwright Page object
            
        Raises:
            Exception: If driver creation fails
        """
        try:
            logger.info("Creating local browser instance...")
            
            # Start Playwright
            self._playwright = sync_playwright().start()
            
            # Get browser type
            browser_type_name = self._get_browser_type_name()
            browser_type = getattr(self._playwright, browser_type_name)
            
            # Launch browser
            launch_options = self._get_launch_options()
            self._browser = browser_type.launch(**launch_options)
            logger.info(f"Browser launched successfully: {browser_type_name}")
            
            # Create context
            context_options = self._get_context_options()
            self._context = self._browser.new_context(**context_options)
            logger.info("Browser context created")
            
            # Create page
            self._page = self._context.new_page()
            logger.info("Page created successfully")
            
            # Set default timeouts
            self._apply_timeouts()
            
            return self._page
            
        except Exception as e:
            logger.error(f"Failed to create local driver: {e}")
            self._cleanup()
            raise
    
    def _create_remote_driver(self) -> Page:
        """
        Create a remote browser instance via Selenium Grid / Moon.
        
        Returns:
            Playwright Page object
            
        Raises:
            NotImplementedError: Remote execution not yet implemented
        """
        # Note: Playwright's remote browser connection is different from Selenium
        # For now, we'll raise NotImplementedError as this requires additional setup
        grid_url = self.framework_config.get('grid_url')
        logger.warning(
            f"Remote execution requested with grid_url: {grid_url}. "
            "Remote Playwright execution requires additional setup."
        )
        
        # For Playwright remote execution, you would typically use:
        # - Playwright's browserType.connect() method
        # - Or use Selenium Grid with Playwright bindings
        # This is a placeholder for future implementation
        
        raise NotImplementedError(
            "Remote browser execution is not yet implemented. "
            "Please use local execution or implement remote connection logic."
        )
    
    def _apply_timeouts(self) -> None:
        """Apply default timeouts to the page from configuration."""
        if self._page is None:
            return
        
        try:
            # Default timeout for all operations
            default_timeout = self.framework_config.get('default_timeout', 10) * 1000
            self._page.set_default_timeout(default_timeout)
            
            # Navigation timeout
            page_load_timeout = self.framework_config.get('page_load_timeout', 30) * 1000
            self._page.set_default_navigation_timeout(page_load_timeout)
            
            # Element timeout (used for locator operations)
            element_timeout = self.framework_config.get('element_timeout', 5) * 1000
            
            logger.debug(
                f"Timeouts applied - Default: {default_timeout}ms, "
                f"Navigation: {page_load_timeout}ms, "
                f"Element: {element_timeout}ms"
            )
        except Exception as e:
            logger.warning(f"Failed to apply timeouts: {e}")
    
    def get_driver(self, max_retries: Optional[int] = None) -> Page:
        """
        Get a ready-to-use Playwright Page instance with retry mechanism.
        
        Args:
            max_retries: Maximum number of retry attempts. 
                        If None, uses value from config.yaml
        
        Returns:
            Playwright Page object ready for test execution
            
        Raises:
            Exception: If driver creation fails after all retries
        """
        if max_retries is None:
            max_retries = self.framework_config.get('retries', 2)
        
        retry_delay = self.framework_config.get('retry_delay', 1)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"Retry attempt {attempt}/{max_retries} "
                        f"for driver creation..."
                    )
                    time.sleep(retry_delay)
                
                # Create driver based on execution mode
                if self.remote:
                    driver = self._create_remote_driver()
                else:
                    driver = self._create_local_driver()
                
                logger.info(
                    f"✓ Driver created successfully on attempt {attempt + 1}"
                )
                return driver
                
            except Exception as e:
                last_exception = e
                logger.error(
                    f"✗ Driver creation failed on attempt {attempt + 1}: {e}"
                )
                
                # Cleanup any partial resources
                self._cleanup()
                
                # If this was the last attempt, raise the exception
                if attempt == max_retries:
                    logger.error(
                        f"Failed to create driver after {max_retries + 1} attempts"
                    )
                    raise
        
        # Should not reach here, but just in case
        raise last_exception if last_exception else Exception("Driver creation failed")
    
    def _cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self._page:
                self._page.close()
                self._page = None
            if self._context:
                self._context.close()
                self._context = None
            if self._browser:
                self._browser.close()
                self._browser = None
            if self._playwright:
                self._playwright.stop()
                self._playwright = None
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def quit_driver(self) -> None:
        """
        Safely quit the driver and clean up resources.
        
        This method ensures all browser resources are properly closed.
        """
        try:
            logger.info("Quitting driver...")
            self._cleanup()
            logger.info("✓ Driver quit successfully")
        except Exception as e:
            logger.error(f"✗ Error while quitting driver: {e}")
            raise
    
    def get_browser(self) -> Optional[Browser]:
        """
        Get the underlying Browser instance.
        
        Returns:
            Browser instance or None if not initialized
        """
        return self._browser
    
    def get_context(self) -> Optional[BrowserContext]:
        """
        Get the underlying BrowserContext instance.
        
        Returns:
            BrowserContext instance or None if not initialized
        """
        return self._context
    
    def get_page(self) -> Optional[Page]:
        """
        Get the underlying Page instance.
        
        Returns:
            Page instance or None if not initialized
        """
        return self._page
