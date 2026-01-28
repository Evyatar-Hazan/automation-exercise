"""
Core package for the automation framework.
Contains driver management and base test classes.
"""

from core.driver_factory import DriverFactory
from core.base_test import BaseTest

__all__ = ['DriverFactory', 'BaseTest']
