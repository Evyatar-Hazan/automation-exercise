"""
DriverFactory Module
Responsible for creating and managing Playwright browser instances.
Supports both local and remote execution with retry mechanisms.
"""

import time
import json
import urllib.parse
from typing import Optional, Dict, Any, Union
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from loguru import logger

from config.config_loader import ConfigLoader


class RemoteCapabilitiesMapper:
    """Maps Playwright browser profiles to Playwright remote capabilities."""
    
    @staticmethod
    def map_to_remote_capabilities(browser_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map browser profile to Playwright remote capabilities for Grid/Moon.
        
        Playwright's remote connection expects capabilities in a specific format.
        
        Args:
            browser_profile: Browser profile dictionary from YAML
            
        Returns:
            Dictionary of remote capabilities
        """
        capabilities = {
            "browserName": RemoteCapabilitiesMapper._get_browser_name(
                browser_profile.get('browserName', 'chromium')
            ),
        }
        
        # Add browser version if specified
        browser_version = browser_profile.get('browserVersion')
        if browser_version and browser_version.lower() != 'latest':
            capabilities["browserVersion"] = str(browser_version)
        
        # Add viewport configuration
        viewport = browser_profile.get('viewport')
        if viewport:
            capabilities["viewport"] = {
                "width": viewport.get('width', 1920),
                "height": viewport.get('height', 1080)
            }
        
        # Add headless flag if explicitly set
        headless = browser_profile.get('headless')
        if headless is not None:
            capabilities["headless"] = bool(headless)
        
        # Platform name for Grid compatibility
        platform_name = browser_profile.get('platformName')
        if platform_name:
            capabilities["platformName"] = platform_name
        
        # Add any Moon/Grid-specific options
        remote_options = browser_profile.get('remote_options', {})
        if remote_options:
            capabilities.update(remote_options)
        
        logger.debug(f"Mapped remote capabilities: {json.dumps(capabilities, indent=2)}")
        return capabilities
    
    @staticmethod
    def _get_browser_name(browser_name: str) -> str:
        """
        Normalize browser name for remote capabilities.
        
        Args:
            browser_name: Browser name from profile
            
        Returns:
            Standard browser name for Grid (chromium, firefox, webkit)
        """
        name_map = {
            'chromium': 'chromium',
            'chrome': 'chromium',
            'msedge': 'chromium',
            'edge': 'chromium',
            'firefox': 'firefox',
            'webkit': 'webkit',
            'safari': 'webkit'
        }
        return name_map.get(browser_name.lower(), 'chromium')


class DriverFactory:
    """
    Factory class for creating and managing Playwright browser instances.
    
    This class handles:
    - Local browser execution
    - Remote execution via Playwright Grid / Moon (W3C WebDriver compliant)
    - Browser configuration from YAML files or profile dictionaries
    - Retry mechanism for driver creation
    - Isolated browser sessions per test
    """
    
    def __init__(
        self,
        browser_profile: Optional[Union[str, Dict[str, Any]]] = None,
        remote: Optional[bool] = None,
        remote_url: Optional[str] = None
    ):
        """
        Initialize the DriverFactory.
        
        Args:
            browser_profile: Either:
                - Browser profile name (string) from browsers.yaml 
                  (e.g., 'chrome_127', 'firefox_latest')
                - Browser profile dictionary with keys:
                  - name: Profile name
                  - browserName: Type (chromium, firefox, webkit)
                  - browserVersion: Version string
                  - headless: Boolean
                  - viewport: Dict with width/height
                  - remote: Boolean (optional override)
                  - remote_url: String (optional override)
                  - Other Playwright options
                If None, uses default browser from config.
            remote: Override remote flag from profile or config
            remote_url: Override remote URL from profile or config
        """
        self.config_loader = ConfigLoader()
        
        # Load framework config
        self.framework_config = self.config_loader.get_all('config')
        
        # Handle browser_profile parameter
        if browser_profile is None:
            # Use default browser from config
            default_browser = self.config_loader.get_default_browser()
            self.browser_profile = self._load_browser_profile_by_name(default_browser)
            self.profile_name = default_browser
        elif isinstance(browser_profile, str):
            # Load profile by name from browsers.yaml
            self.browser_profile = self._load_browser_profile_by_name(browser_profile)
            self.profile_name = browser_profile
        elif isinstance(browser_profile, dict):
            # Use provided dictionary as profile
            self.browser_profile = browser_profile.copy()
            self.profile_name = browser_profile.get('name', 'custom_profile')
        else:
            raise TypeError(
                f"browser_profile must be None, str, or dict, got {type(browser_profile)}"
            )
        
        # Determine remote execution mode
        # Priority: CLI parameter > browser_profile > config
        if remote is not None:
            self.remote = remote
            self.remote_url = remote_url
        else:
            # Check if profile specifies remote
            self.remote = self.browser_profile.get('remote', False)
            self.remote_url = remote_url or self.browser_profile.get('remote_url')
        
        # Validate remote configuration
        if self.remote and not self.remote_url:
            # Try to get from framework config as fallback
            self.remote_url = self.framework_config.get('remote_url') or self.framework_config.get('grid_url')
            if not self.remote_url:
                logger.warning(
                    "Remote execution requested but no remote_url provided. "
                    "Will attempt to use Playwright's default Grid URL."
                )
        
        # Playwright objects
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        logger.info(
            f"DriverFactory initialized - Profile: {self.profile_name}, "
            f"Browser: {self.browser_profile.get('browserName', 'unknown')}, "
            f"Remote: {self.remote}, Remote URL: {self.remote_url or 'N/A'}"
        )
    
    def _load_browser_profile_by_name(self, browser_name: str) -> Dict[str, Any]:
        """
        Load browser profile from browsers.yaml by name.
        
        Args:
            browser_name: Name of the browser profile
            
        Returns:
            Browser profile dictionary
            
        Raises:
            ValueError: If browser profile is not found
        """
        try:
            config = self.config_loader.get_browser_config(browser_name)
            profile = {"name": browser_name}
            profile.update(config)
            logger.debug(f"Loaded browser profile: {browser_name}")
            return profile
        except ValueError as e:
            logger.error(f"Failed to load browser profile: {e}")
            raise
    
    def _get_browser_type_name(self) -> str:
        """
        Get the Playwright browser type name from profile.
        
        Returns:
            Browser type name (chromium, firefox, webkit)
        """
        browser_name = self.browser_profile.get('browserName', 'chromium')
        
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
        Build launch options for browser from profile.
        
        Returns:
            Dictionary of browser launch options
        """
        options = {}
        
        # Headless mode
        headless = self.browser_profile.get(
            'headless',
            self.framework_config.get('headless', False)
        )
        options['headless'] = headless
        
        # Browser arguments
        args = self.browser_profile.get('args', [])
        if args:
            options['args'] = args
        
        # Slow motion for debugging (if needed)
        slow_mo = self.framework_config.get('slow_motion', 0)
        if slow_mo > 0:
            options['slow_mo'] = slow_mo
        
        # Channel for chromium-based browsers
        browser_type_name = self._get_browser_type_name()
        if browser_type_name == 'chromium':
            browser_name = self.browser_profile.get('browserName', '').lower()
            if browser_name in ['chrome', 'msedge', 'edge']:
                options['channel'] = browser_name if browser_name != 'edge' else 'msedge'
        
        logger.debug(f"Launch options prepared: {options}")
        return options
    
    def _get_context_options(self) -> Dict[str, Any]:
        """
        Build context options from profile.
        
        Returns:
            Dictionary of browser context options
        """
        options = {}
        
        # Viewport size
        viewport = self.browser_profile.get('viewport')
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
        Create a remote browser instance via Playwright Grid / Moon.
        
        Uses Playwright's browserType.connect() to establish a websocket connection
        to the Moon/Grid instance, passing capabilities via the URL query parameters.
        
        Returns:
            Playwright Page object connected to remote browser
            
        Raises:
            ValueError: If remote URL is not configured
            Exception: If remote connection fails
        """
        try:
            if not self.remote_url:
                raise ValueError(
                    "Remote execution requested but remote_url not configured. "
                    "Set remote_url in browser profile or config."
                )
            
            logger.info(f"Connecting to remote Grid/Moon at: {self.remote_url}")
            
            # Start Playwright
            self._playwright = sync_playwright().start()
            
            # Get browser type (chromium, firefox, webkit)
            browser_type_name = self._get_browser_type_name()
            browser_type = getattr(self._playwright, browser_type_name)
            
            # Map profile to remote capabilities
            capabilities = RemoteCapabilitiesMapper.map_to_remote_capabilities(
                self.browser_profile
            )
            
            # Encode capabilities for URL
            caps_json = json.dumps(capabilities)
            encoded_caps = urllib.parse.quote(caps_json)
            logger.debug(f"Encoded capabilities: {encoded_caps}")
            
            # Construct Moon WebSocket Endpoint
            # Format: ws://MOON_HOST/playwright/{browser}?capabilities={json}
            parsed_url = urllib.parse.urlparse(self.remote_url)
            scheme = 'wss' if parsed_url.scheme == 'https' else 'ws'
            host = parsed_url.netloc
            
            ws_endpoint = f"{scheme}://{host}/playwright/{browser_type_name}?capabilities={encoded_caps}"
            logger.info(f"Connecting to Moon endpoint: {ws_endpoint}")
            
            # Connect to Moon
            self._browser = browser_type.connect(ws_endpoint)
            logger.info("Successfully connected to remote browser")
            
            # Create context
            # Note: Viewport and other options are handled by Moon via capabilities,
            # but we pass context options for client-side behaviors like locale/timezone
            context_options = self._get_context_options()
            self._context = self._browser.new_context(**context_options)
            logger.info("Remote browser context created")
            
            # Create page
            self._page = self._context.new_page()
            logger.info("Remote page created successfully")
            
            # Set default timeouts
            self._apply_timeouts()
            
            # Log remote session info
            self._log_remote_session_info()
            
            return self._page
            
        except Exception as e:
            logger.error(f"Failed to create remote driver: {e}")
            self._cleanup()
            raise
    
    def _log_remote_session_info(self) -> None:
        """Log remote session information for debugging and reporting."""
        try:
            if not self.remote or not self._page:
                return
            
            session_info = {
                "execution_mode": "remote",
                "remote_url": self.remote_url,
                "browser_name": self.browser_profile.get('browserName', 'unknown'),
                "browser_version": self.browser_profile.get('browserVersion', 'unknown'),
                "viewport": self.browser_profile.get('viewport'),
                "headless": self.browser_profile.get('headless', False)
            }
            
            logger.info(f"Remote Session Info: {json.dumps(session_info, indent=2)}")
            
            # TODO: Integrate with ReportingManager to attach to Allure report
            from reporting.manager import ReportingManager
            try:
                ReportingManager.log_info(f"Remote Session: {json.dumps(session_info)}")
            except Exception as e:
                logger.debug(f"Could not log to ReportingManager: {e}")
        except Exception as e:
            logger.warning(f"Failed to log remote session info: {e}")
    
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
