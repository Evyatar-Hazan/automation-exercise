"""
Reporter Interface

Abstract base class defining the contract for any reporting implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path


class Reporter(ABC):
    """
    Abstract base class for test reporting implementations.
    
    Defines the interface that all reporting systems must implement.
    Allows easy switching between Allure, Extent Reports, Report Portal, etc.
    without changing test code.
    """
    
    @abstractmethod
    def log_step(self, message: str) -> None:
        """
        Log a test step.
        
        Args:
            message: Step description
            
        Example:
            reporter.log_step("Click login button")
        """
        pass
    
    @abstractmethod
    def attach_screenshot(self, name: str, path: str) -> None:
        """
        Attach a screenshot to the test report.
        
        Args:
            name: Name/description for the screenshot
            path: File path to the screenshot
            
        Example:
            reporter.attach_screenshot("Login page", "reports/screenshots/login.png")
        """
        pass
    
    @abstractmethod
    def attach_text(self, name: str, content: str) -> None:
        """
        Attach text content to the test report.
        
        Args:
            name: Name/description for the attachment
            content: Text content to attach
            
        Example:
            reporter.attach_text("Error Details", str(exception))
        """
        pass
    
    @abstractmethod
    def attach_exception(self, name: str, exception: Exception) -> None:
        """
        Attach exception details to the test report.
        
        Args:
            name: Name/description for the attachment
            exception: The exception to attach
            
        Example:
            reporter.attach_exception("Failure", test_exception)
        """
        pass
