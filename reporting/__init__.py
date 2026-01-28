"""
Reporting Module

Provides abstraction layer for test reporting, allowing easy extension to different
reporting backends (Allure, Extent Reports, Report Portal, etc.)
"""

from reporting.manager import ReportingManager

__all__ = ["ReportingManager"]
