"""
Reporting Manager

Central facade for accessing the active reporter instance.
Manages reporter initialization and provides singleton-like access.
"""

from typing import Optional, Literal
from loguru import logger

from reporting.reporter import Reporter
from reporting.allure_reporter import AllureReporter


class ReportingManager:
    """
    Facade for managing test reporting.
    
    Provides a single access point for reporter functionality throughout the framework.
    Supports initialization with different reporter types and safe lazy-loading.
    
    Usage:
        ReportingManager.init("allure")
        ReportingManager.reporter().log_step("Click button")
    """
    
    _instance: Optional[Reporter] = None
    _reporter_type: Optional[str] = None
    
    @classmethod
    def init(cls, reporter_type: str = "allure") -> None:
        """
        Initialize the reporting manager with a specific reporter type.
        
        Should be called once during test session setup (in pytest_configure).
        
        Args:
            reporter_type: Type of reporter to use ("allure", "extent", "report_portal", etc.)
                          Currently only "allure" is implemented.
        
        Raises:
            ValueError: If reporter type is not supported
            ImportError: If reporter dependencies are not installed
            
        Example:
            ReportingManager.init("allure")
        """
        if cls._instance is not None:
            logger.debug(
                f"ReportingManager already initialized with {cls._reporter_type}. "
                "Skipping re-initialization."
            )
            return
        
        cls._reporter_type = reporter_type.lower()
        
        try:
            if cls._reporter_type == "allure":
                cls._instance = AllureReporter()
                logger.info(f"✓ ReportingManager initialized with {reporter_type}")
            else:
                raise ValueError(
                    f"Unsupported reporter type: {reporter_type}. "
                    "Currently supported: allure"
                )
        except ImportError as e:
            logger.error(f"Failed to initialize reporter: {e}")
            raise
    
    @classmethod
    def reporter(cls) -> Reporter:
        """
        Get the active reporter instance.
        
        Returns:
            Reporter instance (AllureReporter, etc.)
            
        Raises:
            RuntimeError: If ReportingManager has not been initialized
            
        Example:
            reporter = ReportingManager.reporter()
            reporter.log_step("Test action")
        """
        if cls._instance is None:
            raise RuntimeError(
                "ReportingManager not initialized. "
                "Call ReportingManager.init() during test session setup."
            )
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """
        Reset the reporting manager.
        
        Useful for testing or switching reporters.
        After reset, must call init() again before accessing reporter().
        """
        cls._instance = None
        cls._reporter_type = None
        logger.debug("ReportingManager reset")
    
    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if reporting manager has been initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return cls._instance is not None
    
    @classmethod
    def log_info(cls, message: str) -> None:
        """
        Log informational message to report.
        
        Safe to call even if reporter not initialized.
        
        Args:
            message: Information message to log
        """
        try:
            if cls.is_initialized():
                cls.reporter().log_step(message)
        except Exception:
            logger.debug(f"Could not log to reporter: {message}")
    
    @classmethod
    def attach_remote_capabilities(cls, capabilities: dict) -> None:
        """
        Attach remote execution capabilities to report.
        
        Args:
            capabilities: Dictionary of remote execution capabilities
        """
        try:
            if cls.is_initialized():
                import json
                cap_text = json.dumps(capabilities, indent=2)
                cls.reporter().attach_text("Remote Capabilities", cap_text)
        except Exception as e:
            logger.debug(f"Could not attach remote capabilities: {e}")
