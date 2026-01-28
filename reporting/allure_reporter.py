"""
Allure Reporter Implementation

Implements Reporter interface using the Allure Python API.
All Allure-specific imports and logic are contained here.
"""

import traceback
from pathlib import Path
from typing import Optional

from reporting.reporter import Reporter


class AllureReporter(Reporter):
    """
    Reporter implementation using Allure reporting framework.
    
    Wraps Allure-specific logic to implement the Reporter interface.
    No Allure imports should appear outside this module.
    """
    
    def __init__(self):
        """Initialize Allure reporter."""
        try:
            import allure
            self.allure = allure
        except ImportError:
            raise ImportError(
                "allure-pytest package not found. "
                "Install with: pip install allure-pytest"
            )
    
    def log_step(self, message: str) -> None:
        """
        Log a test step using Allure step decorator.
        
        Args:
            message: Step description
        """
        with self.allure.step(message):
            pass
    
    def attach_screenshot(self, name: str, path: str) -> None:
        """
        Attach a screenshot to the Allure report.
        
        Args:
            name: Name/description for the screenshot
            path: File path to the screenshot
        """
        try:
            screenshot_path = Path(path)
            if not screenshot_path.exists():
                return
            
            with open(screenshot_path, 'rb') as img:
                self.allure.attach(
                    img.read(),
                    name=name,
                    attachment_type=self.allure.attachment_type.PNG
                )
        except Exception as e:
            # Silently fail if screenshot attachment fails
            # to avoid breaking test execution
            pass
    
    def attach_text(self, name: str, content: str) -> None:
        """
        Attach text content to the Allure report.
        
        Args:
            name: Name/description for the attachment
            content: Text content to attach
        """
        try:
            self.allure.attach(
                content,
                name=name,
                attachment_type=self.allure.attachment_type.TEXT
            )
        except Exception:
            pass
    
    def attach_exception(self, name: str, exception: Exception) -> None:
        """
        Attach exception details to the Allure report.
        
        Args:
            name: Name/description for the attachment
            exception: The exception to attach
        """
        try:
            exc_traceback = traceback.format_exc()
            self.allure.attach(
                exc_traceback,
                name=name,
                attachment_type=self.allure.attachment_type.TEXT
            )
        except Exception:
            pass
